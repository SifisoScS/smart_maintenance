"""
Asset Model for tracking organizational assets

Demonstrates:
- OOP Encapsulation: Status management logic internal to model
- State Management: Asset condition and status tracking
- Enum Pattern: Type-safe categories and statuses
"""

from enum import Enum
from app.models.base import BaseModel
from app.database import db


class AssetCategory(Enum):
    """Asset category enumeration"""
    ELECTRICAL = 'electrical'
    PLUMBING = 'plumbing'
    HVAC = 'hvac'
    IT_EQUIPMENT = 'it_equipment'
    BUILDING = 'building'
    FURNITURE = 'furniture'
    OTHER = 'other'


class AssetCondition(Enum):
    """Asset condition enumeration"""
    EXCELLENT = 'excellent'
    GOOD = 'good'
    FAIR = 'fair'
    POOR = 'poor'
    CRITICAL = 'critical'


class AssetStatus(Enum):
    """Asset operational status"""
    ACTIVE = 'active'
    IN_REPAIR = 'in_repair'
    OUT_OF_SERVICE = 'out_of_service'
    RETIRED = 'retired'


class Asset(BaseModel):
    """
    Asset entity representing physical/digital organizational assets.

    OOP Principles:
    - Encapsulation: Status management and validation internal
    - Single Responsibility: Manages only asset data
    - State Pattern (implicit): Status transitions with validation

    Relationships:
    - One asset can have many maintenance requests
    """

    __tablename__ = 'assets'

    # Basic Information
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    asset_tag = db.Column(db.String(50), unique=True, nullable=False, index=True)

    # Classification
    category = db.Column(db.Enum(AssetCategory), nullable=False)
    subcategory = db.Column(db.String(100), nullable=True)

    # Location
    building = db.Column(db.String(100), nullable=True)
    floor = db.Column(db.String(20), nullable=True)
    room = db.Column(db.String(50), nullable=True)
    location_details = db.Column(db.String(255), nullable=True)

    # Status and Condition
    status = db.Column(db.Enum(AssetStatus), nullable=False, default=AssetStatus.ACTIVE)
    condition = db.Column(db.Enum(AssetCondition), nullable=False, default=AssetCondition.GOOD)

    # Maintenance Information
    manufacturer = db.Column(db.String(100), nullable=True)
    model = db.Column(db.String(100), nullable=True)
    serial_number = db.Column(db.String(100), nullable=True)
    purchase_date = db.Column(db.Date, nullable=True)
    warranty_expiry = db.Column(db.Date, nullable=True)

    # Relationships (will be defined when we create MaintenanceRequest)
    # maintenance_requests = relationship with MaintenanceRequest

    def __repr__(self):
        return f"<Asset(id={self.id}, tag='{self.asset_tag}', name='{self.name}', status='{self.status.value}')>"

    @property
    def full_location(self):
        """
        Compute full location string.

        Returns:
            str: Formatted location string
        """
        parts = []
        if self.building:
            parts.append(f"Building: {self.building}")
        if self.floor:
            parts.append(f"Floor: {self.floor}")
        if self.room:
            parts.append(f"Room: {self.room}")
        if self.location_details:
            parts.append(self.location_details)

        return ", ".join(parts) if parts else "Location not specified"

    @property
    def needs_maintenance(self):
        """
        Check if asset needs maintenance based on condition.

        Returns:
            bool: True if condition is poor or critical
        """
        return self.condition in [AssetCondition.POOR, AssetCondition.CRITICAL]

    @property
    def is_operational(self):
        """
        Check if asset is currently operational.

        Returns:
            bool: True if status is active
        """
        return self.status == AssetStatus.ACTIVE

    def mark_under_repair(self):
        """
        Mark asset as under repair.

        OOP Principle: Encapsulation - Status change logic internal
        """
        if self.status == AssetStatus.RETIRED:
            raise ValueError("Cannot repair retired asset")

        self.status = AssetStatus.IN_REPAIR

    def mark_repaired(self, new_condition=None):
        """
        Mark asset as repaired and return to active status.

        Args:
            new_condition (AssetCondition, optional): Updated condition after repair
        """
        self.status = AssetStatus.ACTIVE

        if new_condition and isinstance(new_condition, AssetCondition):
            self.condition = new_condition

    def mark_out_of_service(self):
        """Mark asset as out of service"""
        self.status = AssetStatus.OUT_OF_SERVICE

    def retire(self):
        """
        Retire asset (final status).

        Once retired, asset cannot be reactivated.
        """
        self.status = AssetStatus.RETIRED

    def update_condition(self, new_condition):
        """
        Update asset condition with validation.

        Args:
            new_condition (AssetCondition): New condition value

        Raises:
            ValueError: If condition is invalid
        """
        if not isinstance(new_condition, AssetCondition):
            raise ValueError("Invalid asset condition")

        self.condition = new_condition

        # Automatically mark for repair if condition degrades to poor/critical
        if new_condition in [AssetCondition.POOR, AssetCondition.CRITICAL]:
            if self.status == AssetStatus.ACTIVE:
                # Don't automatically change status, but flag it
                # This would be a good place to trigger Observer pattern
                # to notify administrators
                pass

    def validate(self):
        """
        Validate asset data.

        Raises:
            ValueError: If validation fails
        """
        # Name validation
        if not self.name or not self.name.strip():
            raise ValueError("Asset name is required")

        # Asset tag validation
        if not self.asset_tag or not self.asset_tag.strip():
            raise ValueError("Asset tag is required")

        # Category validation
        if not isinstance(self.category, AssetCategory):
            raise ValueError("Invalid asset category")

        # Status validation
        if not isinstance(self.status, AssetStatus):
            raise ValueError("Invalid asset status")

        # Condition validation
        if not isinstance(self.condition, AssetCondition):
            raise ValueError("Invalid asset condition")

    def to_dict(self):
        """
        Convert asset to dictionary.

        Returns:
            dict: Asset data with frontend-friendly field names
        """
        data = super().to_dict()

        # Convert enums to string values
        if 'category' in data:
            data['category'] = self.category.value if isinstance(self.category, AssetCategory) else self.category

        if 'status' in data:
            data['status'] = self.status.value if isinstance(self.status, AssetStatus) else self.status

        if 'condition' in data:
            data['condition'] = self.condition.value if isinstance(self.condition, AssetCondition) else self.condition

        # Add computed properties
        data['full_location'] = self.full_location
        data['needs_maintenance'] = self.needs_maintenance
        data['is_operational'] = self.is_operational

        # Map fields for frontend (PascalCase and renamed fields)
        data['AssetCode'] = data.get('asset_tag', '')
        data['AssetType'] = data.get('category', '')
        data['Location'] = self.full_location
        data['PurchaseDate'] = self.purchase_date.isoformat() if self.purchase_date else None
        data['PurchasePrice'] = None  # Not tracked in backend yet
        data['CreatedAt'] = self.created_at.isoformat() if hasattr(self, 'created_at') and self.created_at else None

        # Format dates
        if self.purchase_date:
            data['purchase_date'] = self.purchase_date.isoformat()
        if self.warranty_expiry:
            data['warranty_expiry'] = self.warranty_expiry.isoformat()

        return data
