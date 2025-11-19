"""
Role Controller
REST API endpoints for role management
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.services.role_service import RoleService
from app.middleware.permissions import require_permission

role_bp = Blueprint('roles', __name__, url_prefix='/api/v1/roles')
role_service = RoleService()


@role_bp.route('', methods=['GET'])
@jwt_required()
@require_permission('view_roles')
def get_all_roles():
    """
    Get all roles

    Query Parameters:
        include_permissions (bool): Include permissions in response
        include_users (bool): Include users in response

    Returns:
        JSON: List of all roles
    """
    include_permissions = request.args.get('include_permissions', 'false').lower() == 'true'
    include_users = request.args.get('include_users', 'false').lower() == 'true'

    result = role_service.get_all_roles(include_permissions, include_users)
    return jsonify(result), 200 if result['success'] else 400


@role_bp.route('/<int:role_id>', methods=['GET'])
@jwt_required()
@require_permission('view_roles')
def get_role(role_id):
    """
    Get role by ID

    Args:
        role_id (int): Role ID

    Query Parameters:
        include_permissions (bool): Include permissions
        include_users (bool): Include users

    Returns:
        JSON: Role details
    """
    include_permissions = request.args.get('include_permissions', 'true').lower() == 'true'
    include_users = request.args.get('include_users', 'false').lower() == 'true'

    result = role_service.get_role_by_id(role_id, include_permissions, include_users)
    return jsonify(result), 200 if result['success'] else 404


@role_bp.route('', methods=['POST'])
@jwt_required()
@require_permission('manage_roles')
def create_role():
    """
    Create new role

    Request Body:
        {
            "name": "Manager",
            "description": "Department manager role",
            "permission_ids": [1, 2, 3, 4]
        }

    Returns:
        JSON: Created role
    """
    data = request.get_json()
    result = role_service.create_role(data)
    return jsonify(result), 201 if result['success'] else 400


@role_bp.route('/<int:role_id>', methods=['PATCH'])
@jwt_required()
@require_permission('manage_roles')
def update_role(role_id):
    """
    Update role

    Args:
        role_id (int): Role ID

    Request Body:
        {
            "name": "Senior Manager",
            "description": "Updated description",
            "permission_ids": [1, 2, 3, 4, 5]
        }

    Returns:
        JSON: Updated role
    """
    data = request.get_json()
    result = role_service.update_role(role_id, data)
    return jsonify(result), 200 if result['success'] else 404


@role_bp.route('/<int:role_id>', methods=['DELETE'])
@jwt_required()
@require_permission('manage_roles')
def delete_role(role_id):
    """
    Delete role (only if not system role)

    Args:
        role_id (int): Role ID

    Returns:
        JSON: Success message
    """
    result = role_service.delete_role(role_id)
    return jsonify(result), 200 if result['success'] else 400


@role_bp.route('/<int:role_id>/permissions', methods=['POST'])
@jwt_required()
@require_permission('manage_roles')
def add_permission_to_role(role_id):
    """
    Add permission to role

    Args:
        role_id (int): Role ID

    Request Body:
        {
            "permission_id": 5
        }

    Returns:
        JSON: Updated role
    """
    data = request.get_json()
    permission_id = data.get('permission_id')

    if not permission_id:
        return jsonify({
            'success': False,
            'error': 'permission_id is required'
        }), 400

    result = role_service.add_permission_to_role(role_id, permission_id)
    return jsonify(result), 200 if result['success'] else 400


@role_bp.route('/<int:role_id>/permissions/<int:permission_id>', methods=['DELETE'])
@jwt_required()
@require_permission('manage_roles')
def remove_permission_from_role(role_id, permission_id):
    """
    Remove permission from role

    Args:
        role_id (int): Role ID
        permission_id (int): Permission ID

    Returns:
        JSON: Updated role
    """
    result = role_service.remove_permission_from_role(role_id, permission_id)
    return jsonify(result), 200 if result['success'] else 400


@role_bp.route('/<int:role_id>/users', methods=['GET'])
@jwt_required()
@require_permission('view_roles')
def get_role_users(role_id):
    """
    Get all users with specific role

    Args:
        role_id (int): Role ID

    Returns:
        JSON: List of users with role
    """
    result = role_service.get_role_users(role_id)
    return jsonify(result), 200 if result['success'] else 404


# User Role Assignment Endpoints

@role_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
@require_permission('view_roles')
def get_user_roles(user_id):
    """
    Get all roles assigned to user

    Args:
        user_id (int): User ID

    Returns:
        JSON: List of user roles
    """
    result = role_service.get_user_roles(user_id)
    return jsonify(result), 200 if result['success'] else 404


@role_bp.route('/user/<int:user_id>/assign', methods=['POST'])
@jwt_required()
@require_permission('assign_roles')
def assign_role_to_user(user_id):
    """
    Assign role to user

    Args:
        user_id (int): User ID

    Request Body:
        {
            "role_id": 3
        }

    Returns:
        JSON: Success message
    """
    data = request.get_json()
    role_id = data.get('role_id')

    if not role_id:
        return jsonify({
            'success': False,
            'error': 'role_id is required'
        }), 400

    result = role_service.assign_role_to_user(user_id, role_id)
    return jsonify(result), 200 if result['success'] else 400


@role_bp.route('/user/<int:user_id>/remove/<int:role_id>', methods=['DELETE'])
@jwt_required()
@require_permission('remove_roles')
def remove_role_from_user(user_id, role_id):
    """
    Remove role from user

    Args:
        user_id (int): User ID
        role_id (int): Role ID

    Returns:
        JSON: Success message
    """
    result = role_service.remove_role_from_user(user_id, role_id)
    return jsonify(result), 200 if result['success'] else 400
