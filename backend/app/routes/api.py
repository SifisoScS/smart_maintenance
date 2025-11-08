"""
Basic API routes for testing.

Full API will be implemented in Phase 4.
"""

from flask import Blueprint, jsonify
from app.repositories import UserRepository, AssetRepository, RequestRepository

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Smart Maintenance Management System is running',
        'version': '1.0.0',
        'phase': 'Phase 1 Complete - Core Domain Models'
    }), 200


@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        user_repo = UserRepository()
        asset_repo = AssetRepository()
        request_repo = RequestRepository()

        stats = {
            'users': {
                'total': user_repo.count(),
                'admins': user_repo.count(role='ADMIN'),
                'technicians': user_repo.count(role='TECHNICIAN'),
                'clients': user_repo.count(role='CLIENT')
            },
            'assets': asset_repo.get_asset_statistics(),
            'requests': request_repo.get_request_statistics()
        }

        return jsonify({
            'success': True,
            'data': stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/', methods=['GET'])
def api_root():
    """API root endpoint"""
    return jsonify({
        'message': 'Smart Maintenance Management System API',
        'version': 'v1',
        'endpoints': {
            'health': '/api/v1/health',
            'stats': '/api/v1/stats'
        },
        'status': 'Phase 1 Complete',
        'next_phase': 'Phase 2 - Business Logic & Service Layer'
    }), 200
