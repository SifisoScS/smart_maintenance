"""
Tenant Middleware
Extracts tenant context from subdomain and sets it in Flask g
"""

from flask import g, request, jsonify
from app.repositories.tenant_repository import TenantRepository
from app.models.tenant import TenantStatus


class TenantMiddleware:
    """
    Middleware to extract and validate tenant context from requests.

    Tenant Identification Methods:
    1. Subdomain (primary): acme.smartmaintenance.com -> subdomain='acme'
    2. X-Tenant-ID header (fallback): For API clients without subdomain
    3. Default tenant (localhost/development): Uses 'app' subdomain

    Sets Flask g.current_tenant_id for use by BaseRepository.
    """

    def __init__(self, app=None):
        """
        Initialize middleware.

        Args:
            app: Flask application instance
        """
        self.app = app
        self.tenant_repo = TenantRepository()

        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        Register middleware with Flask app.

        Args:
            app: Flask application instance
        """
        app.before_request(self.load_tenant)

    def extract_subdomain(self):
        """
        Extract subdomain from request.

        Returns:
            Subdomain string or None
        """
        # Get host from request
        host = request.host.split(':')[0]  # Remove port if present

        # Development/localhost handling
        if host in ['localhost', '127.0.0.1', '0.0.0.0']:
            return 'app'  # Default tenant for local development

        # Production subdomain extraction
        # Expected format: subdomain.smartmaintenance.com
        parts = host.split('.')

        # If host has subdomain (e.g., acme.smartmaintenance.com)
        if len(parts) >= 3:
            return parts[0]  # Return first part as subdomain

        # If host is just domain (e.g., smartmaintenance.com)
        # Use 'app' as default tenant
        return 'app'

    def load_tenant(self):
        """
        Load tenant context before each request.

        Sets g.current_tenant_id and g.current_tenant for use throughout request.

        Returns:
            None or error response if tenant invalid
        """
        # Skip tenant loading for public endpoints
        public_endpoints = [
            '/api/v1/auth/register',
            '/api/v1/auth/login',
            '/api/v1/tenants/register',  # Tenant registration
            '/health',
            '/api/docs'
        ]

        if request.path in public_endpoints or request.path.startswith('/static'):
            g.current_tenant_id = None
            g.current_tenant = None
            return None

        # Method 1: Check X-Tenant-ID header (for API clients)
        tenant_id_header = request.headers.get('X-Tenant-ID')
        if tenant_id_header:
            try:
                tenant_id = int(tenant_id_header)
                tenant = self.tenant_repo.get_by_id(tenant_id)

                if tenant:
                    return self._set_tenant_context(tenant)
                else:
                    return jsonify({
                        'error': 'Invalid tenant',
                        'message': f'Tenant with ID {tenant_id} not found'
                    }), 404

            except ValueError:
                return jsonify({
                    'error': 'Invalid tenant ID',
                    'message': 'X-Tenant-ID must be a number'
                }), 400

        # Method 2: Extract subdomain (primary method)
        subdomain = self.extract_subdomain()

        if not subdomain:
            return jsonify({
                'error': 'Tenant required',
                'message': 'No tenant subdomain found in request'
            }), 400

        # Look up tenant by subdomain
        tenant = self.tenant_repo.get_by_subdomain(subdomain)

        if not tenant:
            return jsonify({
                'error': 'Tenant not found',
                'message': f'No tenant found for subdomain: {subdomain}'
            }), 404

        return self._set_tenant_context(tenant)

    def _set_tenant_context(self, tenant):
        """
        Set tenant context in Flask g.

        Args:
            tenant: Tenant instance

        Returns:
            None or error response if tenant is suspended/cancelled
        """
        # Check tenant status
        if tenant.status == TenantStatus.SUSPENDED:
            return jsonify({
                'error': 'Tenant suspended',
                'message': 'This account has been suspended. Please contact support.',
                'tenant': tenant.subdomain
            }), 403

        if tenant.status == TenantStatus.CANCELLED:
            return jsonify({
                'error': 'Tenant cancelled',
                'message': 'This account has been cancelled.',
                'tenant': tenant.subdomain
            }), 410  # 410 Gone

        if not tenant.is_active:
            return jsonify({
                'error': 'Tenant inactive',
                'message': 'This account is not active.',
                'tenant': tenant.subdomain
            }), 403

        # Check trial expiration
        if tenant.status == TenantStatus.TRIAL and tenant.is_trial_expired():
            return jsonify({
                'error': 'Trial expired',
                'message': 'Your trial period has expired. Please upgrade to continue.',
                'tenant': tenant.subdomain,
                'trial_ended': tenant.trial_ends.isoformat() if tenant.trial_ends else None
            }), 402  # 402 Payment Required

        # Set tenant context
        g.current_tenant_id = tenant.id
        g.current_tenant = tenant

        # Store tenant info for logging/analytics
        g.tenant_subdomain = tenant.subdomain
        g.tenant_name = tenant.name
        g.tenant_plan = tenant.plan

        return None  # Continue processing request


def create_tenant_middleware(app):
    """
    Factory function to create and register tenant middleware.

    Args:
        app: Flask application instance

    Returns:
        TenantMiddleware instance
    """
    return TenantMiddleware(app)
