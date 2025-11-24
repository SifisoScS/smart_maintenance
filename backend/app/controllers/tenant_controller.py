"""
Tenant Controller
API endpoints for tenant management
"""

from flask import Blueprint, request, jsonify, g
from app.services.tenant_service import TenantService
from app.decorators.auth_decorators import require_auth, require_permission

# Create blueprint
tenant_bp = Blueprint('tenant', __name__, url_prefix='/api/v1/tenants')

# Initialize service
tenant_service = TenantService()


@tenant_bp.route('/register', methods=['POST'])
def register_tenant():
    """
    Register a new tenant (public endpoint).

    POST /api/v1/tenants/register
    Body: {
        "name": "Acme Corp",
        "subdomain": "acme",
        "admin_email": "admin@acme.com",
        "admin_password": "password123",
        "admin_first_name": "John",
        "admin_last_name": "Doe",
        "plan": "free",
        "billing_email": "billing@acme.com",
        "contact_name": "John Doe",
        "contact_phone": "+1234567890"
    }

    Returns:
        201: Tenant created with trial
        400: Validation error
        409: Subdomain already taken
    """
    try:
        data = request.get_json()

        # Required fields
        required_fields = [
            'name', 'subdomain', 'admin_email', 'admin_password',
            'admin_first_name', 'admin_last_name'
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': 'Missing field',
                    'message': f'Field "{field}" is required'
                }), 400

        # Provision tenant
        result = tenant_service.provision_tenant(
            name=data['name'],
            subdomain=data['subdomain'].lower(),
            admin_email=data['admin_email'],
            admin_password=data['admin_password'],
            admin_first_name=data['admin_first_name'],
            admin_last_name=data['admin_last_name'],
            plan=data.get('plan', 'free'),
            billing_email=data.get('billing_email'),
            contact_name=data.get('contact_name'),
            contact_phone=data.get('contact_phone')
        )

        return jsonify(result), 201

    except ValueError as e:
        return jsonify({'error': 'Validation error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Server error', 'message': str(e)}), 500


@tenant_bp.route('/current', methods=['GET'])
@require_auth()
def get_current_tenant():
    """
    Get current tenant information.

    GET /api/v1/tenants/current

    Returns:
        200: Tenant info with usage statistics
        401: Unauthorized
    """
    try:
        tenant = g.current_tenant

        if not tenant:
            return jsonify({'error': 'No tenant context'}), 400

        # Get usage statistics
        stats = tenant.get_usage_stats()

        # Build response
        response = tenant.to_dict()
        response['usage'] = stats

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': 'Server error', 'message': str(e)}), 500


@tenant_bp.route('/current', methods=['PUT'])
@require_auth()
@require_permission('manage_tenant')
def update_current_tenant():
    """
    Update current tenant settings.

    PUT /api/v1/tenants/current
    Body: {
        "name": "New Name",
        "billing_email": "new@email.com",
        "contact_name": "Jane Doe",
        "contact_phone": "+1234567890"
    }

    Returns:
        200: Tenant updated
        401: Unauthorized
        403: Forbidden (no permission)
    """
    try:
        tenant = g.current_tenant
        if not tenant:
            return jsonify({'error': 'No tenant context'}), 400

        data = request.get_json()

        # Updateable fields
        updateable_fields = ['name', 'billing_email', 'contact_name', 'contact_phone']

        # Apply updates
        for field in updateable_fields:
            if field in data:
                setattr(tenant, field, data[field])

        from app.database import db
        db.session.commit()

        return jsonify(tenant.to_dict()), 200

    except Exception as e:
        from app.database import db
        db.session.rollback()
        return jsonify({'error': 'Server error', 'message': str(e)}), 500


@tenant_bp.route('/current/branding', methods=['PUT'])
@require_auth()
@require_permission('manage_tenant')
def update_branding():
    """
    Update tenant branding.

    PUT /api/v1/tenants/current/branding
    Body: {
        "logo_url": "https://cdn.example.com/logo.png",
        "primary_color": "#667eea",
        "secondary_color": "#764ba2"
    }

    Returns:
        200: Branding updated
        401: Unauthorized
        403: Forbidden
    """
    try:
        tenant = g.current_tenant
        if not tenant:
            return jsonify({'error': 'No tenant context'}), 400

        data = request.get_json()

        result = tenant_service.update_branding(
            tenant_id=tenant.id,
            logo_url=data.get('logo_url'),
            primary_color=data.get('primary_color'),
            secondary_color=data.get('secondary_color')
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': 'Server error', 'message': str(e)}), 500


@tenant_bp.route('/current/subscription', methods=['GET'])
@require_auth()
@require_permission('view_billing')
def get_subscription():
    """
    Get current tenant subscription details.

    GET /api/v1/tenants/current/subscription

    Returns:
        200: Subscription info
        401: Unauthorized
        403: Forbidden
    """
    try:
        tenant = g.current_tenant
        if not tenant:
            return jsonify({'error': 'No tenant context'}), 400

        from app.models.tenant_subscription import TenantSubscription
        subscription = TenantSubscription.query.filter_by(
            tenant_id=tenant.id
        ).order_by(TenantSubscription.created_at.desc()).first()

        if not subscription:
            return jsonify({
                'message': 'No subscription found',
                'tenant_plan': tenant.plan,
                'tenant_status': tenant.status
            }), 404

        return jsonify(subscription.to_dict()), 200

    except Exception as e:
        return jsonify({'error': 'Server error', 'message': str(e)}), 500


@tenant_bp.route('/current/subscription/upgrade', methods=['POST'])
@require_auth()
@require_permission('manage_subscription')
def upgrade_subscription():
    """
    Upgrade tenant subscription to a new plan.

    POST /api/v1/tenants/current/subscription/upgrade
    Body: {
        "plan": "premium",
        "billing_cycle": "monthly",
        "stripe_subscription_id": "sub_xxx"
    }

    Returns:
        200: Subscription upgraded
        400: Invalid plan
        401: Unauthorized
        403: Forbidden
    """
    try:
        tenant = g.current_tenant
        if not tenant:
            return jsonify({'error': 'No tenant context'}), 400

        data = request.get_json()

        if 'plan' not in data:
            return jsonify({'error': 'Missing field', 'message': 'Plan is required'}), 400

        result = tenant_service.upgrade_subscription(
            tenant_id=tenant.id,
            new_plan=data['plan'],
            billing_cycle=data.get('billing_cycle', 'monthly'),
            stripe_subscription_id=data.get('stripe_subscription_id')
        )

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': 'Validation error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Server error', 'message': str(e)}), 500


@tenant_bp.route('/current/limits', methods=['GET'])
@require_auth()
def get_plan_limits():
    """
    Get current tenant plan limits and usage.

    GET /api/v1/tenants/current/limits

    Returns:
        200: Limits and usage data
        401: Unauthorized
    """
    try:
        tenant = g.current_tenant
        if not tenant:
            return jsonify({'error': 'No tenant context'}), 400

        stats = tenant.get_usage_stats()

        response = {
            'plan': tenant.plan,
            'limits': {
                'users': tenant.max_users,
                'assets': tenant.max_assets,
                'requests_per_month': tenant.max_requests_per_month
            },
            'usage': stats,
            'unlimited': {
                'users': tenant.max_users is None,
                'assets': tenant.max_assets is None,
                'requests': tenant.max_requests_per_month is None
            }
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': 'Server error', 'message': str(e)}), 500


@tenant_bp.route('/current/limits/check', methods=['POST'])
@require_auth()
def check_plan_limit():
    """
    Check if tenant can add more of a resource.

    POST /api/v1/tenants/current/limits/check
    Body: {
        "resource": "users",  // or "assets" or "requests"
        "count": 1  // optional, default 1
    }

    Returns:
        200: Limit check result with allowed boolean
        400: Invalid resource
        401: Unauthorized
    """
    try:
        tenant = g.current_tenant
        if not tenant:
            return jsonify({'error': 'No tenant context'}), 400

        data = request.get_json()

        if 'resource' not in data:
            return jsonify({'error': 'Missing field', 'message': 'Resource is required'}), 400

        result = tenant_service.check_plan_limits(
            tenant_id=tenant.id,
            resource=data['resource'],
            count=data.get('count', 1)
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': 'Server error', 'message': str(e)}), 500


# Admin-only endpoints (super admin across all tenants)

@tenant_bp.route('/', methods=['GET'])
@require_auth()
@require_permission('view_all_tenants')
def list_all_tenants():
    """
    List all tenants (super admin only).

    GET /api/v1/tenants?status=active&plan=premium&limit=50

    Query params:
        status: Filter by status
        plan: Filter by plan
        limit: Max results
        search: Search query

    Returns:
        200: List of tenants
        401: Unauthorized
        403: Forbidden (no permission)
    """
    try:
        status = request.args.get('status')
        plan = request.args.get('plan')
        limit = request.args.get('limit', type=int)
        search = request.args.get('search')

        if search:
            tenants = tenant_service.search_tenants(search, limit or 20)
        else:
            tenants = tenant_service.list_tenants(status=status, plan=plan, limit=limit)

        return jsonify({
            'total': len(tenants),
            'tenants': [t.to_dict() for t in tenants]
        }), 200

    except Exception as e:
        return jsonify({'error': 'Server error', 'message': str(e)}), 500


@tenant_bp.route('/<int:tenant_id>', methods=['GET'])
@require_auth()
@require_permission('view_all_tenants')
def get_tenant_by_id(tenant_id):
    """
    Get specific tenant by ID (super admin only).

    GET /api/v1/tenants/{tenant_id}

    Returns:
        200: Tenant data
        404: Tenant not found
        401: Unauthorized
        403: Forbidden
    """
    try:
        tenant = tenant_service.get_tenant_by_id(tenant_id)

        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404

        stats = tenant.get_usage_stats()
        response = tenant.to_dict()
        response['usage'] = stats

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': 'Server error', 'message': str(e)}), 500


@tenant_bp.route('/<int:tenant_id>/suspend', methods=['POST'])
@require_auth()
@require_permission('manage_all_tenants')
def suspend_tenant(tenant_id):
    """
    Suspend a tenant (super admin only).

    POST /api/v1/tenants/{tenant_id}/suspend
    Body: {
        "reason": "Payment overdue"
    }

    Returns:
        200: Tenant suspended
        404: Tenant not found
        401: Unauthorized
        403: Forbidden
    """
    try:
        data = request.get_json() or {}
        reason = data.get('reason')

        result = tenant_service.suspend_tenant(tenant_id, reason)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': 'Not found', 'message': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Server error', 'message': str(e)}), 500


@tenant_bp.route('/<int:tenant_id>/activate', methods=['POST'])
@require_auth()
@require_permission('manage_all_tenants')
def activate_tenant(tenant_id):
    """
    Activate a suspended tenant (super admin only).

    POST /api/v1/tenants/{tenant_id}/activate

    Returns:
        200: Tenant activated
        404: Tenant not found
        401: Unauthorized
        403: Forbidden
    """
    try:
        result = tenant_service.activate_tenant(tenant_id)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': 'Not found', 'message': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Server error', 'message': str(e)}), 500


# Register blueprint
def register_tenant_routes(app):
    """Register tenant blueprint with Flask app"""
    app.register_blueprint(tenant_bp)
