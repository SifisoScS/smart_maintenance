# Smart Maintenance - SaaS Enhancement Roadmap

**Last Updated**: November 12, 2025
**Current Status**: Phase 1 (Feature Flags) - COMPLETED ✅

---

## 📍 Where We Are Now

### ✅ COMPLETED: Phase 1 - Feature Flags System (Nov 11-12, 2025)

**What was built**:
- Complete backend feature flags infrastructure
  - Database model with gradual rollout (0-100%)
  - Repository, Service, Controller layers
  - 10 REST API endpoints
  - `@feature_required` decorator
  - 26 feature flags across 8 categories

- Full frontend integration (Blazor)
  - Beautiful admin UI with real-time toggles
  - Category filtering
  - Summary dashboard
  - Admin-only access control

**Files Created/Modified**:
```
backend/
├── app/models/feature_flag.py (NEW)
├── app/repositories/feature_flag_repository.py (NEW)
├── app/services/feature_flag_service.py (NEW)
├── app/controllers/feature_flag_controller.py (NEW)
├── app/middleware/feature_flags.py (NEW)
└── migrations/versions/[hash]_add_feature_flags_table.py (NEW)

frontend/
├── Models/FeatureFlagModel.cs (NEW)
├── Pages/FeatureFlags.razor (NEW)
├── Services/ApiService.cs (MODIFIED - added 10 endpoints)
└── Layout/NavMenu.razor (MODIFIED - added menu item)
```

**Access**:
- Frontend: `http://localhost:5112/features`
- Login as admin: `admin@smartmaintenance.com`

---

## 🎯 Next Phases - Priority Order

### Phase 2: Enhanced Role-Based Access Control (RBAC) ⚡

**Priority**: HIGH | **Effort**: Medium (2-3 days) | **Value**: High

#### Why This Next?
- Quick win with immediate security benefits
- Foundation for multi-tenancy
- Natural evolution from feature flags
- Minimal disruption to existing code

#### What to Build

**Backend Components**:

1. **New Models**:
```python
# backend/app/models/permission.py
class Permission(BaseModel):
    name: str  # "view_requests", "edit_assets"
    description: str
    resource: str  # "requests", "assets", "users"
    action: str  # "view", "create", "edit", "delete"

# backend/app/models/role.py
class Role(BaseModel):
    name: str  # "Super Admin", "Manager", "Field Tech"
    description: str
    is_system: bool  # True for built-in roles
    permissions: List[Permission]  # Many-to-many

# Modify existing User model
class User(BaseModel):
    # Add: roles = relationship("Role", secondary="user_roles")
```

2. **Database Tables**:
```sql
permissions (
  id, name, description, resource, action, created_at
)

roles (
  id, name, description, is_system, created_at
)

role_permissions (
  role_id, permission_id
)

user_roles (
  user_id, role_id, assigned_at, assigned_by
)
```

3. **Permission Decorators**:
```python
# backend/app/middleware/permissions.py

@require_permission("edit_assets")
def update_asset(asset_id):
    pass

@require_any_permission("view_requests", "manage_all_requests")
def get_requests():
    pass

@require_all_permissions("create_users", "assign_roles")
def create_admin_user():
    pass
```

4. **Services**:
```python
# backend/app/services/permission_service.py
- check_user_permission(user_id, permission_name)
- get_user_permissions(user_id)
- get_permissions_by_role(role_id)

# backend/app/services/role_service.py
- create_role(name, description, permission_ids)
- update_role(role_id, updates)
- assign_role_to_user(user_id, role_id)
- remove_role_from_user(user_id, role_id)
```

5. **API Endpoints**:
```
GET    /api/v1/permissions          # List all permissions
GET    /api/v1/permissions/:id      # Get permission details

GET    /api/v1/roles                # List all roles
POST   /api/v1/roles                # Create custom role (admin only)
GET    /api/v1/roles/:id            # Get role with permissions
PATCH  /api/v1/roles/:id            # Update role
DELETE /api/v1/roles/:id            # Delete role (non-system only)
POST   /api/v1/roles/:id/permissions # Add permission to role

GET    /api/v1/users/:id/roles      # Get user's roles
POST   /api/v1/users/:id/roles      # Assign role to user
DELETE /api/v1/users/:id/roles/:rid # Remove role from user
GET    /api/v1/users/:id/permissions # Get effective permissions
```

**Frontend Components**:

1. **New Pages**:
```
Pages/Roles.razor              # List all roles
Pages/RoleDetails.razor        # Edit role + permission matrix
Pages/Permissions.razor        # List all permissions
Pages/Users.razor              # Modified to show/assign roles
```

2. **Permission Matrix UI**:
```
+-----------------+-------+--------+--------+--------+
| Resource        | View  | Create | Edit   | Delete |
+-----------------+-------+--------+--------+--------+
| Requests        |  ✓    |   ✓    |   ✓    |   □    |
| Assets          |  ✓    |   □    |   □    |   □    |
| Users           |  ✓    |   □    |   □    |   □    |
| Analytics       |  ✓    |   ✓    |   ✓    |   ✓    |
| Feature Flags   |  ✓    |   □    |   □    |   □    |
+-----------------+-------+--------+--------+--------+
```

**Default Permissions to Seed**:
```
Requests:
- view_requests, create_requests, edit_requests, delete_requests
- assign_requests, start_work, complete_requests

Assets:
- view_assets, create_assets, edit_assets, delete_assets
- update_asset_condition, view_asset_history

Users:
- view_users, create_users, edit_users, delete_users
- assign_roles, remove_roles

Analytics:
- view_dashboard, view_reports, export_data

Feature Flags:
- view_feature_flags, toggle_feature_flags, manage_feature_flags

System:
- manage_roles, manage_permissions, view_audit_logs
```

**Default Roles to Seed**:
```
1. Super Admin (all permissions)
2. Admin (all except manage_roles, manage_permissions)
3. Manager (view all, edit requests/assets, view analytics)
4. Technician (view requests, start_work, complete_requests, update_asset_condition)
5. Client (create_requests, view_own_requests)
```

#### Task Checklist

**Backend**:
- [ ] Create Permission model and repository
- [ ] Create Role model and repository
- [ ] Modify User model to support roles (many-to-many)
- [ ] Create permission_service.py
- [ ] Create role_service.py
- [ ] Create permission decorators (`@require_permission`)
- [ ] Update existing endpoints with permission decorators
- [ ] Create role/permission API endpoints
- [ ] Database migrations
- [ ] Seed default permissions and roles
- [ ] Unit tests for permission checking
- [ ] Integration tests for role assignment

**Frontend**:
- [ ] Create RoleModel.cs and PermissionModel.cs DTOs
- [ ] Add methods to ApiService.cs (10+ endpoints)
- [ ] Create Roles.razor page
- [ ] Create RoleDetails.razor with permission matrix
- [ ] Create Permissions.razor page
- [ ] Update Users.razor to show/assign roles
- [ ] Add role management to nav menu (admin only)
- [ ] Test role assignment flow
- [ ] Test permission enforcement

**Testing**:
- [ ] Test permission decorator blocks unauthorized access
- [ ] Test role assignment/removal
- [ ] Test effective permissions calculation
- [ ] Test UI hides features based on permissions

**Estimated Time**: 2-3 days

---

### Phase 3: Multi-Tenant Architecture 🏗️

**Priority**: HIGH | **Effort**: High (5-7 days) | **Value**: Very High

#### Why This?
- Transforms product into true SaaS
- Enables unlimited customer scaling
- Data isolation and security
- Per-tenant customization

#### Architecture Decision: Shared Database with tenant_id

**Pros**:
- Simpler to implement and manage
- Lower infrastructure costs
- Easier backups and migrations
- Good for MVP/early stage

**Cons**:
- More complex queries (always filter by tenant_id)
- Risk of data leakage bugs
- Less isolation than separate DBs

**Decision**: Start with shared DB, can migrate to separate schemas later if needed.

#### What to Build

**Backend Components**:

1. **New Models**:
```python
# backend/app/models/tenant.py
class Tenant(BaseModel):
    name: str                   # "Acme Corp"
    subdomain: str              # "acme" (acme.smartmaintenance.com)
    status: TenantStatus        # active, suspended, trial
    plan: SubscriptionPlan      # free, basic, premium, enterprise
    max_users: int              # Plan limit
    max_assets: int             # Plan limit
    settings: dict              # JSON: { logo, colors, features }
    billing_email: str
    subscription_expires: datetime
    created_at: datetime

class TenantSubscription(BaseModel):
    tenant_id: int
    plan: str
    status: str                 # active, cancelled, past_due
    billing_cycle: str          # monthly, annual
    price: decimal
    stripe_subscription_id: str  # For future billing integration
```

2. **Modify ALL Existing Models**:
```python
# Add to User, Asset, MaintenanceRequest, FeatureFlag, etc.
tenant_id: int = Column(Integer, ForeignKey('tenants.id'), nullable=False, index=True)
tenant = relationship("Tenant")
```

3. **Tenant Middleware**:
```python
# backend/app/middleware/tenant_middleware.py

class TenantMiddleware:
    """Extract tenant from subdomain or header"""

    def __call__(self, request):
        # Option 1: Subdomain
        subdomain = extract_subdomain(request.host)
        tenant = get_tenant_by_subdomain(subdomain)

        # Option 2: Header (for API clients)
        tenant_id = request.headers.get('X-Tenant-ID')

        # Store in request context
        g.current_tenant = tenant
```

4. **Automatic Tenant Filtering**:
```python
# backend/app/repositories/base_repository.py

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
```

5. **Tenant Services**:
```python
# backend/app/services/tenant_service.py

class TenantService:
    def create_tenant(self, data):
        """Create tenant + default admin user"""

    def provision_tenant(self, tenant_id):
        """Set up default roles, permissions, sample data"""

    def suspend_tenant(self, tenant_id, reason):
        """Suspend for non-payment or violations"""

    def check_limits(self, tenant_id, resource):
        """Check if tenant exceeded plan limits"""
```

6. **API Endpoints**:
```
# Tenant Management (super admin only)
GET    /api/v1/tenants               # List all tenants
POST   /api/v1/tenants               # Create new tenant
GET    /api/v1/tenants/:id           # Get tenant details
PATCH  /api/v1/tenants/:id           # Update tenant
DELETE /api/v1/tenants/:id           # Delete tenant

# Tenant Settings (tenant admin)
GET    /api/v1/tenant/settings       # Get current tenant settings
PATCH  /api/v1/tenant/settings       # Update branding, features
GET    /api/v1/tenant/usage          # Get usage stats vs limits
GET    /api/v1/tenant/billing        # Get billing info

# Public Registration
POST   /api/v1/register-tenant       # New tenant signup (no auth)
```

**Frontend Components**:

1. **Subdomain Routing**:
```
https://acme.smartmaintenance.com     → Acme Corp tenant
https://beta.smartmaintenance.com     → Beta Company tenant
https://smartmaintenance.com          → Landing/marketing site
https://app.smartmaintenance.com      → Main app (legacy/fallback)
```

2. **New Pages**:
```
Pages/TenantRegistration.razor    # Public signup
Pages/TenantSettings.razor        # Branding, features
Pages/TenantBilling.razor         # Subscription management
Pages/TenantUsage.razor           # Usage vs plan limits

# Super Admin Pages
Pages/Admin/Tenants.razor         # Manage all tenants
Pages/Admin/TenantDetails.razor   # View/edit tenant
```

3. **Tenant Branding**:
```csharp
// Dynamically load tenant colors, logo
public class TenantBrandingService
{
    public async Task<TenantBranding> GetBrandingAsync()
    {
        var settings = await ApiService.GetTenantSettingsAsync();
        return new TenantBranding
        {
            Logo = settings.LogoUrl,
            PrimaryColor = settings.PrimaryColor,
            CompanyName = settings.Name
        };
    }
}
```

**Database Migration Strategy**:

1. **Add tenant_id to all tables**:
```sql
-- Migration 1: Create tenants table
CREATE TABLE tenants (...);

-- Migration 2: Add tenant_id columns (nullable first)
ALTER TABLE users ADD COLUMN tenant_id INT;
ALTER TABLE assets ADD COLUMN tenant_id INT;
-- ... for all tables

-- Migration 3: Create default tenant for existing data
INSERT INTO tenants (name, subdomain) VALUES ('Default', 'app');
UPDATE users SET tenant_id = 1;
UPDATE assets SET tenant_id = 1;
-- ...

-- Migration 4: Make tenant_id NOT NULL
ALTER TABLE users ALTER COLUMN tenant_id SET NOT NULL;
-- Add foreign keys and indexes
CREATE INDEX idx_users_tenant ON users(tenant_id);
```

**Subscription Plans**:
```python
PLANS = {
    'free': {
        'price': 0,
        'max_users': 3,
        'max_assets': 10,
        'max_requests_per_month': 50,
        'features': ['basic_dashboard', 'email_notifications']
    },
    'basic': {
        'price': 29,  # per month
        'max_users': 10,
        'max_assets': 100,
        'max_requests_per_month': 500,
        'features': ['advanced_reporting', 'api_access']
    },
    'premium': {
        'price': 99,
        'max_users': 50,
        'max_assets': 1000,
        'max_requests_per_month': 'unlimited',
        'features': ['all_features', 'priority_support']
    },
    'enterprise': {
        'price': 'custom',
        'max_users': 'unlimited',
        'max_assets': 'unlimited',
        'features': ['all_features', 'dedicated_support', 'sla']
    }
}
```

#### Task Checklist

**Backend**:
- [ ] Create Tenant model and repository
- [ ] Create TenantSubscription model
- [ ] Add tenant_id to ALL existing models
- [ ] Create tenant middleware
- [ ] Modify base repository for automatic filtering
- [ ] Create tenant_service.py
- [ ] Create tenant provisioning logic
- [ ] Create tenant API endpoints
- [ ] Implement subdomain routing
- [ ] Database migrations (careful!)
- [ ] Seed default tenant for existing data
- [ ] Test data isolation (critical!)
- [ ] Add plan limit checks

**Frontend**:
- [ ] Create TenantModel.cs DTOs
- [ ] Add tenant endpoints to ApiService
- [ ] Create TenantRegistration.razor (public)
- [ ] Create TenantSettings.razor
- [ ] Create TenantBilling.razor
- [ ] Implement dynamic branding
- [ ] Add tenant context to all API calls
- [ ] Test subdomain routing
- [ ] Test multi-tenant isolation

**Infrastructure**:
- [ ] Configure wildcard DNS (*.smartmaintenance.com)
- [ ] Update CORS for subdomains
- [ ] Test subdomain SSL certificates

**Testing**:
- [ ] Test tenant isolation (user A can't see user B's data)
- [ ] Test plan limits enforcement
- [ ] Test tenant provisioning
- [ ] Load test with multiple tenants

**Estimated Time**: 5-7 days

---

### Phase 4: Custom Fields System 🎨

**Priority**: MEDIUM-HIGH | **Effort**: Medium-High (4-5 days) | **Value**: Very High

#### Why This?
- Major product differentiator
- Extreme flexibility for different industries
- No code changes for new requirements
- High customer value

#### What to Build

**Backend Components**:

1. **Models**:
```python
# backend/app/models/custom_field.py

class FieldType(enum.Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    DATE = "date"
    DATETIME = "datetime"
    DROPDOWN = "dropdown"
    MULTI_SELECT = "multi_select"
    CHECKBOX = "checkbox"
    FILE = "file"
    URL = "url"

class CustomFieldDefinition(BaseModel):
    tenant_id: int
    entity_type: str  # "asset", "request", "user"
    field_name: str   # "warranty_expiry", "building_floor"
    field_type: FieldType
    label: str        # Display name
    description: str
    options: dict     # For dropdown: {"options": ["A", "B", "C"]}
    validation_rules: dict  # {"required": true, "min": 0, "max": 100}
    is_required: bool
    display_order: int
    is_active: bool

class CustomFieldValue(BaseModel):
    tenant_id: int
    entity_type: str
    entity_id: int    # ID of asset/request/user
    field_definition_id: int
    # Store values in type-specific columns for indexing
    value_text: str
    value_number: float
    value_date: datetime
    value_json: dict  # For complex types (multi-select, file metadata)
```

2. **Services**:
```python
# backend/app/services/custom_field_service.py

class CustomFieldService:
    def create_field_definition(self, tenant_id, data):
        """Create new custom field"""

    def get_fields_for_entity(self, tenant_id, entity_type):
        """Get all custom fields for entity type"""

    def set_field_value(self, tenant_id, entity_type, entity_id, field_id, value):
        """Set value with validation"""

    def get_entity_custom_data(self, tenant_id, entity_type, entity_id):
        """Get all custom field values for entity"""

    def validate_value(self, field_definition, value):
        """Validate value against field rules"""
```

3. **API Endpoints**:
```
# Field Definitions (Admin)
GET    /api/v1/custom-fields/:entity_type   # Get fields for entity
POST   /api/v1/custom-fields                # Create field definition
PATCH  /api/v1/custom-fields/:id            # Update field definition
DELETE /api/v1/custom-fields/:id            # Delete field definition

# Field Values
GET    /api/v1/:entity_type/:id/custom-data       # Get custom data
POST   /api/v1/:entity_type/:id/custom-data       # Set custom data
PATCH  /api/v1/:entity_type/:id/custom-data/:fid  # Update single field
```

**Frontend Components**:

1. **Field Builder UI**:
```
+----------------------------------------------+
| Create Custom Field                          |
|----------------------------------------------|
| Field Name: [warranty_expiry_date        ]   |
| Label:      [Warranty Expiry Date        ]   |
| Type:       [Date ▼]                         |
| Entity:     [Assets ▼]                       |
| Required:   [✓]                              |
| Description: [Date when warranty expires  ]  |
|                                              |
| [Cancel]  [Create Field]                     |
+----------------------------------------------+
```

2. **Dynamic Form Rendering**:
```csharp
// Components/CustomFieldsForm.razor
@foreach (var field in customFields)
{
    switch (field.FieldType)
    {
        case "text":
            <InputText @bind-Value="values[field.Id]" />
            break;
        case "dropdown":
            <InputSelect @bind-Value="values[field.Id]">
                @foreach (var option in field.Options)
                {
                    <option value="@option">@option</option>
                }
            </InputSelect>
            break;
        // ...
    }
}
```

**Use Cases**:

**For Construction Company**:
- Assets: building_floor, zone, room_number
- Requests: affected_area, severity_level, safety_hazard

**For Healthcare Facility**:
- Assets: medical_device_type, calibration_date, certification_number
- Requests: patient_impact, regulatory_requirement

**For Manufacturing**:
- Assets: machine_model, production_line, maintenance_interval_hours
- Requests: downtime_cost, production_impact

#### Task Checklist

**Backend**:
- [ ] Create CustomFieldDefinition model
- [ ] Create CustomFieldValue model
- [ ] Create custom_field_service.py
- [ ] Implement validation logic
- [ ] Create API endpoints
- [ ] Add tenant_id to custom field queries
- [ ] Database migrations
- [ ] Test field creation and validation

**Frontend**:
- [ ] Create CustomFieldModel.cs DTOs
- [ ] Add endpoints to ApiService
- [ ] Create CustomFields.razor (admin page)
- [ ] Create FieldBuilder component
- [ ] Create DynamicForm component
- [ ] Integrate into asset/request forms
- [ ] Test field rendering for all types

**Testing**:
- [ ] Test all field types (text, number, date, dropdown, etc.)
- [ ] Test validation rules
- [ ] Test required fields
- [ ] Test file uploads (if implemented)
- [ ] Test query/filter by custom fields

**Estimated Time**: 4-5 days

---

### Phase 5: API Enhancements 🚀

**Priority**: MEDIUM | **Effort**: Medium (3-4 days) | **Value**: High

#### Quick Wins

1. **Rate Limiting**
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: g.current_tenant.id,  # Rate limit per tenant
    default_limits=["1000 per hour", "100 per minute"]
)

@limiter.limit("10 per minute")
def create_request():
    pass
```

2. **API Versioning**
```python
# /api/v2/requests  (new version)
# /api/v1/requests  (legacy, maintained for 6 months)
```

3. **OpenAPI/Swagger Docs**
```python
from flasgger import Swagger

swagger = Swagger(app)

@app.route('/api/v1/requests', methods=['POST'])
def create_request():
    """
    Create Maintenance Request
    ---
    tags:
      - requests
    parameters:
      - in: body
        schema:
          $ref: '#/definitions/RequestCreate'
    responses:
      201:
        description: Request created
    """
```

4. **Webhooks System**
```python
# Tenants can register webhooks for events
POST /api/v1/webhooks
{
    "url": "https://customer.com/maintenance-callback",
    "events": ["request_created", "request_completed"],
    "secret": "shared_secret_for_verification"
}

# System calls webhook when event occurs
```

**Estimated Time**: 3-4 days

---

### Phase 6: Security Hardening 🔒

**Priority**: MEDIUM | **Effort**: Medium (4-5 days) | **Value**: High

1. **Two-Factor Authentication (2FA)**
2. **Comprehensive Audit Logging**
3. **IP Whitelisting per Tenant**
4. **Password Policies**
5. **Account Lockout**
6. **Security Headers**

**Estimated Time**: 4-5 days

---

### Phase 7: Real-Time Features ⚡

**Priority**: MEDIUM-LOW | **Effort**: Medium-High (3-4 days) | **Value**: High (UX)

1. **WebSocket Integration** (Flask-SocketIO + SignalR)
2. **Real-time Notifications**
3. **Live Dashboard Updates**
4. **Online User Presence**

**Estimated Time**: 3-4 days

---

## 📊 Estimated Total Timeline

| Phase | Effort | Days |
|-------|--------|------|
| ✅ Phase 1: Feature Flags | Completed | - |
| Phase 2: RBAC | Medium | 2-3 |
| Phase 3: Multi-Tenant | High | 5-7 |
| Phase 4: Custom Fields | Medium-High | 4-5 |
| Phase 5: API Enhancements | Medium | 3-4 |
| Phase 6: Security | Medium | 4-5 |
| Phase 7: Real-Time | Medium-High | 3-4 |
| **TOTAL** | | **21-28 days** |

---

## 🎯 Recommended Path Forward

**For SaaS Product Launch**:
1. Phase 2 (RBAC) - Foundation for security
2. Phase 3 (Multi-Tenant) - Core SaaS capability
3. Phase 5 (API Enhancements) - Production readiness
4. Phase 6 (Security) - Enterprise readiness
5. Phase 4 (Custom Fields) - Product differentiator
6. Phase 7 (Real-Time) - UX enhancement

**For Demo/Portfolio**:
1. Phase 2 (RBAC) - Shows advanced auth
2. Phase 4 (Custom Fields) - Shows flexibility
3. Phase 5 (API Enhancements) - Shows API design
4. Phase 3 (Multi-Tenant) - Shows scalability thinking

---

## 📝 How to Use This File

**When you return**:
1. Check the "✅ COMPLETED" section to remember what's done
2. Pick the next phase based on your goals (SaaS vs Demo)
3. Review the "Task Checklist" for that phase
4. Start building!

**After completing a phase**:
1. Move it to "✅ COMPLETED" section with date
2. Update estimated times based on actual
3. Commit and tag: `git tag v1.2.0-rbac`

---

## 🔗 Related Files

- `ROADMAP.md` - Original OOP/patterns-focused roadmap
- `CLAUDE.md` - Project overview and conventions
- `claude-session-history.md` - Detailed session logs

---

**Last Session**: Feature Flags implementation (Backend + Frontend)
**Next Session**: Start Phase 2 (RBAC) or choose different phase
**Servers**: `backend: http://localhost:5001` | `frontend: http://localhost:5112`

---

Good luck with the next phase! 🚀
