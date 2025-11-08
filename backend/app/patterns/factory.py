"""
Factory Pattern Implementation for MaintenanceRequest

Purpose: Centralize complex object creation logic.

Benefits:
- Hides complexity of creating specialized request types
- Supports Open/Closed Principle (new types without modifying existing code)
- Provides single point for request instantiation
- Enables runtime type selection

OOP Principles:
- Open/Closed: Can add new request types without modifying factory
- Single Responsibility: Factory handles only object creation
- Polymorphism: Returns appropriate subclass based on type
"""

from typing import Optional
from app.models.request import (
    MaintenanceRequest,
    ElectricalRequest,
    PlumbingRequest,
    HVACRequest,
    RequestType,
    RequestPriority,
    RequestStatus
)


class MaintenanceRequestFactory:
    """
    Factory for creating specialized MaintenanceRequest instances.

    Design Pattern: Factory Method Pattern
    Use Case: Create appropriate request subclass based on request type

    This demonstrates Polymorphism - callers work with MaintenanceRequest
    interface, but get specialized subclasses (Electrical, Plumbing, HVAC).
    """

    # Registry mapping request types to classes
    # This makes the factory Open/Closed - new types can be registered
    _request_types = {
        RequestType.ELECTRICAL: ElectricalRequest,
        RequestType.PLUMBING: PlumbingRequest,
        RequestType.HVAC: HVACRequest,
    }

    @classmethod
    def create_request(cls, request_type: RequestType, title: str, description: str,
                       submitter_id: int, asset_id: Optional[int] = None,
                       priority: RequestPriority = RequestPriority.MEDIUM,
                       category: Optional[str] = None,
                       **kwargs) -> MaintenanceRequest:
        """
        Create appropriate MaintenanceRequest subclass based on type.

        Args:
            request_type: Type of request (RequestType enum)
            title: Request title
            description: Detailed description
            submitter_id: User ID of submitter
            asset_id: Asset ID
            priority: Request priority (default MEDIUM)
            **kwargs: Type-specific fields (voltage, pipe_type, etc.)

        Returns:
            Specialized MaintenanceRequest instance (Electrical/Plumbing/HVAC)

        Raises:
            ValueError: If request type is invalid

        Example:
            factory = MaintenanceRequestFactory()
            request = factory.create_request(
                request_type=RequestType.ELECTRICAL,
                title="Outlet not working",
                description="Office 201 outlet is dead",
                submitter_id=1,
                asset_id=5,
                priority=RequestPriority.HIGH,
                voltage="120V",
                is_emergency=True
            )
        """
        # Validate request type
        if not isinstance(request_type, RequestType):
            raise ValueError(f"Invalid request type: {request_type}")

        # Get appropriate class from registry
        request_class = cls._request_types.get(request_type)

        if not request_class:
            raise ValueError(f"No request class registered for type: {request_type.value}")

        # Create instance with common fields
        request = request_class(
            title=title,
            description=description,
            submitter_id=submitter_id,
            asset_id=asset_id,
            priority=priority,
            status=RequestStatus.SUBMITTED,
            category=category,
            **kwargs  # Type-specific fields
        )

        # Validate the created instance
        request.validate()

        return request

    @classmethod
    def create_electrical_request(cls, title: str, description: str,
                                  submitter_id: int, asset_id: Optional[int] = None,
                                  voltage: Optional[str] = None,
                                  circuit_number: Optional[str] = None,
                                  breaker_location: Optional[str] = None,
                                  is_emergency: bool = False,
                                  category: Optional[str] = None,
                                  **kwargs) -> ElectricalRequest:
        """
        Convenience method to create ElectricalRequest.

        Args:
            title: Request title
            description: Detailed description
            submitter_id: User ID of submitter
            asset_id: Asset ID
            voltage: Voltage specification (optional)
            circuit_number: Circuit number (optional)
            breaker_location: Breaker box location (optional)
            is_emergency: Emergency flag (default False)
            **kwargs: Additional common fields

        Returns:
            ElectricalRequest instance

        Example:
            request = MaintenanceRequestFactory.create_electrical_request(
                title="Power outage",
                description="Entire floor lost power",
                submitter_id=1,
                asset_id=10,
                is_emergency=True
            )
        """
        return cls.create_request(
            request_type=RequestType.ELECTRICAL,
            title=title,
            description=description,
            submitter_id=submitter_id,
            asset_id=asset_id,
            voltage=voltage,
            circuit_number=circuit_number,
            breaker_location=breaker_location,
            is_emergency=is_emergency,
            category=category,
            **kwargs
        )

    @classmethod
    def create_plumbing_request(cls, title: str, description: str,
                                submitter_id: int, asset_id: Optional[int] = None,
                                pipe_type: Optional[str] = None,
                                water_pressure: Optional[str] = None,
                                leak_severity: Optional[str] = None,
                                water_shutoff_required: bool = False,
                                category: Optional[str] = None,
                                **kwargs) -> PlumbingRequest:
        """
        Convenience method to create PlumbingRequest.

        Args:
            title: Request title
            description: Detailed description
            submitter_id: User ID of submitter
            asset_id: Asset ID
            pipe_type: Type of pipe (optional)
            water_pressure: Water pressure reading (optional)
            leak_severity: Severity level (minor/moderate/severe) (optional)
            water_shutoff_required: Water shutoff flag (default False)
            **kwargs: Additional common fields

        Returns:
            PlumbingRequest instance

        Example:
            request = MaintenanceRequestFactory.create_plumbing_request(
                title="Pipe leak",
                description="Bathroom sink leaking",
                submitter_id=2,
                asset_id=15,
                leak_severity="severe",
                water_shutoff_required=True
            )
        """
        return cls.create_request(
            request_type=RequestType.PLUMBING,
            title=title,
            description=description,
            submitter_id=submitter_id,
            asset_id=asset_id,
            pipe_type=pipe_type,
            water_pressure=water_pressure,
            leak_severity=leak_severity,
            water_shutoff_required=water_shutoff_required,
            category=category,
            **kwargs
        )

    @classmethod
    def create_hvac_request(cls, title: str, description: str,
                           submitter_id: int, asset_id: Optional[int] = None,
                           system_type: Optional[str] = None,
                           temperature_issue: Optional[str] = None,
                           refrigerant_leak: bool = False,
                           category: Optional[str] = None,
                           **kwargs) -> HVACRequest:
        """
        Convenience method to create HVACRequest.

        Args:
            title: Request title
            description: Detailed description
            submitter_id: User ID of submitter
            asset_id: Asset ID
            system_type: System type (heating/cooling/ventilation) (optional)
            temperature_issue: Temperature problem description (optional)
            refrigerant_leak: Refrigerant leak flag (default False)
            **kwargs: Additional common fields

        Returns:
            HVACRequest instance

        Example:
            request = MaintenanceRequestFactory.create_hvac_request(
                title="AC not cooling",
                description="Server room AC failing",
                submitter_id=3,
                asset_id=20,
                system_type="cooling",
                temperature_issue="Room temperature at 85°F",
                priority=RequestPriority.URGENT
            )
        """
        return cls.create_request(
            request_type=RequestType.HVAC,
            title=title,
            description=description,
            submitter_id=submitter_id,
            asset_id=asset_id,
            system_type=system_type,
            temperature_issue=temperature_issue,
            refrigerant_leak=refrigerant_leak,
            category=category,
            **kwargs
        )

    @classmethod
    def create_request_from_dict(cls, data: dict) -> MaintenanceRequest:
        """
        Create request from dictionary (useful for API endpoints).

        Args:
            data: Dictionary with request data, must include 'type' field

        Returns:
            MaintenanceRequest instance

        Raises:
            ValueError: If required fields missing or invalid

        Example:
            data = {
                'type': 'electrical',
                'title': 'Light fixture broken',
                'description': 'Hallway light not working',
                'submitter_id': 1,
                'asset_id': 8,
                'voltage': '120V'
            }
            request = MaintenanceRequestFactory.create_request_from_dict(data)
        """
        # Extract and validate request type
        type_str = data.get('type')
        if not type_str:
            raise ValueError("Request type is required")

        # Convert string to RequestType enum
        try:
            if isinstance(type_str, str):
                request_type = RequestType(type_str.lower())
            elif isinstance(type_str, RequestType):
                request_type = type_str
            else:
                raise ValueError(f"Invalid request type format: {type_str}")
        except ValueError:
            raise ValueError(f"Invalid request type: {type_str}")

        # Extract common fields
        common_fields = {
            'title': data.get('title'),
            'description': data.get('description'),
            'submitter_id': data.get('submitter_id'),
            'asset_id': data.get('asset_id'),
            'category': data.get('category'),
        }

        # Validate required fields (asset_id is optional)
        required_fields = ['title', 'description', 'submitter_id']
        for field in required_fields:
            if common_fields.get(field) is None:
                raise ValueError(f"{field} is required")

        # Optional common fields
        if 'priority' in data:
            priority_str = data['priority']
            if isinstance(priority_str, str):
                common_fields['priority'] = RequestPriority(priority_str.lower())
            elif isinstance(priority_str, RequestPriority):
                common_fields['priority'] = priority_str

        # Copy type-specific fields
        type_specific_fields = {}
        if request_type == RequestType.ELECTRICAL:
            type_specific_fields = {
                'voltage': data.get('voltage'),
                'circuit_number': data.get('circuit_number'),
                'breaker_location': data.get('breaker_location'),
                'is_emergency': data.get('is_emergency', False),
            }
        elif request_type == RequestType.PLUMBING:
            type_specific_fields = {
                'pipe_type': data.get('pipe_type'),
                'water_pressure': data.get('water_pressure'),
                'leak_severity': data.get('leak_severity'),
                'water_shutoff_required': data.get('water_shutoff_required', False),
            }
        elif request_type == RequestType.HVAC:
            type_specific_fields = {
                'system_type': data.get('system_type'),
                'temperature_issue': data.get('temperature_issue'),
                'refrigerant_leak': data.get('refrigerant_leak', False),
            }

        # Create request using factory method
        return cls.create_request(
            request_type=request_type,
            **common_fields,
            **type_specific_fields
        )

    @classmethod
    def register_request_type(cls, request_type: RequestType, request_class: type):
        """
        Register a new request type (for future extensibility).

        This method demonstrates the Open/Closed Principle - new types
        can be added without modifying existing factory code.

        Args:
            request_type: RequestType enum value
            request_class: MaintenanceRequest subclass

        Example:
            # In future, if we add GeneralRequest type
            MaintenanceRequestFactory.register_request_type(
                RequestType.GENERAL,
                GeneralRequest
            )
        """
        cls._request_types[request_type] = request_class

    @classmethod
    def get_supported_types(cls) -> list:
        """
        Get list of supported request types.

        Returns:
            List of RequestType enum values
        """
        return list(cls._request_types.keys())
