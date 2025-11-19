"""
Feature Flag Controller

API endpoints for managing feature flags.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.feature_flag_service import FeatureFlagService
from app.repositories.feature_flag_repository import FeatureFlagRepository
from app.middleware.auth import admin_required
from app.middleware.feature_flags import get_enabled_features_for_user
from app.middleware.permissions import require_permission
from app.models.feature_flag import FeatureCategory

# Create blueprint
feature_flag_bp = Blueprint('feature_flags', __name__, url_prefix='/api/v1/features')

# Initialize service
feature_flag_service = FeatureFlagService()


@feature_flag_bp.route('', methods=['GET'])
@jwt_required()
@require_permission("view_feature_flags")
def list_feature_flags():
    """
    Get all feature flags.

    Returns list of all feature flags in the system.
    """
    try:
        result = feature_flag_service.get_all_flags()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@feature_flag_bp.route('/enabled', methods=['GET'])
@jwt_required()
@require_permission("view_feature_flags")
def list_enabled_flags():
    """
    Get all enabled feature flags.

    Returns only flags that are currently enabled.
    """
    try:
        result = feature_flag_service.get_enabled_flags()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@feature_flag_bp.route('/my-features', methods=['GET'])
@jwt_required()
def get_my_features():
    """
    Get feature flags enabled for the current user.

    Takes into account rollout percentages for gradual feature releases.
    Useful for frontend to know which features to show/hide.
    """
    try:
        identity = get_jwt_identity()
        user_id = identity.get('user_id') if isinstance(identity, dict) else identity

        features = get_enabled_features_for_user(user_id)

        return jsonify({
            'success': True,
            'user_id': user_id,
            'features': features
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@feature_flag_bp.route('/<feature_key>', methods=['GET'])
@jwt_required()
@require_permission("view_feature_flags")
def get_feature_flag(feature_key):
    """
    Get specific feature flag by key.

    Args:
        feature_key: Feature key (e.g., 'advanced_reporting')
    """
    try:
        result = feature_flag_service.get_flag_by_key(feature_key)

        if not result['success']:
            return jsonify(result), 404

        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@feature_flag_bp.route('/<feature_key>/check', methods=['GET'])
@jwt_required()
def check_feature_enabled(feature_key):
    """
    Check if a feature is enabled for the current user.

    Args:
        feature_key: Feature key to check

    Returns:
        JSON with enabled status
    """
    try:
        identity = get_jwt_identity()
        user_id = identity.get('user_id') if isinstance(identity, dict) else identity

        is_enabled = feature_flag_service.is_enabled(feature_key, user_id)

        return jsonify({
            'success': True,
            'feature_key': feature_key,
            'enabled': is_enabled,
            'user_id': user_id
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@feature_flag_bp.route('', methods=['POST'])
@admin_required()
@require_permission("manage_feature_flags")
def create_feature_flag():
    """
    Create a new feature flag (admin only).

    Request body:
        {
            "feature_key": "new_feature",
            "name": "New Feature",
            "description": "Description of the feature",
            "category": "experimental",
            "enabled": false,
            "rollout_percentage": 100
        }
    """
    try:
        data = request.get_json()

        # Convert category string to enum
        category_str = data.get('category', 'experimental')
        category = FeatureCategory(category_str)

        result = feature_flag_service.create_flag(
            feature_key=data['feature_key'],
            name=data['name'],
            description=data.get('description'),
            category=category,
            enabled=data.get('enabled', False),
            rollout_percentage=data.get('rollout_percentage', 100),
            config_data=data.get('config_data', {})
        )

        if not result['success']:
            return jsonify(result), 400

        return jsonify(result), 201
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid category: {str(e)}'
        }), 400
    except KeyError as e:
        return jsonify({
            'success': False,
            'error': f'Missing required field: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@feature_flag_bp.route('/<int:flag_id>', methods=['PATCH'])
@admin_required()
@require_permission("manage_feature_flags")
def update_feature_flag(flag_id):
    """
    Update a feature flag (admin only).

    Args:
        flag_id: Feature flag ID

    Request body can include:
        {
            "name": "Updated Name",
            "description": "Updated description",
            "enabled": true,
            "rollout_percentage": 50
        }
    """
    try:
        data = request.get_json()

        # Convert category if provided
        if 'category' in data:
            data['category'] = FeatureCategory(data['category'])

        result = feature_flag_service.update_flag(flag_id, **data)

        if not result['success']:
            return jsonify(result), 404

        return jsonify(result), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid value: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@feature_flag_bp.route('/<int:flag_id>/toggle', methods=['POST'])
@admin_required()
@require_permission("toggle_feature_flags")
def toggle_feature_flag(flag_id):
    """
    Toggle a feature flag on/off (admin only).

    Args:
        flag_id: Feature flag ID
    """
    try:
        result = feature_flag_service.toggle_flag(flag_id)

        if not result['success']:
            return jsonify(result), 404

        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@feature_flag_bp.route('/<int:flag_id>', methods=['DELETE'])
@admin_required()
@require_permission("manage_feature_flags")
def delete_feature_flag(flag_id):
    """
    Delete a feature flag (admin only).

    Args:
        flag_id: Feature flag ID
    """
    try:
        result = feature_flag_service.delete_flag(flag_id)

        if not result['success']:
            return jsonify(result), 404

        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@feature_flag_bp.route('/category/<category>', methods=['GET'])
@jwt_required()
@require_permission("view_feature_flags")
def get_flags_by_category(category):
    """
    Get feature flags by category.

    Args:
        category: Category name (analytics, notifications, etc.)
    """
    try:
        category_enum = FeatureCategory(category)
        result = feature_flag_service.get_flags_by_category(category_enum)

        return jsonify(result), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid category: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
