"""
User Schemas

Input validation for user management endpoints.
"""

from marshmallow import Schema, fields, validate


class UserUpdateSchema(Schema):
    """Schema for updating user profile."""
    first_name = fields.String(validate=validate.Length(min=1, max=50))
    last_name = fields.String(validate=validate.Length(min=1, max=50))
    phone = fields.String(validate=validate.Length(max=20))
    department = fields.String(validate=validate.Length(max=100))


class PasswordChangeSchema(Schema):
    """Schema for changing password."""
    old_password = fields.String(required=True, error_messages={
        'required': 'Current password is required'
    })
    new_password = fields.String(
        required=True,
        validate=validate.Length(min=8, max=100),
        error_messages={
            'required': 'New password is required',
            'invalid': 'Password must be between 8 and 100 characters'
        }
    )
