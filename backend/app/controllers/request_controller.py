"""
Maintenance Request Controller

Endpoints:
- POST /api/v1/requests - Create request
- GET /api/v1/requests - List requests
- GET /api/v1/requests/:id - Get request
- POST /api/v1/requests/:id/assign - Assign request (admin only)
- POST /api/v1/requests/:id/start - Start work (assigned technician)
- POST /api/v1/requests/:id/complete - Complete work (assigned technician)
- GET /api/v1/requests/unassigned - List unassigned (admin only)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.services import MaintenanceService
from app.repositories import (
    RequestRepository, UserRepository,
    AssetRepository
)
from app.patterns.factory import MaintenanceRequestFactory
from app.services import NotificationService
from app.patterns.strategy import EmailNotificationStrategy
from app.schemas.request_schemas import (
    RequestCreateSchema,
    RequestAssignSchema,
    RequestCompleteSchema
)
from app.middleware.auth import admin_required, technician_required, get_current_user
from app.middleware.permissions import require_permission, require_any_permission

# Create blueprint
request_bp = Blueprint('requests', __name__, url_prefix='/api/v1/requests')

# Initialize repositories
request_repo = RequestRepository()
user_repo = UserRepository()
asset_repo = AssetRepository()

# Initialize services
email_strategy = EmailNotificationStrategy(
    smtp_host='smtp.gmail.com',
    smtp_port=587,
    username='noreply@smartmaintenance.com',
    password='dummy'
)
notification_service = NotificationService(user_repo, email_strategy)
factory = MaintenanceRequestFactory()

maintenance_service = MaintenanceService(
    request_repo, user_repo, asset_repo,
    notification_service, factory
)

# Initialize schemas
request_create_schema = RequestCreateSchema()
request_assign_schema = RequestAssignSchema()
request_complete_schema = RequestCompleteSchema()


@request_bp.route('', methods=['POST'])
@jwt_required()
@require_permission("create_requests")
def create_request():
    """Create maintenance request."""
    try:
        current_user = get_current_user()
        data = request_create_schema.load(request.get_json())

        result = maintenance_service.create_request(
            submitter_id=current_user.id,
            **data
        )

        if not result['success']:
            return jsonify({'success': False, 'error': result['error']}), 400

        return jsonify({'success': True, 'data': result['data'], 'message': result['message']}), 201
    except ValidationError as e:
        return jsonify({'error': {'code': 'VALIDATION_ERROR', 'details': e.messages}}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@request_bp.route('', methods=['GET'])
@jwt_required()
@require_permission("view_requests")
def list_requests():
    """List maintenance requests."""
    try:
        requests = request_repo.get_all()
        return jsonify({'success': True, 'data': [r.to_dict() for r in requests], 'total': len(requests)}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@request_bp.route('/<int:request_id>', methods=['GET'])
@jwt_required()
@require_permission("view_requests")
def get_request(request_id):
    """Get request by ID."""
    try:
        req = request_repo.get_by_id(request_id)

        if not req:
            return jsonify({'success': False, 'error': 'Request not found'}), 404

        return jsonify({'success': True, 'data': req.to_dict()}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@request_bp.route('/<int:request_id>/assign', methods=['POST'])
@admin_required()
@require_permission("assign_requests")
def assign_request(request_id):
    """Assign request to technician (admin only)."""
    try:
        current_user = get_current_user()
        data = request_assign_schema.load(request.get_json())

        result = maintenance_service.assign_request(
            request_id=request_id,
            technician_id=data['technician_id'],
            assigned_by_user_id=current_user.id
        )

        if not result['success']:
            return jsonify({'error': result['error']}), 400

        return jsonify({'data': result['data'], 'message': result['message']}), 200
    except ValidationError as e:
        return jsonify({'error': {'code': 'VALIDATION_ERROR', 'details': e.messages}}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@request_bp.route('/<int:request_id>/start', methods=['POST'])
@technician_required()
@require_permission("start_work")
def start_work(request_id):
    """Start work on request (assigned technician)."""
    try:
        current_user = get_current_user()

        result = maintenance_service.start_work(
            request_id=request_id,
            technician_id=current_user.id
        )

        if not result['success']:
            return jsonify({'error': result['error']}), 400

        return jsonify({'data': result['data'], 'message': result['message']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@request_bp.route('/<int:request_id>/complete', methods=['POST'])
@technician_required()
@require_permission("complete_requests")
def complete_request(request_id):
    """Complete work on request (assigned technician)."""
    try:
        current_user = get_current_user()
        data = request_complete_schema.load(request.get_json())

        result = maintenance_service.complete_request(
            request_id=request_id,
            technician_id=current_user.id,
            completion_notes=data['completion_notes'],
            actual_hours=data.get('actual_hours')
        )

        if not result['success']:
            return jsonify({'error': result['error']}), 400

        return jsonify({'data': result['data'], 'message': result['message']}), 200
    except ValidationError as e:
        return jsonify({'error': {'code': 'VALIDATION_ERROR', 'details': e.messages}}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@request_bp.route('/unassigned', methods=['GET'])
@admin_required()
@require_any_permission("assign_requests", "view_requests")
def unassigned_requests():
    """Get unassigned requests (admin only)."""
    try:
        result = maintenance_service.get_unassigned_requests()

        if not result['success']:
            return jsonify({'error': result['error']}), 500

        return jsonify({'data': result['data'], 'message': result['message']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
