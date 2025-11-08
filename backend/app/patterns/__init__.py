"""
Patterns package initialization.

Exports all design pattern implementations.
"""

from app.patterns.singleton import SingletonMeta
from app.patterns.factory import MaintenanceRequestFactory
from app.patterns.strategy import (
    NotificationStrategy,
    EmailNotificationStrategy,
    SMSNotificationStrategy,
    InAppNotificationStrategy,
    NotificationContext
)

__all__ = [
    'SingletonMeta',
    'MaintenanceRequestFactory',
    'NotificationStrategy',
    'EmailNotificationStrategy',
    'SMSNotificationStrategy',
    'InAppNotificationStrategy',
    'NotificationContext',
]
