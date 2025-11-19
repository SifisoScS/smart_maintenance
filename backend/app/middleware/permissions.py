"""
Permission Decorators
Middleware for enforcing permission-based access control on endpoints
"""
from functools import wraps
from flask import jsonify, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.repositories.user_repository import UserRepository
from app.repositories.permission_repository import PermissionRepository


def require_permission(permission_name):
    """
    Decorator to require specific permission for endpoint access

    Args:
        permission_name (str): Name of required permission

    Usage:
        @require_permission('view_users')
        def get_users():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Verify JWT token
                verify_jwt_in_request()

                # Get user ID from token
                identity = get_jwt_identity()
                user_id = identity.get('user_id') if isinstance(identity, dict) else identity

                # Get user from database
                user_repo = UserRepository()
                user = user_repo.get_by_id(user_id)

                if not user:
                    return jsonify({
                        'success': False,
                        'error': 'User not found'
                    }), 401

                # Check if user has permission
                if not user.has_permission_by_name(permission_name):
                    return jsonify({
                        'success': False,
                        'error': f"Permission denied. Required permission: '{permission_name}'",
                        'required_permission': permission_name
                    }), 403

                # Store user in g for use in endpoint
                g.current_user = user

                return func(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f"Authorization error: {str(e)}"
                }), 401

        return wrapper
    return decorator


def require_any_permission(*permission_names):
    """
    Decorator to require ANY of the specified permissions

    Args:
        *permission_names: Variable number of permission names

    Usage:
        @require_any_permission('view_requests', 'manage_all_requests')
        def get_requests():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                identity = get_jwt_identity()
                user_id = identity.get('user_id') if isinstance(identity, dict) else identity

                user_repo = UserRepository()
                user = user_repo.get_by_id(user_id)

                if not user:
                    return jsonify({
                        'success': False,
                        'error': 'User not found'
                    }), 401

                # Check if user has ANY of the permissions
                has_permission = any(user.has_permission_by_name(perm) for perm in permission_names)

                if not has_permission:
                    return jsonify({
                        'success': False,
                        'error': f"Permission denied. Required any of: {', '.join(permission_names)}",
                        'required_permissions': list(permission_names)
                    }), 403

                g.current_user = user
                return func(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f"Authorization error: {str(e)}"
                }), 401

        return wrapper
    return decorator


def require_all_permissions(*permission_names):
    """
    Decorator to require ALL of the specified permissions

    Args:
        *permission_names: Variable number of permission names

    Usage:
        @require_all_permissions('create_users', 'assign_roles')
        def create_admin_user():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                identity = get_jwt_identity()
                user_id = identity.get('user_id') if isinstance(identity, dict) else identity

                user_repo = UserRepository()
                user = user_repo.get_by_id(user_id)

                if not user:
                    return jsonify({
                        'success': False,
                        'error': 'User not found'
                    }), 401

                # Check if user has ALL of the permissions
                missing_permissions = [
                    perm for perm in permission_names
                    if not user.has_permission_by_name(perm)
                ]

                if missing_permissions:
                    return jsonify({
                        'success': False,
                        'error': f"Permission denied. Missing permissions: {', '.join(missing_permissions)}",
                        'required_permissions': list(permission_names),
                        'missing_permissions': missing_permissions
                    }), 403

                g.current_user = user
                return func(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f"Authorization error: {str(e)}"
                }), 401

        return wrapper
    return decorator


def require_resource_permission(resource, action):
    """
    Decorator to require permission for specific resource and action

    Args:
        resource (str): Resource name (e.g., 'users', 'assets')
        action (str): Action name (e.g., 'view', 'create', 'edit', 'delete')

    Usage:
        @require_resource_permission('assets', 'create')
        def create_asset():
            pass
    """
    permission_name = f"{action}_{resource}"
    return require_permission(permission_name)


def optional_permission(permission_name):
    """
    Decorator that checks permission but doesn't block access
    Sets g.has_permission flag for use in endpoint logic

    Args:
        permission_name (str): Name of permission to check

    Usage:
        @optional_permission('view_sensitive_data')
        def get_user_data():
            if g.has_permission:
                # Return full data
            else:
                # Return limited data
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            g.has_permission = False
            try:
                verify_jwt_in_request()
                identity = get_jwt_identity()
                user_id = identity.get('user_id') if isinstance(identity, dict) else identity

                user_repo = UserRepository()
                user = user_repo.get_by_id(user_id)

                if user:
                    g.has_permission = user.has_permission_by_name(permission_name)
                    g.current_user = user

            except Exception:
                # Don't block access if JWT verification fails
                pass

            return func(*args, **kwargs)

        return wrapper
    return decorator


def get_current_user_permissions():
    """
    Helper function to get current user's permissions

    Returns:
        set: Set of permission names user has access to
    """
    try:
        if hasattr(g, 'current_user') and g.current_user:
            return g.current_user.get_all_permissions()
        return set()
    except Exception:
        return set()


def check_permission(permission_name):
    """
    Helper function to check if current user has permission

    Args:
        permission_name (str): Permission to check

    Returns:
        bool: True if user has permission, False otherwise
    """
    try:
        if hasattr(g, 'current_user') and g.current_user:
            return g.current_user.has_permission_by_name(permission_name)
        return False
    except Exception:
        return False
