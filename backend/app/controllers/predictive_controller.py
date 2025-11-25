"""
Predictive Maintenance API Controller

Exposes REST API endpoints for predictive maintenance features:
- Asset health analysis
- Failure predictions
- Smart technician assignment
- Maintenance scheduling
- Predictive insights dashboard

Author: Sifiso Shezi (ARISAN SIFISO)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.database import db
from app.services.predictive_maintenance_service import PredictiveMaintenanceService
from app.models.user import User, UserRole

predictive_bp = Blueprint('predictive', __name__, url_prefix='/api/v1/predictive')


def get_current_user() -> User:
    """Get current authenticated user"""
    identity = get_jwt_identity()
    user_id = identity.get('user_id') if isinstance(identity, dict) else identity
    return db.session.query(User).filter(User.id == user_id).first()


# ========== Asset Health Endpoints ==========

@predictive_bp.route('/health/asset/<int:asset_id>', methods=['GET'])
@jwt_required()
def get_asset_health(asset_id: int):
    """
    Get comprehensive health analysis for a specific asset

    Returns:
        - asset_info: Basic asset information
        - health_score: Overall health (0-100)
        - prediction: Failure prediction data
        - maintenance_summary: Historical stats
        - recommendations: Actionable recommendations
    """
    user = get_current_user()

    try:
        service = PredictiveMaintenanceService(db.session)
        health_data = service.get_asset_health(asset_id)

        return jsonify({
            'success': True,
            'data': health_data
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to analyze asset: {str(e)}'
        }), 500


@predictive_bp.route('/health/all', methods=['GET'])
@jwt_required()
def get_all_assets_health():
    """
    Get health analysis for all assets

    Query params:
        - organization_id: Filter by organization (optional)

    Returns:
        List of asset health analyses sorted by risk
    """
    user = get_current_user()

    try:
        # Get organization_id from query params or user's org
        org_id = request.args.get('organization_id', type=int)
        if not org_id and user.role != UserRole.ADMIN:
            org_id = user.tenant_id

        service = PredictiveMaintenanceService(db.session)
        health_data = service.get_all_asset_health(org_id)

        return jsonify({
            'success': True,
            'data': health_data,
            'count': len(health_data)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to analyze assets: {str(e)}'
        }), 500


@predictive_bp.route('/health/critical', methods=['GET'])
@jwt_required()
def get_critical_assets():
    """
    Get assets requiring immediate attention (risk >= 0.6)

    Query params:
        - organization_id: Filter by organization (optional)

    Returns:
        List of high-risk assets
    """
    user = get_current_user()

    try:
        org_id = request.args.get('organization_id', type=int)
        if not org_id and user.role != UserRole.ADMIN:
            org_id = user.tenant_id

        service = PredictiveMaintenanceService(db.session)
        critical_assets = service.get_critical_assets(org_id)

        return jsonify({
            'success': True,
            'data': critical_assets,
            'count': len(critical_assets)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get critical assets: {str(e)}'
        }), 500


@predictive_bp.route('/health/history/<int:asset_id>', methods=['GET'])
@jwt_required()
def get_asset_history_insights(asset_id: int):
    """
    Get historical trends and insights for a specific asset

    Returns:
        Historical analysis with trends and patterns
    """
    user = get_current_user()

    try:
        service = PredictiveMaintenanceService(db.session)
        history_data = service.get_asset_history_insights(asset_id)

        return jsonify({
            'success': True,
            'data': history_data
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get history insights: {str(e)}'
        }), 500


# ========== Maintenance Scheduling Endpoints ==========

@predictive_bp.route('/schedule', methods=['GET'])
@jwt_required()
def get_maintenance_schedule():
    """
    Get recommended maintenance schedule based on predictions

    Query params:
        - organization_id: Filter by organization (optional)
        - days_ahead: Number of days to schedule (default: 30)

    Returns:
        List of scheduled maintenance recommendations
    """
    user = get_current_user()

    try:
        org_id = request.args.get('organization_id', type=int)
        if not org_id and user.role != UserRole.ADMIN:
            org_id = user.tenant_id

        days_ahead = request.args.get('days_ahead', default=30, type=int)

        service = PredictiveMaintenanceService(db.session)
        schedule = service.get_maintenance_schedule(org_id, days_ahead)

        return jsonify({
            'success': True,
            'data': schedule,
            'count': len(schedule),
            'days_ahead': days_ahead
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get maintenance schedule: {str(e)}'
        }), 500


@predictive_bp.route('/schedule/create', methods=['POST'])
@jwt_required()
def create_preventive_maintenance():
    """
    Create a preventive maintenance request based on predictions

    Request body:
        {
            "asset_id": int,
            "auto_assign": bool (optional, default: true)
        }

    Returns:
        Created maintenance request details with assignment
    """
    user = get_current_user()

    # Only admin and technicians can create preventive maintenance
    if user.role not in ['admin', 'technician']:
        return jsonify({
            'success': False,
            'error': 'Insufficient permissions'
        }), 403

    try:
        data = request.get_json()
        asset_id = data.get('asset_id')
        auto_assign = data.get('auto_assign', True)

        if not asset_id:
            return jsonify({
                'success': False,
                'error': 'asset_id is required'
            }), 400

        service = PredictiveMaintenanceService(db.session)
        result = service.create_preventive_maintenance_request(asset_id, auto_assign)

        return jsonify({
            'success': True,
            'data': result
        }), 201

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to create preventive maintenance: {str(e)}'
        }), 500


# ========== Smart Assignment Endpoints ==========

@predictive_bp.route('/assignment/auto/<int:request_id>', methods=['POST'])
@jwt_required()
def auto_assign_request(request_id: int):
    """
    Automatically assign a maintenance request to the best technician

    Returns:
        Assignment details with reasoning
    """
    user = get_current_user()

    # Only admin can auto-assign
    if user.role != UserRole.ADMIN:
        return jsonify({
            'success': False,
            'error': 'Only administrators can auto-assign requests'
        }), 403

    try:
        service = PredictiveMaintenanceService(db.session)
        assignment = service.auto_assign_request(request_id)

        if not assignment:
            return jsonify({
                'success': False,
                'error': 'No suitable technician found'
            }), 404

        return jsonify({
            'success': True,
            'data': assignment
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to auto-assign request: {str(e)}'
        }), 500


@predictive_bp.route('/assignment/workload', methods=['GET'])
@jwt_required()
def get_technician_workload():
    """
    Get current workload distribution across technicians

    Query params:
        - organization_id: Filter by organization (optional)

    Returns:
        List of technician workload data
    """
    user = get_current_user()

    # Only admin can view workload
    if user.role != UserRole.ADMIN:
        return jsonify({
            'success': False,
            'error': 'Only administrators can view workload distribution'
        }), 403

    try:
        org_id = request.args.get('organization_id', type=int)
        if not org_id:
            org_id = user.tenant_id

        service = PredictiveMaintenanceService(db.session)
        workload = service.get_technician_workload(org_id)

        return jsonify({
            'success': True,
            'data': workload
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get workload: {str(e)}'
        }), 500


@predictive_bp.route('/assignment/recommendations', methods=['GET'])
@jwt_required()
def get_reassignment_recommendations():
    """
    Get recommendations for load balancing through reassignment

    Query params:
        - organization_id: Filter by organization (optional)

    Returns:
        List of recommended reassignments
    """
    user = get_current_user()

    # Only admin can view recommendations
    if user.role != UserRole.ADMIN:
        return jsonify({
            'success': False,
            'error': 'Only administrators can view reassignment recommendations'
        }), 403

    try:
        org_id = request.args.get('organization_id', type=int)
        if not org_id:
            org_id = user.tenant_id

        service = PredictiveMaintenanceService(db.session)
        recommendations = service.get_reassignment_recommendations(org_id)

        return jsonify({
            'success': True,
            'data': recommendations,
            'count': len(recommendations)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get recommendations: {str(e)}'
        }), 500


# ========== Dashboard & Insights Endpoints ==========

@predictive_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_predictive_dashboard():
    """
    Get comprehensive predictive maintenance dashboard data

    Query params:
        - organization_id: Filter by organization (optional)

    Returns:
        Complete dashboard with health overview, workload, and maintenance schedule
    """
    user = get_current_user()

    try:
        org_id = request.args.get('organization_id', type=int)
        if not org_id and user.role != UserRole.ADMIN:
            org_id = user.tenant_id

        service = PredictiveMaintenanceService(db.session)
        dashboard = service.get_dashboard_summary(org_id)

        return jsonify({
            'success': True,
            'data': dashboard
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get dashboard: {str(e)}'
        }), 500


@predictive_bp.route('/insights', methods=['GET'])
@jwt_required()
def get_predictive_insights():
    """
    Get comprehensive predictive insights for decision making

    Query params:
        - organization_id: Filter by organization (optional)

    Returns:
        Detailed insights with trends, recommendations, alerts, and analytics
    """
    user = get_current_user()

    try:
        org_id = request.args.get('organization_id', type=int)
        if not org_id and user.role != UserRole.ADMIN:
            org_id = user.tenant_id

        service = PredictiveMaintenanceService(db.session)
        insights = service.get_predictive_insights(org_id)

        return jsonify({
            'success': True,
            'data': insights
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get insights: {str(e)}'
        }), 500


# ========== Health Check Endpoint ==========

@predictive_bp.route('/status', methods=['GET'])
@jwt_required()
def get_system_status():
    """
    Get predictive system status

    Returns:
        System status and capabilities
    """
    return jsonify({
        'success': True,
        'data': {
            'status': 'operational',
            'version': '1.0.0',
            'strategy': 'RuleBasedStrategy',
            'features': {
                'asset_health_monitoring': True,
                'failure_prediction': True,
                'smart_assignment': True,
                'maintenance_scheduling': True,
                'predictive_insights': True,
                'ml_ready': True
            },
            'cost': 'Zero - Rule-based algorithms',
            'future_ready': 'ML integration available'
        }
    }), 200


# ========== Error Handlers ==========

@predictive_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@predictive_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
