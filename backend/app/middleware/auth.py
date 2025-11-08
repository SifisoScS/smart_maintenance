"""
Authentication and Authorization Middleware

Provides:
- JWT token validation decorators
- Role-based access control (RBAC) decorators
- Permission checking

OOP Principles:
- Single Responsibility: Each decorator handles one permission level
- Open/Closed: Easy to add new permission decorators
- Dependency Inversion: Uses Flask-JWT-Extended abstractions
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt_identity,
    get_jwt
)
from app.repositories import UserRepository
from app.models import UserRole


def authenticated_required():
    """
    Decorator to require any authenticated user.

    Usage:
        @app.route('/protected')
        @authenticated_required()
        def protected_route():
            return {'message': 'Authenticated'}
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'error': {
                        'code': 'UNAUTHORIZED',
                        'message': 'Authentication required',
                        'details': str(e)
                    }
                }), 401
        return wrapper
    return decorator


def admin_required():
    """
    Decorator to require admin role.

    Business Rule: Only users with 'admin' role can access.

    Usage:
        @app.route('/admin-only')
        @admin_required()
        def admin_only_route():
            return {'message': 'Admin access'}
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()

                # Get user from JWT (convert string to int)
                user_id = int(get_jwt_identity())
                user_repo = UserRepository()
                user = user_repo.get_by_id(user_id)

                if not user:
                    return jsonify({
                        'error': {
                            'code': 'UNAUTHORIZED',
                            'message': 'User not found'
                        }
                    }), 401

                if not user.is_active:
                    return jsonify({
                        'error': {
                            'code': 'FORBIDDEN',
                            'message': 'User account is not active'
                        }
                    }), 403

                # Check if user is admin
                if user.role != UserRole.ADMIN:
                    return jsonify({
                        'error': {
                            'code': 'FORBIDDEN',
                            'message': 'Administrator privileges required'
                        }
                    }), 403

                return fn(*args, **kwargs)

            except Exception as e:
                return jsonify({
                    'error': {
                        'code': 'UNAUTHORIZED',
                        'message': 'Authentication required',
                        'details': str(e)
                    }
                }), 401
        return wrapper
    return decorator


def technician_required():
    """
    Decorator to require technician or admin role.

    Business Rule: Users with 'technician' or 'admin' role can access.

    Usage:
        @app.route('/technician-only')
        @technician_required()
        def technician_only_route():
            return {'message': 'Technician access'}
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()

                # Get user from JWT (convert string to int)
                user_id = int(get_jwt_identity())
                user_repo = UserRepository()
                user = user_repo.get_by_id(user_id)

                if not user:
                    return jsonify({
                        'error': {
                            'code': 'UNAUTHORIZED',
                            'message': 'User not found'
                        }
                    }), 401

                if not user.is_active:
                    return jsonify({
                        'error': {
                            'code': 'FORBIDDEN',
                            'message': 'User account is not active'
                        }
                    }), 403

                # Check if user is technician or admin
                if user.role not in [UserRole.TECHNICIAN, UserRole.ADMIN]:
                    return jsonify({
                        'error': {
                            'code': 'FORBIDDEN',
                            'message': 'Technician or administrator privileges required'
                        }
                    }), 403

                return fn(*args, **kwargs)

            except Exception as e:
                return jsonify({
                    'error': {
                        'code': 'UNAUTHORIZED',
                        'message': 'Authentication required',
                        'details': str(e)
                    }
                }), 401
        return wrapper
    return decorator


def get_current_user():
    """
    Helper function to get the current authenticated user.

    Returns:
        User: Current user object or None

    Usage:
        @app.route('/me')
        @authenticated_required()
        def get_me():
            user = get_current_user()
            return user.to_dict()
    """
    try:
        user_id = int(get_jwt_identity())
        user_repo = UserRepository()
        return user_repo.get_by_id(user_id)
    except:
        return None


def check_resource_owner(resource_user_id: int) -> bool:
    """
    Check if current user is the owner of a resource or is an admin.

    Args:
        resource_user_id: User ID who owns the resource

    Returns:
        bool: True if current user is owner or admin

    Usage:
        if not check_resource_owner(request.submitter_id):
            return {'error': 'Forbidden'}, 403
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return False

        # Admins can access everything
        if current_user.role == UserRole.ADMIN:
            return True

        # Check if user is the owner
        return current_user.id == resource_user_id

    except:
        return False
