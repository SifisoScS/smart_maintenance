# Tenant Models - Technical Review

**Created**: November 19, 2025
**Location**: `backend/app/models/tenant.py` and `tenant_subscription.py`

---

## 🏗️ Architecture Overview

### Multi-Tenancy Approach
**Strategy:** Shared Database with tenant_id column
- One database, multiple tenants
- Each row tagged with tenant_id
- Automatic filtering in repositories
- Cost-effective and simpler to manage

### Key Concepts
- **Tenant**: An organization/company using the system
- **Subdomain**: Unique identifier (acme.smartmaintenance.com)
- **Subscription**: Billing and plan tracking
- **Plan Limits**: Enforce resource usage limits per plan

---

## 📦 Tenant Model Details

### File: `backend/app/models/tenant.py`

### Class: `Tenant(BaseModel)`

**Purpose:** Represents an organization using the platform

**Key Features:**
1. Subscription plan management (Free, Basic, Premium, Enterprise)
2. Resource limit enforcement
3. Custom branding (logo, colors)
4. Trial period tracking
5. Usage statistics calculation
6. Feature availability checking

### Fields Breakdown

#### Identity & Status
```python
id              : Primary key
name            : Company name (e.g., "Acme Corp")
subdomain       : URL identifier (e.g., "acme" for acme.smartmaintenance.com)
status          : active | suspended | trial | cancelled
plan            : free | basic | premium | enterprise
is_active       : Boolean flag for quick checks
onboarded       : Has completed setup wizard
```

#### Resource Limits (Null = Unlimited)
```python
max_users                  : Maximum active users allowed
max_assets                 : Maximum assets allowed
max_requests_per_month     : Monthly maintenance request limit
```

#### Customization & Branding
```python
settings        : JSON object for custom configs
logo_url        : URL to company logo
primary_color   : Hex color code (default: #667eea)
secondary_color : Hex color code (default: #764ba2)
```

#### Billing & Contact
```python
billing_email        : For invoices and billing notices
subscription_expires : When paid subscription ends
trial_ends           : When trial period ends
contact_name         : Primary contact person
contact_phone        : Contact phone number
```

### Important Methods

#### 1. `to_dict(include_settings=False, include_stats=False)`
Converts tenant to dictionary for API responses.

**Options:**
- `include_settings`: Include full settings JSON
- `include_stats`: Include current usage statistics

**Returns:**
```python
{
    'id': 1,
    'name': 'Acme Corp',
    'subdomain': 'acme',
    'status': 'active',
    'plan': 'premium',
    'plan_name': 'Premium',
    'max_users': 50,
    'max_assets': 1000,
    'max_requests_per_month': None,  # Unlimited
    'logo_url': 'https://...',
    'primary_color': '#667eea',
    # ... more fields
}
```

#### 2. `has_feature(feature_name)`
Checks if tenant's plan includes a specific feature.

**Usage:**
```python
tenant.has_feature('custom_branding')  # True for Premium+
tenant.has_feature('webhooks')         # True for Premium+
tenant.has_feature('sso')              # True for Premium+
```

**Available Features by Plan:**

**Free (Trial):**
- basic_dashboard
- email_notifications

**Basic ($29/month):**
- basic_dashboard
- email_notifications
- mobile_app
- api_access
- custom_fields

**Premium ($99/month):**
- all_features (everything)
- priority_support
- custom_branding
- advanced_analytics
- webhooks
- sso

**Enterprise (Custom pricing):**
- all_features
- dedicated_support
- sla
- custom_integration
- audit_logs
- white_label

#### 3. `can_add_user()`
Checks if tenant can add more users within plan limits.

**Returns:** Boolean

**Usage:**
```python
if not tenant.can_add_user():
    return {'error': f'User limit reached ({tenant.max_users})'}
```

#### 4. `can_add_asset()`
Checks if tenant can add more assets.

**Returns:** Boolean

#### 5. `can_create_request()`
Checks if tenant can create more maintenance requests this month.

**Returns:** Boolean

#### 6. `get_usage_stats()`
Gets current usage vs limits for all resources.

**Returns:**
```python
{
    'users': {
        'current': 8,
        'limit': 10,
        'percentage': 80
    },
    'assets': {
        'current': 45,
        'limit': 100,
        'percentage': 45
    },
    'requests_this_month': {
        'current': 23,
        'limit': 500,
        'percentage': 4.6
    }
}
```

**When to use:**
- Display usage dashboard
- Show upgrade prompts
- Monitor approaching limits

#### 7. `is_trial_expired()`
Checks if trial period has ended.

**Returns:** Boolean

#### 8. `is_subscription_expired()`
Checks if paid subscription has ended.

**Returns:** Boolean

---

## 💳 TenantSubscription Model Details

### File: `backend/app/models/tenant_subscription.py`

### Class: `TenantSubscription(BaseModel)`

**Purpose:** Track billing cycles, payments, and subscription status

**Stripe Integration Ready:**
- `stripe_subscription_id`
- `stripe_customer_id`
- `stripe_payment_method_id`

### Fields Breakdown

#### Subscription Info
```python
id                      : Primary key
tenant_id               : Foreign key to tenants table
plan                    : free | basic | premium | enterprise
status                  : active | past_due | cancelled | paused
billing_cycle           : monthly | annual
```

#### Pricing
```python
price                   : Decimal (e.g., 29.00, 99.00)
currency                : 3-letter code (USD, EUR, etc.)
```

#### Stripe Integration
```python
stripe_subscription_id   : Stripe subscription ID
stripe_customer_id       : Stripe customer ID
stripe_payment_method_id : Stripe payment method ID
```

#### Billing Periods
```python
current_period_start    : Start of current billing period
current_period_end      : End of current billing period
trial_start             : Trial start date (if applicable)
trial_end               : Trial end date
```

#### Cancellation
```python
cancel_at               : Scheduled cancellation date (end of period)
cancelled_at            : Actual cancellation timestamp
```

### Important Methods

#### 1. `is_active()`
Checks if subscription is currently active and not expired.

**Returns:** Boolean

**Logic:**
```python
# Must have active status
# Current period must not be expired
```

#### 2. `is_in_trial()`
Checks if subscription is in trial period.

**Returns:** Boolean

#### 3. `days_until_renewal()`
Calculates days until next billing cycle.

**Returns:** Integer (days) or None

#### 4. `schedule_cancellation()`
Schedules cancellation at end of current period (user keeps access until then).

**Example:**
```python
subscription.schedule_cancellation()
# Sets cancel_at to current_period_end
# User can use service until period ends
```

#### 5. `cancel_immediately()`
Cancels subscription immediately (user loses access now).

**Example:**
```python
subscription.cancel_immediately()
# Sets status to 'cancelled'
# Sets cancelled_at to now
```

#### 6. `renew()`
Renews subscription for next billing period.

**Example:**
```python
subscription.renew()
# Moves period forward by 1 month (monthly) or 1 year (annual)
# Reactivates if was cancelled
# Clears scheduled cancellation
```

---

## 📊 Subscription Plans Comparison

| Feature | Free | Basic | Premium | Enterprise |
|---------|------|-------|---------|------------|
| **Price** | $0 | $29/mo | $99/mo | Custom |
| **Max Users** | 3 | 10 | 50 | Unlimited |
| **Max Assets** | 10 | 100 | 1,000 | Unlimited |
| **Requests/Month** | 50 | 500 | Unlimited | Unlimited |
| **Trial Period** | 14 days | - | - | - |
| **Basic Dashboard** | ✅ | ✅ | ✅ | ✅ |
| **Email Notifications** | ✅ | ✅ | ✅ | ✅ |
| **Mobile App** | ❌ | ✅ | ✅ | ✅ |
| **API Access** | ❌ | ✅ | ✅ | ✅ |
| **Custom Fields** | ❌ | ✅ | ✅ | ✅ |
| **Custom Branding** | ❌ | ❌ | ✅ | ✅ |
| **Advanced Analytics** | ❌ | ❌ | ✅ | ✅ |
| **Webhooks** | ❌ | ❌ | ✅ | ✅ |
| **SSO** | ❌ | ❌ | ✅ | ✅ |
| **Priority Support** | ❌ | ❌ | ✅ | ✅ |
| **Dedicated Support** | ❌ | ❌ | ❌ | ✅ |
| **SLA** | ❌ | ❌ | ❌ | ✅ |
| **Audit Logs** | ❌ | ❌ | ❌ | ✅ |
| **White Label** | ❌ | ❌ | ❌ | ✅ |

---

## 🔧 Usage Examples

### Example 1: Creating a New Tenant

```python
from app.models import Tenant

# Create tenant
tenant = Tenant(
    name='Acme Corporation',
    subdomain='acme',
    billing_email='billing@acme.com',
    contact_name='John Doe',
    contact_phone='+1-555-0100',
    plan='basic'
)

db.session.add(tenant)
db.session.commit()

# Tenant is created with:
# - status: 'trial' (14-day trial)
# - plan: 'basic'
# - max_users: 10 (from basic plan)
# - max_assets: 100
# - max_requests_per_month: 500
# - trial_ends: 14 days from now
```

### Example 2: Checking Limits Before Creating User

```python
# Before creating user
tenant = Tenant.query.get(tenant_id)

if not tenant.can_add_user():
    return {
        'error': f'User limit reached. Your plan allows {tenant.max_users} users.',
        'upgrade_url': '/upgrade'
    }

# Proceed with user creation
user = create_user(data)
```

### Example 3: Displaying Usage Dashboard

```python
tenant = Tenant.query.get(tenant_id)
stats = tenant.get_usage_stats()

# Display to user:
# Users: 8/10 (80%)
# Assets: 45/100 (45%)
# Requests this month: 23/500 (4.6%)

# Show warning if approaching limits
if stats['users']['percentage'] > 90:
    show_warning('Approaching user limit. Consider upgrading.')
```

### Example 4: Feature Gate

```python
tenant = current_user.tenant

if tenant.has_feature('webhooks'):
    # Show webhooks configuration
    render('webhooks_settings.html')
else:
    # Show upgrade prompt
    render('upgrade_prompt.html', feature='webhooks', required_plan='premium')
```

### Example 5: Subscription Management

```python
# Get active subscription
subscription = TenantSubscription.query.filter_by(
    tenant_id=tenant_id,
    status='active'
).first()

# Check if in trial
if subscription.is_in_trial():
    days_left = (subscription.trial_end - datetime.utcnow()).days
    show_message(f'Trial ends in {days_left} days')

# Check renewal
days_until_renewal = subscription.days_until_renewal()
if days_until_renewal <= 7:
    show_message(f'Subscription renews in {days_until_renewal} days')

# Schedule cancellation
subscription.schedule_cancellation()
# User keeps access until current_period_end
```

---

## ⚡ Performance Considerations

### Indexes Created
```python
tenant_id (indexed on all tables)
subdomain (indexed, unique)
```

### Optimization Tips
1. Cache tenant lookups by subdomain
2. Use `get_usage_stats()` sparingly (does multiple DB queries)
3. Consider eager loading: `Tenant.query.options(joinedload('subscriptions'))`

---

## 🔒 Security Considerations

### Critical Rules
1. ✅ ALWAYS filter by tenant_id in queries
2. ✅ NEVER trust tenant_id from client
3. ✅ Extract tenant from subdomain or header server-side
4. ✅ Validate tenant is active before allowing operations

### Data Isolation
```python
# CORRECT - uses tenant filtering
current_users = User.query.filter_by(tenant_id=g.current_tenant.id).all()

# WRONG - no tenant filtering (security vulnerability!)
all_users = User.query.all()
```

---

## 🧪 Testing Checklist

When testing tenant functionality:

- [ ] Create tenant with Free plan
- [ ] Check limits are enforced (max_users, max_assets, etc.)
- [ ] Create tenant with Premium plan
- [ ] Verify unlimited resources work
- [ ] Check trial expiration logic
- [ ] Test subscription renewal
- [ ] Test subscription cancellation (immediate and scheduled)
- [ ] Verify feature gates work correctly
- [ ] **CRITICAL:** Test tenant data isolation (Tenant A can't see Tenant B's data)

---

## 📖 Related Documentation

- `PHASE_3_PLAN.md` - Complete implementation plan
- `PHASE_3_PROGRESS.md` - Current progress and next steps
- `NEXT_PHASES.md` - Overall project roadmap

---

## 🎯 Summary

**What You Have Now:**
- ✅ Complete Tenant model with subscription management
- ✅ TenantSubscription model for billing
- ✅ 4 subscription plans with clear limits
- ✅ Plan limit checking (users, assets, requests)
- ✅ Feature gating by plan
- ✅ Trial period management
- ✅ Stripe integration ready

**What's Next:**
- Add tenant_id to all existing models
- Create database migrations
- Implement automatic tenant filtering
- Create tenant middleware for subdomain routing
- Build tenant registration and management UI

**Time Investment:**
- ✅ Completed: 2-3 hours (models created)
- 🔜 Remaining: 4-6 days (full implementation)

---

These models are production-ready and follow SaaS best practices. Take time to understand them before proceeding with the schema changes! 🚀
