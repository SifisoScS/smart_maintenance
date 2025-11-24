"""
Models package initialization.

Exports all models for easy importing.
"""

from app.models.base import BaseModel
from app.models.user import User, UserRole
from app.models.permission import Permission
from app.models.role import Role, role_permissions, user_roles
from app.models.asset import Asset, AssetCategory, AssetCondition, AssetStatus
from app.models.request import (
    MaintenanceRequest,
    ElectricalRequest,
    PlumbingRequest,
    HVACRequest,
    RequestStatus,
    RequestPriority,
    RequestType
)
from app.models.feature_flag import FeatureFlag, FeatureCategory, Features
from app.models.tenant import Tenant, TenantStatus, SubscriptionPlan, SUBSCRIPTION_PLANS
from app.models.tenant_subscription import TenantSubscription, SubscriptionStatus, BillingCycle

__all__ = [
    # Base
    'BaseModel',

    # User
    'User',
    'UserRole',

    # RBAC
    'Permission',
    'Role',
    'role_permissions',
    'user_roles',

    # Asset
    'Asset',
    'AssetCategory',
    'AssetCondition',
    'AssetStatus',

    # Maintenance Requests
    'MaintenanceRequest',
    'ElectricalRequest',
    'PlumbingRequest',
    'HVACRequest',
    'RequestStatus',
    'RequestPriority',
    'RequestType',

    # Feature Flags
    'FeatureFlag',
    'FeatureCategory',
    'Features',

    # Multi-Tenancy
    'Tenant',
    'TenantStatus',
    'SubscriptionPlan',
    'SUBSCRIPTION_PLANS',
    'TenantSubscription',
    'SubscriptionStatus',
    'BillingCycle',
]
