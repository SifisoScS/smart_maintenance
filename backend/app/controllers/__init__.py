"""
Controllers Package - API Layer

This package contains Flask blueprints for:
- Authentication (login, logout, refresh)
- User management
- Asset management
- Maintenance request management
"""

from app.controllers.auth_controller import auth_bp
from app.controllers.user_controller import user_bp
from app.controllers.asset_controller import asset_bp
from app.controllers.request_controller import request_bp

__all__ = [
    'auth_bp',
    'user_bp',
    'asset_bp',
    'request_bp',
]
