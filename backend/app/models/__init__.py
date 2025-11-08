"""
Models package initialization.

Exports all models for easy importing.
"""

from app.models.base import BaseModel
from app.models.user import User, UserRole
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

__all__ = [
    # Base
    'BaseModel',

    # User
    'User',
    'UserRole',

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
]
