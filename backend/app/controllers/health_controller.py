"""
Health Check Controller

Simple health check endpoint for testing backend connectivity
"""

from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)


@health_bp.route('/api/v1/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    Returns:
        JSON response indicating backend is running
    """
    return jsonify({
        'status': 'healthy',
        'message': 'Smart Maintenance Backend is running!',
        'version': '1.0.0'
    }), 200


@health_bp.route('/', methods=['GET'])
def root():
    """
    Root endpoint.

    Returns:
        JSON response with API information
    """
    return jsonify({
        'success': True,
        'message': 'Smart Maintenance API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/v1/health',
            'auth': '/api/v1/auth',
            'users': '/api/v1/users',
            'requests': '/api/v1/requests',
            'assets': '/api/v1/assets'
        }
    }), 200
