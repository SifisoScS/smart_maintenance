"""
Tenant Model
Represents an organization/company using the system (multi-tenancy)
"""
from app.database import db
from app.models.base import BaseModel
from sqlalchemy import Column, String, Integer, DateTime, JSON, Boolean
from datetime import datetime, timedelta


class TenantStatus:
    """Tenant status constants"""
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    TRIAL = 'trial'
    CANCELLED = 'cancelled'


class SubscriptionPlan:
    """Subscription plan constants"""
    FREE = 'free'
    BASIC = 'basic'
    PREMIUM = 'premium'
    ENTERPRISE = 'enterprise'


# Subscription plan definitions with limits and features
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
        'features': [
            'basic_dashboard',
            'email_notifications',
            'mobile_app',
            'api_access',
            'custom_fields'
        ]
    },
    'premium': {
        'name': 'Premium',
        'price': 99,
        'max_users': 50,
        'max_assets': 1000,
        'max_requests_per_month': None,  # Unlimited
        'features': [
            'all_features',
            'priority_support',
            'custom_branding',
            'advanced_analytics',
            'webhooks',
            'sso'
        ]
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': None,  # Custom pricing
        'max_users': None,  # Unlimited
        'max_assets': None,  # Unlimited
        'max_requests_per_month': None,  # Unlimited
        'features': [
            'all_features',
            'dedicated_support',
            'sla',
            'custom_integration',
            'audit_logs',
            'white_label'
        ]
    }
}


class Tenant(BaseModel):
    """
    Tenant Model - Represents an organization using the system

    Multi-tenancy approach: Shared database with tenant_id column
    Each tenant is isolated from others and can have custom settings
    """
    __tablename__ = 'tenants'

    # Basic Info
    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True, nullable=False, index=True)

    # Status
    status = Column(String(50), default=TenantStatus.TRIAL, nullable=False)
    plan = Column(String(50), default=SubscriptionPlan.FREE, nullable=False)

    # Plan Limits (null = unlimited)
    max_users = Column(Integer, default=3)
    max_assets = Column(Integer, default=10)
    max_requests_per_month = Column(Integer, default=50)

    # Customization Settings (JSON)
    # Example: {"timezone": "UTC", "date_format": "MM/DD/YYYY", "features": {...}}
    settings = Column(JSON, default={})

    # Branding
    logo_url = Column(String(500))
    primary_color = Column(String(7), default='#667eea')  # Hex color code
    secondary_color = Column(String(7), default='#764ba2')

    # Billing
    billing_email = Column(String(255))
    subscription_expires = Column(DateTime)
    trial_ends = Column(DateTime)

    # Contact
    contact_name = Column(String(255))
    contact_phone = Column(String(50))

    # Metadata
    is_active = Column(Boolean, default=True)
    onboarded = Column(Boolean, default=False)

    def __init__(self, **kwargs):
        """Initialize tenant with defaults"""
        super().__init__(**kwargs)

        # Set trial end date if status is trial
        if self.status == TenantStatus.TRIAL and not self.trial_ends:
            self.trial_ends = datetime.utcnow() + timedelta(
                days=SUBSCRIPTION_PLANS['free']['duration_days']
            )

        # Set plan limits based on subscription plan
        if self.plan and not self.max_users:
            plan_config = SUBSCRIPTION_PLANS.get(self.plan, SUBSCRIPTION_PLANS['free'])
            self.max_users = plan_config['max_users']
            self.max_assets = plan_config['max_assets']
            self.max_requests_per_month = plan_config['max_requests_per_month']

    def to_dict(self, include_settings=False, include_stats=False):
        """
        Convert tenant to dictionary

        Args:
            include_settings (bool): Include full settings JSON
            include_stats (bool): Include usage statistics

        Returns:
            dict: Tenant data
        """
        data = {
            'id': self.id,
            'name': self.name,
            'subdomain': self.subdomain,
            'status': self.status,
            'plan': self.plan,
            'plan_name': SUBSCRIPTION_PLANS.get(self.plan, {}).get('name', self.plan),
            'max_users': self.max_users,
            'max_assets': self.max_assets,
            'max_requests_per_month': self.max_requests_per_month,
            'logo_url': self.logo_url,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'billing_email': self.billing_email,
            'subscription_expires': self.subscription_expires.isoformat() if self.subscription_expires else None,
            'trial_ends': self.trial_ends.isoformat() if self.trial_ends else None,
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'is_active': self.is_active,
            'onboarded': self.onboarded,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_settings:
            data['settings'] = self.settings

        if include_stats:
            data['usage'] = self.get_usage_stats()

        return data

    def get_plan_config(self):
        """Get plan configuration with limits and features"""
        return SUBSCRIPTION_PLANS.get(self.plan, SUBSCRIPTION_PLANS['free'])

    def has_feature(self, feature_name):
        """
        Check if tenant's plan includes a feature

        Args:
            feature_name (str): Feature name

        Returns:
            bool: True if feature is included
        """
        plan_config = self.get_plan_config()
        features = plan_config.get('features', [])

        # Enterprise and premium have all features
        if 'all_features' in features:
            return True

        return feature_name in features

    def is_trial_expired(self):
        """Check if trial period has expired"""
        if self.status != TenantStatus.TRIAL:
            return False

        if not self.trial_ends:
            return False

        return datetime.utcnow() > self.trial_ends

    def is_subscription_expired(self):
        """Check if paid subscription has expired"""
        if not self.subscription_expires:
            return False

        return datetime.utcnow() > self.subscription_expires

    def get_usage_stats(self):
        """
        Get current usage statistics

        Returns:
            dict: Usage stats (user count, asset count, etc.)
        """
        from app.models.user import User
        from app.models.asset import Asset
        from app.models.request import MaintenanceRequest
        from datetime import datetime
        from dateutil.relativedelta import relativedelta

        # Get counts
        user_count = User.query.filter_by(tenant_id=self.id, is_active=True).count()
        asset_count = Asset.query.filter_by(tenant_id=self.id).count()

        # Requests this month
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        request_count_this_month = MaintenanceRequest.query.filter(
            MaintenanceRequest.tenant_id == self.id,
            MaintenanceRequest.created_at >= month_start
        ).count()

        return {
            'users': {
                'current': user_count,
                'limit': self.max_users,
                'percentage': (user_count / self.max_users * 100) if self.max_users else 0
            },
            'assets': {
                'current': asset_count,
                'limit': self.max_assets,
                'percentage': (asset_count / self.max_assets * 100) if self.max_assets else 0
            },
            'requests_this_month': {
                'current': request_count_this_month,
                'limit': self.max_requests_per_month,
                'percentage': (request_count_this_month / self.max_requests_per_month * 100) if self.max_requests_per_month else 0
            }
        }

    def can_add_user(self):
        """Check if tenant can add more users"""
        if self.max_users is None:  # Unlimited
            return True

        stats = self.get_usage_stats()
        return stats['users']['current'] < self.max_users

    def can_add_asset(self):
        """Check if tenant can add more assets"""
        if self.max_assets is None:  # Unlimited
            return True

        stats = self.get_usage_stats()
        return stats['assets']['current'] < self.max_assets

    def can_create_request(self):
        """Check if tenant can create more requests this month"""
        if self.max_requests_per_month is None:  # Unlimited
            return True

        stats = self.get_usage_stats()
        return stats['requests_this_month']['current'] < self.max_requests_per_month

    def __repr__(self):
        return f'<Tenant {self.name} ({self.subdomain})>'
