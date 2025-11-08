"""
Asset Schemas

Input validation for asset management endpoints.
"""

from marshmallow import Schema, fields, validate


class AssetCreateSchema(Schema):
    """Schema for creating an asset."""
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200),
        error_messages={'required': 'Asset name is required'}
    )
    asset_tag = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={'required': 'Asset tag is required'}
    )
    category = fields.String(
        required=True,
        validate=validate.OneOf(['electrical', 'plumbing', 'hvac', 'it_equipment', 'building', 'furniture', 'other']),
        error_messages={
            'required': 'Category is required',
            'invalid': 'Invalid category'
        }
    )
    subcategory = fields.String(validate=validate.Length(max=100))
    building = fields.String(validate=validate.Length(max=100))
    floor = fields.String(validate=validate.Length(max=20))
    room = fields.String(validate=validate.Length(max=50))
    location_details = fields.String(validate=validate.Length(max=255))
    status = fields.String(validate=validate.OneOf(['active', 'in_repair', 'out_of_service', 'retired']))
    condition = fields.String(validate=validate.OneOf(['excellent', 'good', 'fair', 'poor', 'critical']))
    description = fields.String(validate=validate.Length(max=500))
    manufacturer = fields.String(validate=validate.Length(max=100))
    model = fields.String(validate=validate.Length(max=100))
    serial_number = fields.String(validate=validate.Length(max=100))
    purchase_date = fields.Date()
    warranty_expiry = fields.Date()


class AssetUpdateSchema(Schema):
    """Schema for updating an asset."""
    name = fields.String(validate=validate.Length(min=1, max=200))
    subcategory = fields.String(validate=validate.Length(max=100))
    building = fields.String(validate=validate.Length(max=100))
    floor = fields.String(validate=validate.Length(max=20))
    room = fields.String(validate=validate.Length(max=50))
    location_details = fields.String(validate=validate.Length(max=255))
    status = fields.String(validate=validate.OneOf(['active', 'in_repair', 'out_of_service', 'retired']))
    condition = fields.String(validate=validate.OneOf(['excellent', 'good', 'fair', 'poor', 'critical']))
    description = fields.String(validate=validate.Length(max=500))
    manufacturer = fields.String(validate=validate.Length(max=100))
    model = fields.String(validate=validate.Length(max=100))
    serial_number = fields.String(validate=validate.Length(max=100))
    purchase_date = fields.Date()
    warranty_expiry = fields.Date()


class AssetConditionUpdateSchema(Schema):
    """Schema for updating asset condition."""
    condition = fields.String(
        required=True,
        validate=validate.OneOf(['excellent', 'good', 'fair', 'poor', 'critical']),
        error_messages={
            'required': 'Condition is required',
            'invalid': 'Invalid condition'
        }
    )
