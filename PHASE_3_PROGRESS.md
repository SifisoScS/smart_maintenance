# Phase 3: Multi-Tenant Architecture - Progress Report

**Started**: November 19, 2025
**Status**: IN PROGRESS (Day 1 - Foundation Complete)
**Next Session**: Continue with tenant_id migration

---

## ✅ What's Been Completed

### 1. Tenant Model (`backend/app/models/tenant.py`) ✅

**Features:**
- Complete tenant representation with subscription management
- 4 status types: active, suspended, trial, cancelled
- 4 subscription plans: free, basic, premium, enterprise
- Plan-based limits: max_users, max_assets, max_requests_per_month
- Branding fields: logo_url, primary_color, secondary_color
- Subdomain-based identification (acme.smartmaintenance.com)
- Trial period management with auto-expiration
- Usage statistics calculation (current vs limits)
- Helper methods:
  - `can_add_user()` - Check if user limit reached
  - `can_add_asset()` - Check if asset limit reached
  - `can_create_request()` - Check if monthly request limit reached
  - `has_feature(feature_name)` - Check if plan includes feature
  - `get_usage_stats()` - Get current usage vs limits
  - `is_trial_expired()` - Check trial status
  - `is_subscription_expired()` - Check subscription status

**Key Fields:**
```python
- id, name, subdomain
- status, plan
- max_users, max_assets, max_requests_per_month
- settings (JSON), logo_url, primary_color, secondary_color
- billing_email, subscription_expires, trial_ends
- contact_name, contact_phone
- is_active, onboarded
```

**Subscription Plans Defined:**
```python
FREE:       $0/mo  | 3 users, 10 assets, 50 requests/month | 14-day trial
BASIC:      $29/mo | 10 users, 100 assets, 500 requests/month
PREMIUM:    $99/mo | 50 users, 1000 assets, unlimited requests
ENTERPRISE: Custom | Unlimited everything
```

### 2. TenantSubscription Model (`backend/app/models/tenant_subscription.py`) ✅

**Features:**
- Billing cycle tracking (monthly, annual)
- Stripe integration ready (subscription_id, customer_id, payment_method_id)
- Subscription status: active, past_due, cancelled, paused
- Billing period management with auto-renewal
- Trial period tracking
- Cancellation scheduling (cancel at period end or immediately)
- Helper methods:
  - `is_active()` - Check if subscription is current
  - `is_in_trial()` - Check if in trial period
  - `days_until_renewal()` - Get days until next billing
  - `schedule_cancellation()` - Cancel at period end
  - `cancel_immediately()` - Cancel now
  - `renew()` - Renew for next period

**Key Fields:**
```python
- id, tenant_id
- plan, status, billing_cycle
- price, currency
- stripe_subscription_id, stripe_customer_id, stripe_payment_method_id
- current_period_start, current_period_end
- trial_start, trial_end
- cancel_at, cancelled_at
```

### 3. Models Registered (`backend/app/models/__init__.py`) ✅

Both Tenant and TenantSubscription are properly exported and available for import.

---

## 📋 What's Next - Detailed Implementation Plan

### Phase 1: Database Schema Changes (Critical - Do Carefully!)

#### Step 1: Add tenant_id to ALL Existing Models

**Files to Modify:**

1. **`backend/app/models/user.py`**
```python
# Add after imports
from sqlalchemy import ForeignKey

# Add to User model
tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True, index=True)
tenant = relationship('Tenant', backref='users')
```

2. **`backend/app/models/asset.py`**
```python
# Add to Asset model
tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True, index=True)
tenant = relationship('Tenant', backref='assets')
```

3. **`backend/app/models/request.py`**
```python
# Add to MaintenanceRequest model (base class)
tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True, index=True)
tenant = relationship('Tenant', backref='requests')

# Note: ElectricalRequest, PlumbingRequest, HVACRequest inherit this automatically
```

4. **`backend/app/models/feature_flag.py`**
```python
# Add to FeatureFlag model
tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True, index=True)
tenant = relationship('Tenant', backref='feature_flags')
```

5. **`backend/app/models/role.py`**
```python
# Add to Role model
tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True, index=True)
tenant = relationship('Tenant', backref='roles')
```

6. **`backend/app/models/permission.py`**
```python
# Add to Permission model
tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True, index=True)
tenant = relationship('Tenant', backref='permissions')
```

**IMPORTANT NOTES:**
- Start with `nullable=True` - we'll make it NOT NULL after data migration
- Add indexes for performance (`index=True`)
- Use `backref` to access tenant's data (tenant.users, tenant.assets, etc.)

#### Step 2: Create Database Migrations

**Migration 1: Create tenants tables**
```bash
cd backend
flask db migrate -m "add tenants and tenant_subscriptions tables"
flask db upgrade
```

**Migration 2: Add tenant_id columns**
```bash
flask db migrate -m "add tenant_id to all tables"
flask db upgrade
```

**Migration 3: Create default tenant and migrate data**
```python
# Create migration script: backend/migrations/versions/XXXXX_migrate_to_default_tenant.py

def upgrade():
    # Create default tenant
    op.execute("""
        INSERT INTO tenants (name, subdomain, status, plan, max_users, max_assets, max_requests_per_month)
        VALUES ('Default Organization', 'app', 'active', 'enterprise', NULL, NULL, NULL)
    """)

    # Get default tenant ID
    default_tenant_id = 1

    # Migrate existing data
    op.execute(f"UPDATE users SET tenant_id = {default_tenant_id}")
    op.execute(f"UPDATE assets SET tenant_id = {default_tenant_id}")
    op.execute(f"UPDATE maintenance_requests SET tenant_id = {default_tenant_id}")
    op.execute(f"UPDATE feature_flags SET tenant_id = {default_tenant_id}")
    op.execute(f"UPDATE roles SET tenant_id = {default_tenant_id}")
    op.execute(f"UPDATE permissions SET tenant_id = {default_tenant_id}")

    # Make tenant_id NOT NULL
    op.alter_column('users', 'tenant_id', nullable=False)
    op.alter_column('assets', 'tenant_id', nullable=False)
    op.alter_column('maintenance_requests', 'tenant_id', nullable=False)
    op.alter_column('feature_flags', 'tenant_id', nullable=False)
    op.alter_column('roles', 'tenant_id', nullable=False)
    op.alter_column('permissions', 'tenant_id', nullable=False)

def downgrade():
    # Remove NOT NULL constraint
    op.alter_column('users', 'tenant_id', nullable=True)
    # ... (reverse all changes)

    # Delete default tenant
    op.execute("DELETE FROM tenants WHERE subdomain = 'app'")
```

### Phase 2: Repository & Service Layer

#### Step 1: Create TenantRepository

**File:** `backend/app/repositories/tenant_repository.py`

```python
from app.repositories.base_repository import BaseRepository
from app.models.tenant import Tenant

class TenantRepository(BaseRepository):
    def __init__(self):
        super().__init__(Tenant)

    def get_by_subdomain(self, subdomain):
        """Get tenant by subdomain"""
        return self.model.query.filter_by(subdomain=subdomain).first()

    def check_subdomain_available(self, subdomain):
        """Check if subdomain is available"""
        return self.get_by_subdomain(subdomain) is None

    def get_active_tenants(self):
        """Get all active tenants"""
        return self.model.query.filter_by(is_active=True).all()

    def suspend_tenant(self, tenant_id, reason=None):
        """Suspend a tenant"""
        tenant = self.get_by_id(tenant_id)
        if tenant:
            tenant.status = 'suspended'
            if reason:
                tenant.settings['suspension_reason'] = reason
            self.db.session.commit()
        return tenant

    def activate_tenant(self, tenant_id):
        """Activate a suspended tenant"""
        tenant = self.get_by_id(tenant_id)
        if tenant:
            tenant.status = 'active'
            tenant.is_active = True
            if 'suspension_reason' in tenant.settings:
                del tenant.settings['suspension_reason']
            self.db.session.commit()
        return tenant
```

**Don't forget:** Add to `backend/app/repositories/__init__.py`

#### Step 2: Create TenantService

**File:** `backend/app/services/tenant_service.py`

```python
from app.services.base_service import BaseService
from app.repositories.tenant_repository import TenantRepository
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.permission_repository import PermissionRepository
from app.models.tenant import Tenant, SUBSCRIPTION_PLANS
from flask import g

class TenantService(BaseService):
    def __init__(self):
        super().__init__(TenantRepository())
        self.user_repo = UserRepository()
        self.role_repo = RoleRepository()
        self.permission_repo = PermissionRepository()

    def create_tenant(self, data):
        """
        Create new tenant with provisioning

        Args:
            data (dict): {name, subdomain, billing_email, admin_email, admin_password}

        Returns:
            dict: Created tenant with admin user
        """
        try:
            # Validate subdomain
            if not self.repository.check_subdomain_available(data['subdomain']):
                return {
                    'success': False,
                    'error': 'Subdomain is already taken'
                }

            # Create tenant
            plan = data.get('plan', 'free')
            plan_config = SUBSCRIPTION_PLANS.get(plan, SUBSCRIPTION_PLANS['free'])

            tenant = self.repository.create({
                'name': data['name'],
                'subdomain': data['subdomain'],
                'status': 'trial',
                'plan': plan,
                'max_users': plan_config['max_users'],
                'max_assets': plan_config['max_assets'],
                'max_requests_per_month': plan_config['max_requests_per_month'],
                'billing_email': data.get('billing_email'),
                'contact_name': data.get('contact_name'),
                'contact_phone': data.get('contact_phone')
            })

            # Provision tenant (create admin user, roles, permissions)
            self.provision_tenant(tenant.id, data.get('admin_email'), data.get('admin_password'))

            return {
                'success': True,
                'data': tenant.to_dict(),
                'message': 'Tenant created successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def provision_tenant(self, tenant_id, admin_email, admin_password):
        """
        Provision new tenant with default setup
        - Create admin user
        - Copy default roles and permissions
        - Set up default settings
        """
        # Store tenant in context for auto-filtering
        tenant = self.repository.get_by_id(tenant_id)
        g.current_tenant = tenant

        # Create admin user
        admin_user = self.user_repo.create({
            'email': admin_email,
            'password': admin_password,
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'tenant_id': tenant_id,
            'is_active': True
        })

        # TODO: Copy default roles and permissions for this tenant
        # (Will implement after RBAC is tenant-aware)

        # Mark tenant as onboarded
        tenant.onboarded = True
        self.repository.db.session.commit()

        return admin_user

    def get_tenant_usage(self, tenant_id):
        """Get tenant usage statistics"""
        try:
            tenant = self.repository.get_by_id(tenant_id)
            if not tenant:
                return {'success': False, 'error': 'Tenant not found'}

            return {
                'success': True,
                'data': tenant.get_usage_stats()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def check_limit(self, tenant_id, resource_type):
        """
        Check if tenant can add more resources

        Args:
            tenant_id: Tenant ID
            resource_type: 'user', 'asset', or 'request'

        Returns:
            dict: {can_add: bool, reason: str}
        """
        tenant = self.repository.get_by_id(tenant_id)
        if not tenant:
            return {'can_add': False, 'reason': 'Tenant not found'}

        if resource_type == 'user':
            can_add = tenant.can_add_user()
            reason = None if can_add else f'User limit reached ({tenant.max_users})'
        elif resource_type == 'asset':
            can_add = tenant.can_add_asset()
            reason = None if can_add else f'Asset limit reached ({tenant.max_assets})'
        elif resource_type == 'request':
            can_add = tenant.can_create_request()
            reason = None if can_add else f'Monthly request limit reached ({tenant.max_requests_per_month})'
        else:
            return {'can_add': False, 'reason': 'Invalid resource type'}

        return {'can_add': can_add, 'reason': reason}
```

#### Step 3: Modify BaseRepository for Auto-Filtering

**File:** `backend/app/repositories/base_repository.py`

Add these methods:

```python
from flask import g

def _apply_tenant_filter(self, query):
    """
    Automatically filter query by current tenant

    CRITICAL FOR SECURITY: Ensures tenant data isolation
    """
    # Skip tenant filtering for Tenant model itself
    if self.model.__tablename__ == 'tenants':
        return query

    # Skip if no tenant in context (e.g., during migrations)
    if not hasattr(g, 'current_tenant') or not g.current_tenant:
        return query

    # Apply tenant filter if model has tenant_id
    if hasattr(self.model, 'tenant_id'):
        return query.filter_by(tenant_id=g.current_tenant.id)

    return query

def get_all(self):
    """Get all records (filtered by tenant)"""
    query = self.model.query
    query = self._apply_tenant_filter(query)
    return query.all()

def get_by_id(self, id):
    """Get record by ID (filtered by tenant)"""
    query = self.model.query
    query = self._apply_tenant_filter(query)
    return query.get(id)

# Update all other query methods to use _apply_tenant_filter
```

### Phase 3: Tenant Middleware

**File:** `backend/app/middleware/tenant_middleware.py`

```python
from flask import g, request, jsonify
from app.repositories.tenant_repository import TenantRepository

class TenantMiddleware:
    """
    Extract tenant from subdomain or header
    Store in Flask g for use in repositories
    """

    def __init__(self, app=None):
        self.app = app
        self.tenant_repo = TenantRepository()
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize middleware with Flask app"""
        app.before_request(self.before_request)

    def before_request(self):
        """Extract tenant before each request"""
        tenant = None

        # Method 1: Extract from subdomain (primary method)
        host = request.host
        subdomain = self.extract_subdomain(host)
        if subdomain:
            tenant = self.tenant_repo.get_by_subdomain(subdomain)

        # Method 2: Extract from header (for API clients)
        if not tenant:
            tenant_id = request.headers.get('X-Tenant-ID')
            if tenant_id:
                tenant = self.tenant_repo.get_by_id(int(tenant_id))

        # Method 3: Default tenant for main domain
        if not tenant and host in ['smartmaintenance.com', 'app.smartmaintenance.com', 'localhost:5112']:
            tenant = self.tenant_repo.get_by_subdomain('app')

        # Store in context
        g.current_tenant = tenant

        # Check if tenant is active
        if tenant and not tenant.is_active:
            return jsonify({
                'success': False,
                'error': 'Tenant account is suspended'
            }), 403

    def extract_subdomain(self, host):
        """
        Extract subdomain from host

        Examples:
            acme.smartmaintenance.com -> acme
            beta.smartmaintenance.com -> beta
            smartmaintenance.com -> None
            localhost:5112 -> None
        """
        parts = host.split('.')

        # localhost or IP address
        if 'localhost' in host or ':' in parts[0]:
            return None

        # Main domain (no subdomain)
        if len(parts) <= 2:
            return None

        # Has subdomain
        return parts[0]
```

**Register middleware in `backend/app/__init__.py`:**

```python
from app.middleware.tenant_middleware import TenantMiddleware

def create_app(config_name='development'):
    app = Flask(__name__)
    # ... existing setup ...

    # Initialize tenant middleware
    TenantMiddleware(app)

    return app
```

---

## 📝 Testing Checklist

### Critical Security Tests (MUST DO!)

1. **Tenant Isolation Test**
```python
# Create 2 tenants with data
# Switch to Tenant A
# Try to access Tenant B's data
# Should return 0 results
```

2. **Subdomain Routing Test**
```python
# Request to acme.smartmaintenance.com
# Should set g.current_tenant to Acme
# All queries should filter by Acme's tenant_id
```

3. **Plan Limit Test**
```python
# Create Free plan tenant (max 3 users)
# Try to create 4th user
# Should fail with limit error
```

---

## 🎯 When You Return

### Step-by-Step Resume Plan:

**Session Start Checklist:**
1. Review this document (PHASE_3_PROGRESS.md)
2. Review the Tenant models created
3. Check the todo list status
4. Start with Step 1: Add tenant_id to models

**Recommended Order:**
1. Add tenant_id to all 6 models (User, Asset, Request, FeatureFlag, Role, Permission)
2. Create database migrations (3 migrations)
3. Run migrations and test
4. Create TenantRepository
5. Create TenantService
6. Modify BaseRepository for auto-filtering
7. Create TenantMiddleware
8. Create TenantController with API endpoints
9. Test tenant isolation (CRITICAL)
10. Frontend integration (DTOs, pages, API calls)

**Estimated Time Remaining:** 4-6 days

---

## 📚 Key Files Created So Far

```
backend/app/models/
├── tenant.py (NEW - 300+ lines)
├── tenant_subscription.py (NEW - 180+ lines)
└── __init__.py (MODIFIED - added exports)

Documentation:
├── PHASE_3_PLAN.md (NEW - implementation plan)
├── PHASE_3_PROGRESS.md (THIS FILE - progress tracker)
└── NEXT_PHASES.md (UPDATED - marked Phase 2 complete, Phase 3 in progress)
```

---

## ⚠️ Important Reminders

**Before Making Schema Changes:**
1. ✅ Backup your database
2. ✅ Test migrations on a copy first
3. ✅ Have a rollback plan
4. ✅ Review each model change carefully

**Security Considerations:**
- ALWAYS filter by tenant_id in queries
- Test cross-tenant data access thoroughly
- Validate subdomain format
- Check tenant status before allowing operations

**Performance:**
- Add indexes on all tenant_id columns
- Monitor query performance
- Consider caching tenant lookups

---

## 🚀 Next Session Goals

**Primary Goal:** Add tenant_id to all models and create migrations

**Success Criteria:**
- ✅ All 6 models have tenant_id field
- ✅ 3 database migrations created and tested
- ✅ Existing data migrated to default tenant
- ✅ All tests still passing

---

Good luck with Phase 3! Take your time with the database changes - they're critical for the entire multi-tenant architecture. 🎯
