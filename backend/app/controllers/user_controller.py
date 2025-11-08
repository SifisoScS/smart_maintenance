"""
User Management Controller

Endpoints:
- GET /api/v1/users - List users (admin only)
- GET /api/v1/users/:id - Get user (self or admin)
- PUT /api/v1/users/:id - Update user (self or admin)
- POST /api/v1/users/:id/password - Change password (self only)
- GET /api/v1/users/technicians - List available technicians
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.services import UserService
from app.repositories import UserRepository
from app.schemas.user_schemas import UserUpdateSchema, PasswordChangeSchema
from app.middleware.auth import admin_required, get_current_user, check_resource_owner

# Create blueprint
user_bp = Blueprint('users', __name__, url_prefix='/api/v1/users')

# Initialize services
user_repo = UserRepository()
user_service = UserService(user_repo)

# Initialize schemas
user_update_schema = UserUpdateSchema()
password_change_schema = PasswordChangeSchema()


@user_bp.route('', methods=['GET'])
@admin_required()
def list_users():
    """List all users (admin only)."""
    try:
        users = user_repo.get_all()
        return jsonify({
            'data': [u.to_dict() for u in users],
            'total': len(users)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user by ID (self or admin)."""
    try:
        if not check_resource_owner(user_id):
            return jsonify({'error': 'Forbidden'}), 403

        result = user_service.get_user_profile(user_id)

        if not result['success']:
            return jsonify({'error': result['error']}), 404

        return jsonify({'data': result['data']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user profile (self or admin)."""
    try:
        if not check_resource_owner(user_id):
            return jsonify({'error': 'Forbidden'}), 403

        data = user_update_schema.load(request.get_json())
        result = user_service.update_profile(user_id, **data)

        if not result['success']:
            return jsonify({'error': result['error']}), 400

        return jsonify({'data': result['data'], 'message': result['message']}), 200
    except ValidationError as e:
        return jsonify({'error': {'code': 'VALIDATION_ERROR', 'details': e.messages}}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/<int:user_id>/password', methods=['POST'])
@jwt_required()
def change_password(user_id):
    """Change user password (self only)."""
    try:
        current_user = get_current_user()

        if current_user.id != user_id:
            return jsonify({'error': 'Forbidden - can only change own password'}), 403

        data = password_change_schema.load(request.get_json())
        result = user_service.change_password(user_id, data['old_password'], data['new_password'])

        if not result['success']:
            return jsonify({'error': result['error']}), 400

        return jsonify({'message': result['message']}), 200
    except ValidationError as e:
        return jsonify({'error': {'code': 'VALIDATION_ERROR', 'details': e.messages}}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/technicians', methods=['GET'])
@jwt_required()
def list_technicians():
    """List available technicians."""
    try:
        result = user_service.get_available_technicians()

        if not result['success']:
            return jsonify({'error': result['error']}), 500

        return jsonify({'data': result['data'], 'message': result['message']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
