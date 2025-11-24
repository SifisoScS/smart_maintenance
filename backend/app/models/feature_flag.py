"""
Feature Flag Model

Enables/disables features dynamically without code deployment.
Supports gradual rollouts, A/B testing, and feature experimentation.
"""

from enum import Enum
from app.models.base import BaseModel
from app.database import db


class FeatureCategory(Enum):
    """Feature categories for organization."""
    ANALYTICS = 'analytics'
    NOTIFICATIONS = 'notifications'
    INTEGRATIONS = 'integrations'
    MOBILE = 'mobile'
    AUTOMATION = 'automation'
    SECURITY = 'security'
    UI = 'ui'
    EXPERIMENTAL = 'experimental'


class FeatureFlag(BaseModel):
    """
    Feature flag for controlling feature availability.

    Attributes:
        feature_key: Unique identifier (e.g., 'advanced_reporting')
        name: Display name (e.g., 'Advanced Reporting')
        description: What the feature does
        category: Feature category for organization
        enabled: Whether feature is currently enabled
        rollout_percentage: Percentage of users to enable for (0-100)
        metadata: Additional configuration as JSON
    """

    __tablename__ = 'feature_flags'

    # Core fields
    feature_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    # Organization
    category = db.Column(db.Enum(FeatureCategory), nullable=False, default=FeatureCategory.EXPERIMENTAL)

    # Enablement
    enabled = db.Column(db.Boolean, nullable=False, default=False, index=True)
    rollout_percentage = db.Column(db.Integer, default=100)  # 0-100

    # Config data for feature-specific settings
    config_data = db.Column(db.JSON, default=dict)

    # Multi-Tenancy
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)
    tenant = db.relationship('Tenant', backref='feature_flags')

    def __init__(self, feature_key: str, name: str, description: str = None,
                 category: FeatureCategory = FeatureCategory.EXPERIMENTAL,
                 enabled: bool = False, rollout_percentage: int = 100,
                 config_data: dict = None):
        """
        Initialize feature flag.

        Args:
            feature_key: Unique identifier for the feature
            name: Human-readable name
            description: What the feature does
            category: Feature category
            enabled: Whether feature is enabled
            rollout_percentage: Percentage of users to enable for
            config_data: Additional configuration
        """
        self.feature_key = feature_key
        self.name = name
        self.description = description
        self.category = category
        self.enabled = enabled
        self.rollout_percentage = rollout_percentage
        self.config_data = config_data or {}

    def is_enabled_for_user(self, user_id: int = None) -> bool:
        """
        Check if feature is enabled for a specific user.

        Args:
            user_id: Optional user ID for rollout percentage calculation

        Returns:
            bool: True if feature is enabled for this user
        """
        if not self.enabled:
            return False

        # If 100% rollout, everyone gets it
        if self.rollout_percentage >= 100:
            return True

        # If 0% rollout, nobody gets it
        if self.rollout_percentage <= 0:
            return False

        # If no user_id provided, use rollout percentage
        if user_id is None:
            return True  # Assume enabled if checking without user context

        # Deterministic rollout based on user_id
        # Same user always gets same result
        user_bucket = (user_id % 100) + 1  # 1-100
        return user_bucket <= self.rollout_percentage

    def to_dict(self) -> dict:
        """Convert feature flag to dictionary."""
        data = super().to_dict()

        # Convert enum to string value
        if 'category' in data:
            data['category'] = self.category.value if isinstance(self.category, FeatureCategory) else self.category

        return data

    def __repr__(self) -> str:
        """String representation."""
        return f"<FeatureFlag {self.feature_key} enabled={self.enabled}>"


# Pre-defined feature keys as constants for easy reference
class Features:
    """
    Feature key constants.

    Use these constants in code instead of hardcoded strings:
    Example: if feature_service.is_enabled(Features.ADVANCED_REPORTING):
    """

    # Analytics features
    ADVANCED_REPORTING = 'advanced_reporting'
    PREDICTIVE_ANALYTICS = 'predictive_analytics'
    CUSTOM_DASHBOARDS = 'custom_dashboards'
    DATA_EXPORT = 'data_export'

    # Notification features
    EMAIL_NOTIFICATIONS = 'email_notifications'
    SMS_NOTIFICATIONS = 'sms_notifications'
    PUSH_NOTIFICATIONS = 'push_notifications'
    IN_APP_NOTIFICATIONS = 'in_app_notifications'

    # Integration features
    API_ACCESS = 'api_access'
    WEBHOOK_INTEGRATIONS = 'webhook_integrations'
    THIRD_PARTY_SYNC = 'third_party_sync'

    # Mobile features
    MOBILE_APP_ACCESS = 'mobile_app_access'
    OFFLINE_MODE = 'offline_mode'
    BARCODE_SCANNING = 'barcode_scanning'

    # Automation features
    CUSTOM_WORKFLOWS = 'custom_workflows'
    AUTO_ASSIGNMENT = 'auto_assignment'
    SCHEDULED_MAINTENANCE = 'scheduled_maintenance'

    # Asset features
    ASSET_QR_CODES = 'asset_qr_codes'
    ASSET_TRACKING = 'asset_tracking'
    ASSET_LIFECYCLE = 'asset_lifecycle'

    # Security features
    TWO_FACTOR_AUTH = 'two_factor_auth'
    AUDIT_LOGGING = 'audit_logging'
    IP_WHITELISTING = 'ip_whitelisting'

    # UI features
    DARK_MODE = 'dark_mode'
    COMPACT_VIEW = 'compact_view'
    DRAG_DROP_UI = 'drag_drop_ui'

    @classmethod
    def all_features(cls) -> list:
        """Get list of all feature keys."""
        return [
            value for name, value in vars(cls).items()
            if isinstance(value, str) and not name.startswith('_')
        ]
