"""
Authentication Schemas

Input validation for authentication endpoints.
"""

from marshmallow import Schema, fields, validate, ValidationError


class LoginSchema(Schema):
    """Schema for user login."""
    email = fields.Email(required=True, error_messages={
        'required': 'Email is required',
        'invalid': 'Invalid email format'
    })
    password = fields.String(required=True, validate=validate.Length(min=1), error_messages={
        'required': 'Password is required'
    })


class RegisterSchema(Schema):
    """Schema for user registration."""
    email = fields.Email(required=True, error_messages={
        'required': 'Email is required',
        'invalid': 'Invalid email format'
    })
    password = fields.String(
        required=True,
        validate=validate.Length(min=8, max=100),
        error_messages={
            'required': 'Password is required',
            'invalid': 'Password must be between 8 and 100 characters'
        }
    )
    first_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={'required': 'First name is required'}
    )
    last_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={'required': 'Last name is required'}
    )
    role = fields.String(
        required=True,
        validate=validate.OneOf(['admin', 'technician', 'client']),
        error_messages={
            'required': 'Role is required',
            'invalid': 'Role must be one of: admin, technician, client'
        }
    )
    phone = fields.String(validate=validate.Length(max=20), allow_none=True, load_default=None)
    department = fields.String(validate=validate.Length(max=100), allow_none=True, load_default=None)
