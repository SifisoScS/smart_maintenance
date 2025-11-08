"""
Services Package - Business Logic Layer

This package contains all service layer implementations:
- BaseService: Common service functionality
- NotificationService: Notification management with Strategy pattern
- UserService: User management and authentication
- AssetService: Asset management
- MaintenanceService: Maintenance request lifecycle
"""

from app.services.base_service import BaseService
from app.services.notification_service import NotificationService
from app.services.user_service import UserService
from app.services.asset_service import AssetService
from app.services.maintenance_service import MaintenanceService

__all__ = [
    'BaseService',
    'NotificationService',
    'UserService',
    'AssetService',
    'MaintenanceService',
]
