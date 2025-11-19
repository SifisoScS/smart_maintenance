"""
Asset Management Controller

Endpoints:
- POST /api/v1/assets - Create asset (admin only)
- GET /api/v1/assets - List assets
- GET /api/v1/assets/:id - Get asset
- PUT /api/v1/assets/:id - Update asset (admin only)
- PATCH /api/v1/assets/:id/condition - Update condition (technician/admin)
- GET /api/v1/assets/maintenance - Assets needing maintenance
- GET /api/v1/assets/statistics - Asset statistics
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.services import AssetService
from app.repositories import AssetRepository
from app.schemas.asset_schemas import AssetCreateSchema, AssetUpdateSchema, AssetConditionUpdateSchema
from app.middleware.auth import admin_required, technician_required
from app.middleware.permissions import require_permission, require_any_permission
from app.models.asset import AssetCategory, AssetStatus, AssetCondition

# Create blueprint
asset_bp = Blueprint('assets', __name__, url_prefix='/api/v1/assets')

# Initialize services
asset_repo = AssetRepository()
asset_service = AssetService(asset_repo)

# Initialize schemas
asset_create_schema = AssetCreateSchema()
asset_update_schema = AssetUpdateSchema()
asset_condition_schema = AssetConditionUpdateSchema()


@asset_bp.route('', methods=['POST'])
@admin_required()
@require_permission("create_assets")
def create_asset():
    """Create new asset (admin only)."""
    try:
        data = asset_create_schema.load(request.get_json())

        # Convert string enum values to actual enums
        if 'category' in data and data['category']:
            data['category'] = AssetCategory(data['category'])

        # Set defaults if not provided
        if 'status' not in data or not data['status']:
            data['status'] = AssetStatus.ACTIVE
        else:
            data['status'] = AssetStatus(data['status'])

        if 'condition' not in data or not data['condition']:
            data['condition'] = AssetCondition.GOOD
        else:
            data['condition'] = AssetCondition(data['condition'])

        asset = asset_repo.create_asset(**data)
        return jsonify({'data': asset.to_dict(), 'message': 'Asset created successfully'}), 201
    except ValidationError as e:
        return jsonify({'error': {'code': 'VALIDATION_ERROR', 'details': e.messages}}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@asset_bp.route('', methods=['GET'])
@jwt_required()
@require_permission("view_assets")
def list_assets():
    """List all assets."""
    try:
        assets = asset_repo.get_all()
        return jsonify({'success': True, 'data': [a.to_dict() for a in assets], 'total': len(assets)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@asset_bp.route('/<int:asset_id>', methods=['GET'])
@jwt_required()
@require_permission("view_assets")
def get_asset(asset_id):
    """Get asset by ID."""
    try:
        asset = asset_repo.get_by_id(asset_id)

        if not asset:
            return jsonify({'error': 'Asset not found'}), 404

        return jsonify({'data': asset.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@asset_bp.route('/<int:asset_id>/condition', methods=['PATCH'])
@technician_required()
@require_permission("update_asset_condition")
def update_condition(asset_id):
    """Update asset condition (technician/admin)."""
    try:
        data = asset_condition_schema.load(request.get_json())
        result = asset_service.update_asset_condition(asset_id, data['condition'])

        if not result['success']:
            return jsonify({'error': result['error']}), 400

        return jsonify({'data': result['data'], 'message': result['message']}), 200
    except ValidationError as e:
        return jsonify({'error': {'code': 'VALIDATION_ERROR', 'details': e.messages}}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@asset_bp.route('/maintenance', methods=['GET'])
@jwt_required()
@require_any_permission("view_assets", "view_asset_history")
def assets_needing_maintenance():
    """Get assets needing maintenance."""
    try:
        result = asset_service.get_assets_needing_maintenance()

        if not result['success']:
            return jsonify({'error': result['error']}), 500

        return jsonify({'data': result['data'], 'message': result['message']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@asset_bp.route('/statistics', methods=['GET'])
@jwt_required()
@require_permission("view_assets")
def asset_statistics():
    """Get asset statistics."""
    try:
        result = asset_service.get_asset_statistics()

        if not result['success']:
            return jsonify({'error': result['error']}), 500

        return jsonify({'data': result['data']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
