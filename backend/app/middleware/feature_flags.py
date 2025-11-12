"""
Feature Flag Middleware and Decorators

Provides decorators for protecting routes with feature flags.
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.repositories.feature_flag_repository import FeatureFlagRepository


def feature_required(feature_key: str, check_user: bool = True):
    """
    Decorator to protect routes with feature flags.

    Args:
        feature_key: Feature key to check
        check_user: Whether to check user-specific rollout (requires JWT)

    Returns:
        Decorated function

    Example:
        @app.route('/api/v1/advanced-analytics')
        @jwt_required()
        @feature_required('advanced_reporting')
        def advanced_analytics():
            return jsonify({'data': 'analytics'})
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            repository = FeatureFlagRepository()

            # Get user_id if checking user-specific rollout
            user_id = None
            if check_user:
                try:
                    identity = get_jwt_identity()
                    user_id = identity.get('user_id') if isinstance(identity, dict) else identity
                except:
                    pass  # No JWT context, check global flag only

            # Check if feature is enabled
            if not repository.is_enabled(feature_key, user_id):
                return jsonify({
                    'success': False,
                    'error': f"Feature '{feature_key}' is not enabled",
                    'feature_key': feature_key,
                    'enabled': False
                }), 403

            # Feature is enabled, proceed with route handler
            return func(*args, **kwargs)

        return wrapper
    return decorator


def get_enabled_features_for_user(user_id: int = None) -> dict:
    """
    Get all enabled features for a specific user.

    Useful for frontend to know which features to show/hide.

    Args:
        user_id: Optional user ID

    Returns:
        Dict mapping feature keys to enabled status

    Example:
        >>> features = get_enabled_features_for_user(user_id=5)
        >>> {
        >>>     'advanced_reporting': True,
        >>>     'sms_notifications': False,
        >>>     'mobile_access': True
        >>> }
    """
    repository = FeatureFlagRepository()
    all_flags = repository.get_all()

    return {
        flag.feature_key: flag.is_enabled_for_user(user_id)
        for flag in all_flags
    }
