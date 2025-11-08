"""
Authentication Controller

Endpoints:
- POST /api/v1/auth/login - User login
- POST /api/v1/auth/logout - User logout
- POST /api/v1/auth/refresh - Refresh access token
- GET /api/v1/auth/me - Get current user
- POST /api/v1/auth/register - User registration

Demonstrates:
- JWT token generation
- Authentication flow
- Input validation with Marshmallow
- Error handling
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from marshmallow import ValidationError
from app.services import UserService
from app.repositories import UserRepository
from app.schemas.auth_schemas import LoginSchema, RegisterSchema
from app.middleware.auth import get_current_user

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

# Initialize services
user_repo = UserRepository()
user_service = UserService(user_repo)

# Initialize schemas
login_schema = LoginSchema()
register_schema = RegisterSchema()

# Token blacklist (in production, use Redis or database)
token_blacklist = set()


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.

    Request Body:
        {
            "email": "user@example.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe",
            "role": "client",
            "phone": "+1-555-0100",
            "department": "IT"
        }

    Returns:
        201: User created successfully
        400: Validation error
        500: Server error
    """
    try:
        # Validate input
        data = register_schema.load(request.get_json())

        # Register user via service
        result = user_service.register_user(**data)

        if not result['success']:
            return jsonify({'error': result['error']}), 400

        # Remove sensitive data from response
        user_data = result['data']
        if 'password_hash' in user_data:
            del user_data['password_hash']

        return jsonify({
            'message': result['message'],
            'data': user_data
        }), 201

    except ValidationError as e:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input',
                'details': e.messages
            }
        }), 400
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e)
            }
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT tokens.

    Request Body:
        {
            "email": "user@example.com",
            "password": "password123"
        }

    Returns:
        200: Login successful with tokens
        400: Validation error
        401: Invalid credentials
        500: Server error
    """
    try:
        # Validate input
        data = login_schema.load(request.get_json())

        # Authenticate via service
        result = user_service.authenticate(
            email=data['email'],
            password=data['password']
        )

        if not result['success']:
            return jsonify({
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': result['error']
                }
            }), 401

        user_data = result['data']

        # Generate JWT tokens (identity must be string)
        access_token = create_access_token(
            identity=str(user_data['id']),
            additional_claims={
                'email': user_data['email'],
                'role': user_data['role']
            }
        )

        refresh_token = create_refresh_token(
            identity=str(user_data['id'])
        )

        # Remove sensitive data
        if 'password_hash' in user_data:
            del user_data['password_hash']

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user_data
        }), 200

    except ValidationError as e:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input',
                'details': e.messages
            }
        }), 400
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e)
            }
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token.

    Headers:
        Authorization: Bearer <refresh_token>

    Returns:
        200: New access token
        401: Invalid or expired refresh token
    """
    try:
        # Get user identity from refresh token (convert string to int)
        user_id = int(get_jwt_identity())

        # Get user data for additional claims
        user = user_repo.get_by_id(user_id)

        if not user:
            return jsonify({
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'User not found'
                }
            }), 401

        # Generate new access token (identity must be string)
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'email': user.email,
                'role': user.role.value
            }
        )

        return jsonify({
            'access_token': access_token
        }), 200

    except Exception as e:
        return jsonify({
            'error': {
                'code': 'UNAUTHORIZED',
                'message': str(e)
            }
        }), 401


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user (blacklist token).

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        200: Logout successful
        401: Invalid token

    Note: In production, use Redis or database for token blacklist
    """
    try:
        jti = get_jwt()['jti']  # JWT ID
        token_blacklist.add(jti)

        return jsonify({
            'message': 'Logout successful'
        }), 200

    except Exception as e:
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e)
            }
        }), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """
    Get current authenticated user.

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        200: User data
        401: Invalid or missing token
    """
    try:
        user = get_current_user()

        if not user:
            return jsonify({
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'User not found'
                }
            }), 401

        user_data = user.to_dict()

        # Remove sensitive data
        if 'password_hash' in user_data:
            del user_data['password_hash']

        return jsonify({
            'data': user_data
        }), 200

    except Exception as e:
        return jsonify({
            'error': {
                'code': 'UNAUTHORIZED',
                'message': str(e)
            }
        }), 401


# JWT token blacklist checker
@auth_bp.before_app_request
def check_if_token_revoked():
    """
    Check if token is in blacklist.

    Note: This runs before every request.
    In production, use Redis for better performance.
    """
    try:
        jwt_data = get_jwt()
        jti = jwt_data.get('jti')

        if jti and jti in token_blacklist:
            return jsonify({
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Token has been revoked'
                }
            }), 401
    except:
        pass  # No JWT in request, that's fine
