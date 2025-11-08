"""
MaintenanceRequest Models with Polymorphic Inheritance

Demonstrates:
- OOP Inheritance: Specialized request types inherit from base
- Polymorphism: Different request types share common interface
- Liskov Substitution Principle: Subtypes can replace base type
- Open/Closed Principle: New request types can be added without modifying existing code
"""

from enum import Enum
from app.models.base import BaseModel
from app.database import db


class RequestStatus(Enum):
    """Request status enumeration"""
    SUBMITTED = 'submitted'
    ASSIGNED = 'assigned'
    IN_PROGRESS = 'in_progress'
    ON_HOLD = 'on_hold'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class RequestPriority(Enum):
    """Request priority enumeration"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'


class RequestType(Enum):
    """Request type enumeration - used by Factory pattern"""
    ELECTRICAL = 'electrical'
    PLUMBING = 'plumbing'
    HVAC = 'hvac'


class MaintenanceRequest(BaseModel):
    """
    Base maintenance request model with polymorphic inheritance.

    OOP Principles:
    - Inheritance: Specialized requests inherit common behavior
    - Polymorphism: All requests share the same interface
    - Encapsulation: Status transition logic internal

    SQLAlchemy Polymorphic Pattern:
    - Uses 'type' column to distinguish subclasses
    - All subclasses stored in same table (single table inheritance)
    - Factory pattern will create appropriate subclass

    Relationships:
    - Belongs to User (submitter)
    - Belongs to User (assigned technician)
    - Belongs to Asset
    """

    __tablename__ = 'maintenance_requests'

    # Polymorphic discriminator column
    type = db.Column(db.String(50), nullable=False)

    # Basic Information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True)

    # Status and Priority
    status = db.Column(db.Enum(RequestStatus), nullable=False, default=RequestStatus.SUBMITTED)
    priority = db.Column(db.Enum(RequestPriority), nullable=False, default=RequestPriority.MEDIUM)

    # Relationships
    submitter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_technician_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=True)

    # Work Details
    estimated_hours = db.Column(db.Float, nullable=True)
    actual_hours = db.Column(db.Float, nullable=True)
    completion_notes = db.Column(db.Text, nullable=True)

    # Relationships (will be set up after all models are defined)
    submitter = db.relationship('User', foreign_keys=[submitter_id], backref='submitted_requests')
    assigned_technician = db.relationship('User', foreign_keys=[assigned_technician_id], backref='assigned_requests')
    asset = db.relationship('Asset', backref='maintenance_requests')

    # Polymorphic configuration
    __mapper_args__ = {
        'polymorphic_identity': 'maintenance_request',
        'polymorphic_on': type
    }

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, title='{self.title}', status='{self.status.value}')>"

    @property
    def is_open(self):
        """Check if request is still open (not completed or cancelled)"""
        return self.status not in [RequestStatus.COMPLETED, RequestStatus.CANCELLED]

    @property
    def is_assigned(self):
        """Check if request has been assigned to a technician"""
        return self.assigned_technician_id is not None

    @property
    def is_completed(self):
        """Check if request is completed"""
        return self.status == RequestStatus.COMPLETED

    def assign_to(self, technician_id):
        """
        Assign request to a technician.

        Args:
            technician_id (int): Technician user ID

        Raises:
            ValueError: If request is already completed/cancelled
        """
        if not self.is_open:
            raise ValueError("Cannot assign completed or cancelled request")

        self.assigned_technician_id = technician_id
        if self.status == RequestStatus.SUBMITTED:
            self.status = RequestStatus.ASSIGNED

    def start_work(self):
        """
        Mark request as in progress.

        Raises:
            ValueError: If request is not assigned or already completed
        """
        if not self.is_assigned:
            raise ValueError("Request must be assigned before starting work")

        if not self.is_open:
            raise ValueError("Cannot start work on completed or cancelled request")

        self.status = RequestStatus.IN_PROGRESS

    def put_on_hold(self, reason=None):
        """
        Put request on hold.

        Args:
            reason (str, optional): Reason for putting on hold
        """
        if not self.is_open:
            raise ValueError("Cannot put completed or cancelled request on hold")

        self.status = RequestStatus.ON_HOLD
        if reason and self.completion_notes:
            self.completion_notes += f"\n[ON HOLD]: {reason}"
        elif reason:
            self.completion_notes = f"[ON HOLD]: {reason}"

    def resume_work(self):
        """Resume work from on-hold status"""
        if self.status != RequestStatus.ON_HOLD:
            raise ValueError("Can only resume requests that are on hold")

        self.status = RequestStatus.IN_PROGRESS

    def complete(self, completion_notes=None, actual_hours=None):
        """
        Mark request as completed.

        Args:
            completion_notes (str, optional): Notes about completion
            actual_hours (float, optional): Actual hours worked

        Raises:
            ValueError: If request is not in progress
        """
        if self.status not in [RequestStatus.IN_PROGRESS, RequestStatus.ON_HOLD]:
            raise ValueError("Request must be in progress to complete")

        self.status = RequestStatus.COMPLETED
        if completion_notes:
            self.completion_notes = completion_notes
        if actual_hours:
            self.actual_hours = actual_hours

    def cancel(self, reason=None):
        """
        Cancel the request.

        Args:
            reason (str, optional): Reason for cancellation
        """
        if not self.is_open:
            raise ValueError("Cannot cancel completed or already cancelled request")

        self.status = RequestStatus.CANCELLED
        if reason:
            self.completion_notes = f"[CANCELLED]: {reason}"

    def validate(self):
        """
        Validate maintenance request data.

        Raises:
            ValueError: If validation fails
        """
        # Title validation
        if not self.title or not self.title.strip():
            raise ValueError("Request title is required")

        # Description validation
        if not self.description or not self.description.strip():
            raise ValueError("Request description is required")

        # Submitter validation
        if not self.submitter_id:
            raise ValueError("Submitter is required")

        # Asset validation (optional - requests can be general or asset-specific)
        # No validation needed - asset_id is now optional

        # Status validation
        if not isinstance(self.status, RequestStatus):
            raise ValueError("Invalid request status")

        # Priority validation
        if not isinstance(self.priority, RequestPriority):
            raise ValueError("Invalid request priority")

    def to_dict(self):
        """Convert request to dictionary"""
        data = super().to_dict()

        # Convert enums to string values
        if 'status' in data:
            data['status'] = self.status.value if isinstance(self.status, RequestStatus) else self.status

        if 'priority' in data:
            data['priority'] = self.priority.value if isinstance(self.priority, RequestPriority) else self.priority

        # Add request_type as alias for type (for API consistency)
        if 'type' in data:
            data['request_type'] = data['type']

        # Add assigned_to as alias for assigned_technician_id (for API consistency)
        if 'assigned_technician_id' in data:
            data['assigned_to'] = data['assigned_technician_id']

        # Add computed properties
        data['is_open'] = self.is_open
        data['is_assigned'] = self.is_assigned
        data['is_completed'] = self.is_completed

        return data


class ElectricalRequest(MaintenanceRequest):
    """
    Specialized request for electrical maintenance.

    Demonstrates: Polymorphism and Inheritance
    """

    # Electrical-specific fields
    voltage = db.Column(db.String(20), nullable=True)
    circuit_number = db.Column(db.String(50), nullable=True)
    breaker_location = db.Column(db.String(100), nullable=True)
    is_emergency = db.Column(db.Boolean, default=False)

    __mapper_args__ = {
        'polymorphic_identity': RequestType.ELECTRICAL.value,
    }

    def validate(self):
        """Extended validation for electrical requests"""
        super().validate()  # Call parent validation

        # If marked as emergency, priority should be urgent
        if self.is_emergency and self.priority != RequestPriority.URGENT:
            self.priority = RequestPriority.URGENT

    def to_dict(self):
        """Extended to_dict with electrical-specific fields"""
        data = super().to_dict()
        data['voltage'] = self.voltage
        data['circuit_number'] = self.circuit_number
        data['breaker_location'] = self.breaker_location
        data['is_emergency'] = self.is_emergency
        return data


class PlumbingRequest(MaintenanceRequest):
    """
    Specialized request for plumbing maintenance.

    Demonstrates: Polymorphism and Inheritance
    """

    # Plumbing-specific fields
    pipe_type = db.Column(db.String(50), nullable=True)
    water_pressure = db.Column(db.String(20), nullable=True)
    leak_severity = db.Column(db.String(20), nullable=True)  # minor, moderate, severe
    water_shutoff_required = db.Column(db.Boolean, default=False)

    __mapper_args__ = {
        'polymorphic_identity': RequestType.PLUMBING.value,
    }

    def __init__(self, category=None, **kwargs):
        super().__init__(category=category, **kwargs)

    def validate(self):
        """Extended validation for plumbing requests"""
        super().validate()

        # If water shutoff required or severe leak, priority should be high/urgent
        if self.water_shutoff_required or self.leak_severity == 'severe':
            if self.priority not in [RequestPriority.HIGH, RequestPriority.URGENT]:
                self.priority = RequestPriority.HIGH

    def to_dict(self):
        """Extended to_dict with plumbing-specific fields"""
        data = super().to_dict()
        data['pipe_type'] = self.pipe_type
        data['water_pressure'] = self.water_pressure
        data['leak_severity'] = self.leak_severity
        data['water_shutoff_required'] = self.water_shutoff_required
        return data


class HVACRequest(MaintenanceRequest):
    """
    Specialized request for HVAC maintenance.

    Demonstrates: Polymorphism and Inheritance
    """

    # HVAC-specific fields
    system_type = db.Column(db.String(50), nullable=True)  # heating, cooling, ventilation
    temperature_issue = db.Column(db.String(100), nullable=True)
    filter_last_changed = db.Column(db.Date, nullable=True)
    refrigerant_leak = db.Column(db.Boolean, default=False)

    __mapper_args__ = {
        'polymorphic_identity': RequestType.HVAC.value,
    }

    def validate(self):
        """Extended validation for HVAC requests"""
        super().validate()

        # Refrigerant leak is high priority
        if self.refrigerant_leak and self.priority not in [RequestPriority.HIGH, RequestPriority.URGENT]:
            self.priority = RequestPriority.HIGH

    def to_dict(self):
        """Extended to_dict with HVAC-specific fields"""
        data = super().to_dict()
        data['system_type'] = self.system_type
        data['temperature_issue'] = self.temperature_issue
        data['refrigerant_leak'] = self.refrigerant_leak

        if self.filter_last_changed:
            data['filter_last_changed'] = self.filter_last_changed.isoformat()

        return data
