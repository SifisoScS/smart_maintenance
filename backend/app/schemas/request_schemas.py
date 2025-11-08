"""
Maintenance Request Schemas

Input validation for maintenance request endpoints.
"""

from marshmallow import Schema, fields, validate


class RequestCreateSchema(Schema):
    """Schema for creating a maintenance request."""
    request_type = fields.String(
        required=True,
        validate=validate.OneOf(['electrical', 'plumbing', 'hvac']),
        error_messages={
            'required': 'Request type is required',
            'invalid': 'Request type must be electrical, plumbing, or hvac'
        }
    )
    asset_id = fields.Integer(
        required=False,
        allow_none=True,
        validate=validate.Range(min=1),
        missing=None
    )
    title = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200),
        error_messages={'required': 'Title is required'}
    )
    description = fields.String(
        required=True,
        validate=validate.Length(min=1, max=2000),
        error_messages={'required': 'Description is required'}
    )
    priority = fields.String(
        validate=validate.OneOf(['low', 'medium', 'high', 'urgent']),
        missing='medium'
    )

    # Electrical-specific fields
    voltage = fields.String(validate=validate.Length(max=20))
    circuit_number = fields.String(validate=validate.Length(max=50))
    breaker_location = fields.String(validate=validate.Length(max=100))
    is_emergency = fields.Boolean()

    # Plumbing-specific fields
    pipe_type = fields.String(validate=validate.Length(max=50))
    water_pressure = fields.String(validate=validate.Length(max=20))
    leak_severity = fields.String(validate=validate.Length(max=20))
    water_shutoff_required = fields.Boolean()

    # HVAC-specific fields
    system_type = fields.String(validate=validate.Length(max=50))
    temperature_issue = fields.String(validate=validate.Length(max=100))
    filter_last_changed = fields.Date()
    refrigerant_leak = fields.Boolean()


class RequestUpdateSchema(Schema):
    """Schema for updating a maintenance request."""
    title = fields.String(validate=validate.Length(min=1, max=200))
    description = fields.String(validate=validate.Length(min=1, max=2000))
    priority = fields.String(validate=validate.OneOf(['low', 'medium', 'high', 'urgent']))


class RequestAssignSchema(Schema):
    """Schema for assigning a request to a technician."""
    technician_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1),
        error_messages={'required': 'Technician ID is required'}
    )


class RequestCompleteSchema(Schema):
    """Schema for completing a maintenance request."""
    completion_notes = fields.String(
        required=True,
        validate=validate.Length(min=1, max=2000),
        error_messages={'required': 'Completion notes are required'}
    )
    actual_hours = fields.Float(validate=validate.Range(min=0, max=1000))
