# Phase 3: Multi-Tenant Architecture - Implementation Plan

**Started**: November 19, 2025
**Estimated Completion**: 5-7 days
**Status**: IN PROGRESS 🔄

---

## 🎯 Goals

Transform Smart Maintenance into a true SaaS platform where:
- Multiple organizations (tenants) use the same application
- Each tenant's data is completely isolated
- Each tenant can have custom branding and features
- Subscription plans with usage limits
- Subdomain-based tenant access (acme.smartmaintenance.com)

---

## 🏗️ Architecture Overview

### Multi-Tenancy Approach: Shared Database with tenant_id

**Why?**
- ✅ Simpler to implement and manage
- ✅ Lower infrastructure costs
- ✅ Easier backups and migrations
- ✅ Good for MVP/early stage
- ✅ Can scale to hundreds of tenants

**Trade-offs**:
- ⚠️ Must be careful with queries (always filter by tenant_id)
- ⚠️ Risk of data leakage bugs (mitigated by automated filtering)
- ⚠️ Less isolation than separate databases

**Decision**: Start with shared DB, can migrate to separate schemas later if needed.

---

## 📋 Implementation Phases

### Phase A: Backend Foundation (Days 1-3)

**Goal**: Create tenant infrastructure and modify existing models

#### Day 1: Core Models & Migrations
1. ✅ Create `Tenant` model
2. ✅ Create `TenantSubscription` model
3. ✅ Add `tenant_id` to all 10+ existing models
4. ✅ Database migrations

#### Day 2: Repositories & Services
1. ✅ Create `TenantRepository`
2. ✅ Create `TenantService` with provisioning
3. ✅ Modify `BaseRepository` for automatic tenant filtering
4. ✅ Create tenant middleware

#### Day 3: API & Data Migration
1. ✅ Create tenant controller (8 endpoints)
2. ✅ Migrate existing data to default tenant
3. ✅ Test tenant isolation

### Phase B: Frontend Integration (Days 4-5)

**Goal**: Build tenant management UI and registration flow

#### Day 4: Core UI
1. ✅ Create DTOs
2. ✅ Add ApiService methods
3. ✅ Create TenantRegistration.razor
4. ✅ Create TenantSettings.razor

#### Day 5: Admin UI & Branding
1. ✅ Create Tenants.razor (admin)
2. ✅ Implement dynamic branding
3. ✅ Add X-Tenant-ID to API calls

### Phase C: Testing & Refinement (Days 6-7)

**Goal**: Ensure security and reliability

#### Day 6: Testing
1. ✅ Test tenant data isolation (CRITICAL)
2. ✅ Test plan limit enforcement
3. ✅ Unit tests for TenantService
4. ✅ Integration tests

#### Day 7: Polish & Documentation
1. ✅ Fix any bugs found
2. ✅ Update documentation
3. ✅ Create tenant provisioning guide

---

## 🗄️ Database Schema

### New Tables

```sql
-- Tenants table
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    plan VARCHAR(50) DEFAULT 'free',
    max_users INT DEFAULT 3,
    max_assets INT DEFAULT 10,
    max_requests_per_month INT DEFAULT 50,
    settings JSONB,
    logo_url VARCHAR(500),
    primary_color VARCHAR(7) DEFAULT '#667eea',
    billing_email VARCHAR(255),
    subscription_expires TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tenant subscriptions (for future billing integration)
CREATE TABLE tenant_subscriptions (
    id SERIAL PRIMARY KEY,
    tenant_id INT REFERENCES tenants(id) ON DELETE CASCADE,
    plan VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    billing_cycle VARCHAR(20) DEFAULT 'monthly',
    price DECIMAL(10,2),
    stripe_subscription_id VARCHAR(255),
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Modified Tables (add tenant_id to all)

```sql
ALTER TABLE users ADD COLUMN tenant_id INT REFERENCES tenants(id);
ALTER TABLE assets ADD COLUMN tenant_id INT REFERENCES tenants(id);
ALTER TABLE maintenance_requests ADD COLUMN tenant_id INT REFERENCES tenants(id);
ALTER TABLE feature_flags ADD COLUMN tenant_id INT REFERENCES tenants(id);
ALTER TABLE roles ADD COLUMN tenant_id INT REFERENCES tenants(id);
-- ... and more

-- Create indexes for performance
CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_assets_tenant ON assets(tenant_id);
CREATE INDEX idx_requests_tenant ON maintenance_requests(tenant_id);
```

---

## 🔑 Key Components

### 1. Tenant Model

```python
class Tenant(BaseModel):
    __tablename__ = 'tenants'

    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True, nullable=False)
    status = Column(String(50), default='active')  # active, suspended, trial
    plan = Column(String(50), default='free')  # free, basic, premium, enterprise

    # Plan limits
    max_users = Column(Integer, default=3)
    max_assets = Column(Integer, default=10)
    max_requests_per_month = Column(Integer, default=50)

    # Customization
    settings = Column(JSON)
    logo_url = Column(String(500))
    primary_color = Column(String(7), default='#667eea')

    # Billing
    billing_email = Column(String(255))
    subscription_expires = Column(DateTime)
```

### 2. Tenant Middleware

```python
class TenantMiddleware:
    """Extract tenant from subdomain or header"""

    def __call__(self, environ, start_response):
        # Option 1: Extract from subdomain
        host = environ.get('HTTP_HOST', '')
        subdomain = extract_subdomain(host)
        tenant = get_tenant_by_subdomain(subdomain)

        # Option 2: From header (for API clients)
        if not tenant:
            tenant_id = environ.get('HTTP_X_TENANT_ID')
            if tenant_id:
                tenant = get_tenant_by_id(tenant_id)

        # Store in g
        g.current_tenant = tenant
```

### 3. Auto-Filtering in BaseRepository

```python
class BaseRepository:
    def _apply_tenant_filter(self, query):
        """Automatically filter by current tenant"""
        if hasattr(g, 'current_tenant') and g.current_tenant:
            return query.filter_by(tenant_id=g.current_tenant.id)
        return query

    def get_all(self):
        query = self.model.query
        query = self._apply_tenant_filter(query)
        return query.all()

    def create(self, data):
        """Automatically add tenant_id"""
        if hasattr(g, 'current_tenant') and g.current_tenant:
            data['tenant_id'] = g.current_tenant.id
        instance = self.model(**data)
        # ...
```

---

## 📊 Subscription Plans

```python
SUBSCRIPTION_PLANS = {
    'free': {
        'name': 'Free Trial',
        'price': 0,
        'max_users': 3,
        'max_assets': 10,
        'max_requests_per_month': 50,
        'features': ['basic_dashboard', 'email_notifications'],
        'duration_days': 14
    },
    'basic': {
        'name': 'Basic',
        'price': 29,  # USD per month
        'max_users': 10,
        'max_assets': 100,
        'max_requests_per_month': 500,
        'features': ['basic_dashboard', 'email_notifications', 'mobile_app', 'api_access']
    },
    'premium': {
        'name': 'Premium',
        'price': 99,
        'max_users': 50,
        'max_assets': 1000,
        'max_requests_per_month': None,  # Unlimited
        'features': ['all_features', 'priority_support', 'custom_branding', 'advanced_analytics']
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': None,  # Custom pricing
        'max_users': None,  # Unlimited
        'max_assets': None,  # Unlimited
        'max_requests_per_month': None,  # Unlimited
        'features': ['all_features', 'dedicated_support', 'sla', 'custom_integration']
    }
}
```

---

## 🚀 Subdomain Routing

### How it works:

```
https://acme.smartmaintenance.com     → Acme Corp (tenant_id: 5)
https://beta.smartmaintenance.com     → Beta Company (tenant_id: 12)
https://app.smartmaintenance.com      → Default tenant (legacy)
https://smartmaintenance.com          → Landing page (no tenant)
```

### DNS Configuration Required:

```
*.smartmaintenance.com    A    <server-ip>
```

### CORS Configuration:

```python
CORS(app, origins=[
    'https://*.smartmaintenance.com',
    'https://smartmaintenance.com',
    'http://localhost:5112'  # Development
])
```

---

## ✅ Testing Strategy

### Critical Tests:

1. **Tenant Isolation Test** (MOST IMPORTANT)
   ```python
   # Create 2 tenants with data
   # Ensure Tenant A cannot see Tenant B's data
   # Test all models (users, assets, requests, etc.)
   ```

2. **Plan Limit Tests**
   ```python
   # Test user creation fails when max_users reached
   # Test asset creation fails when max_assets reached
   # Test request creation fails when monthly limit reached
   ```

3. **Subdomain Routing Tests**
   ```python
   # Test middleware extracts correct tenant
   # Test fallback to header
   # Test missing tenant handling
   ```

4. **Data Migration Tests**
   ```python
   # Test existing data moved to default tenant
   # Test no data loss
   # Test referential integrity maintained
   ```

---

## ⚠️ Critical Considerations

### Security:
- **ALWAYS filter by tenant_id** in all queries
- Test for SQL injection in tenant queries
- Test for cross-tenant data leakage
- Validate subdomain format (no special chars)

### Performance:
- Add indexes on all tenant_id columns
- Monitor query performance
- Consider caching tenant lookups

### Data Migration:
- Backup database before migration
- Test migration on copy first
- Have rollback plan ready
- Migrate in steps (add column → populate → make required)

---

## 📚 API Endpoints

### Tenant Management (Super Admin only)
```
GET    /api/v1/tenants               # List all tenants
POST   /api/v1/tenants               # Create tenant
GET    /api/v1/tenants/:id           # Get tenant
PATCH  /api/v1/tenants/:id           # Update tenant
DELETE /api/v1/tenants/:id           # Delete tenant
POST   /api/v1/tenants/:id/suspend   # Suspend tenant
POST   /api/v1/tenants/:id/activate  # Activate tenant
```

### Tenant Self-Service (Tenant Admin)
```
GET    /api/v1/tenant/settings       # Get current tenant settings
PATCH  /api/v1/tenant/settings       # Update branding/features
GET    /api/v1/tenant/usage          # Get usage stats
GET    /api/v1/tenant/billing        # Get billing info
```

### Public Endpoints (No auth)
```
POST   /api/v1/register-tenant       # New tenant signup
GET    /api/v1/check-subdomain       # Check if subdomain available
```

---

## 🎨 Frontend Pages

### Public
- **TenantRegistration.razor** - Signup form (company name, subdomain, admin email)

### Tenant Admin
- **TenantSettings.razor** - Branding (logo, colors), features, company info
- **TenantUsage.razor** - Usage stats, plan limits, upgrade options

### Super Admin
- **Tenants.razor** - List all tenants, filter, search
- **TenantDetails.razor** - View/edit tenant, suspend/activate, view usage

---

## 📖 Next Steps

**After Phase 3 Completion:**
1. Phase 4: Custom Fields System (4-5 days)
   - Allows tenants to add custom fields to assets/requests
   - Industry-specific flexibility

2. Phase 5: Billing Integration (2-3 days)
   - Stripe integration
   - Subscription management
   - Automated plan upgrades/downgrades

3. Phase 6: Advanced Features
   - Two-factor authentication
   - Audit logging per tenant
   - Advanced analytics per tenant

---

**Ready to start implementation!** 🚀

Let's begin with creating the Tenant model.
