"""
Permission Controller
REST API endpoints for permission management
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.services.permission_service import PermissionService
from app.middleware.permissions import require_permission

permission_bp = Blueprint('permissions', __name__, url_prefix='/api/v1/permissions')
permission_service = PermissionService()


@permission_bp.route('', methods=['GET'])
@jwt_required()
@require_permission('view_permissions')
def get_all_permissions():
    """
    Get all permissions

    Returns:
        JSON: List of all permissions
    """
    result = permission_service.get_all_permissions()
    return jsonify(result), 200 if result['success'] else 400


@permission_bp.route('/grouped', methods=['GET'])
@jwt_required()
@require_permission('view_permissions')
def get_permissions_grouped():
    """
    Get permissions grouped by resource

    Returns:
        JSON: Permissions grouped by resource
    """
    result = permission_service.get_permissions_grouped()
    return jsonify(result), 200 if result['success'] else 400


@permission_bp.route('/<int:permission_id>', methods=['GET'])
@jwt_required()
@require_permission('view_permissions')
def get_permission(permission_id):
    """
    Get permission by ID

    Args:
        permission_id (int): Permission ID

    Returns:
        JSON: Permission details
    """
    result = permission_service.get_permission_by_id(permission_id)
    return jsonify(result), 200 if result['success'] else 404


@permission_bp.route('', methods=['POST'])
@jwt_required()
@require_permission('manage_permissions')
def create_permission():
    """
    Create new permission

    Request Body:
        {
            "name": "edit_assets",
            "description": "Permission to edit assets",
            "resource": "assets",
            "action": "edit"
        }

    Returns:
        JSON: Created permission
    """
    data = request.get_json()
    result = permission_service.create_permission(data)
    return jsonify(result), 201 if result['success'] else 400


@permission_bp.route('/<int:permission_id>', methods=['PATCH'])
@jwt_required()
@require_permission('manage_permissions')
def update_permission(permission_id):
    """
    Update permission

    Args:
        permission_id (int): Permission ID

    Request Body:
        {
            "description": "Updated description",
            "resource": "assets",
            "action": "edit"
        }

    Returns:
        JSON: Updated permission
    """
    data = request.get_json()
    result = permission_service.update_permission(permission_id, data)
    return jsonify(result), 200 if result['success'] else 404


@permission_bp.route('/<int:permission_id>', methods=['DELETE'])
@jwt_required()
@require_permission('manage_permissions')
def delete_permission(permission_id):
    """
    Delete permission

    Args:
        permission_id (int): Permission ID

    Returns:
        JSON: Success message
    """
    result = permission_service.delete_permission(permission_id)
    return jsonify(result), 200 if result['success'] else 404


@permission_bp.route('/check/<int:user_id>/<permission_name>', methods=['GET'])
@jwt_required()
@require_permission('view_permissions')
def check_user_permission(user_id, permission_name):
    """
    Check if user has specific permission

    Args:
        user_id (int): User ID
        permission_name (str): Permission name

    Returns:
        JSON: Permission check result
    """
    result = permission_service.check_user_permission(user_id, permission_name)
    return jsonify(result), 200 if result['success'] else 404


@permission_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
@require_permission('view_permissions')
def get_user_permissions(user_id):
    """
    Get all permissions for user

    Args:
        user_id (int): User ID

    Returns:
        JSON: List of user permissions
    """
    result = permission_service.get_user_permissions(user_id)
    return jsonify(result), 200 if result['success'] else 404
