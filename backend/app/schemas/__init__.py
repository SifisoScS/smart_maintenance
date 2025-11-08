"""
Schemas Package - Input Validation

This package contains Marshmallow schemas for:
- Request body validation
- Response serialization
- Type checking
"""

from app.schemas.auth_schemas import LoginSchema, RegisterSchema
from app.schemas.user_schemas import UserUpdateSchema, PasswordChangeSchema
from app.schemas.asset_schemas import AssetCreateSchema, AssetUpdateSchema
from app.schemas.request_schemas import (
    RequestCreateSchema,
    RequestAssignSchema,
    RequestCompleteSchema
)

__all__ = [
    'LoginSchema',
    'RegisterSchema',
    'UserUpdateSchema',
    'PasswordChangeSchema',
    'AssetCreateSchema',
    'AssetUpdateSchema',
    'RequestCreateSchema',
    'RequestAssignSchema',
    'RequestCompleteSchema',
]
