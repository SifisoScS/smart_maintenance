"""
Unit tests for MaintenanceRequestFactory.

Tests demonstrate Factory Pattern benefits:
- Centralizes complex object creation
- Type-safe creation based on runtime selection
- Extensibility (Open/Closed Principle)
"""

import pytest
from app.patterns.factory import MaintenanceRequestFactory
from app.models import (
    ElectricalRequest,
    PlumbingRequest,
    HVACRequest,
    RequestType,
    RequestPriority,
    RequestStatus
)


class TestMaintenanceRequestFactory:
    """Test suite for MaintenanceRequestFactory (Factory Pattern)"""

    @pytest.fixture(autouse=True)
    def setup(self, db_session, sample_user, sample_asset):
        """Set up test dependencies"""
        self.factory = MaintenanceRequestFactory()
        self.submitter_id = sample_user.id
        self.asset_id = sample_asset.id

    def test_create_electrical_request(self, db_session):
        """Test factory creates ElectricalRequest instance"""
        request = self.factory.create_request(
            request_type=RequestType.ELECTRICAL,
            title='Power outlet issue',
            description='Outlet in room 201 not working',
            submitter_id=self.submitter_id,
            asset_id=self.asset_id,
            priority=RequestPriority.HIGH,
            voltage='120V',
            circuit_number='C12',
            is_emergency=True
        )

        # Verify correct type created
        assert isinstance(request, ElectricalRequest)
        assert request.type == RequestType.ELECTRICAL.value

        # Verify common fields
        assert request.title == 'Power outlet issue'
        assert request.description == 'Outlet in room 201 not working'
        assert request.submitter_id == self.submitter_id
        assert request.asset_id == self.asset_id
        # Emergency automatically sets priority to URGENT (validated in model)
        assert request.priority == RequestPriority.URGENT
        assert request.status == RequestStatus.SUBMITTED

        # Verify electrical-specific fields
        assert request.voltage == '120V'
        assert request.circuit_number == 'C12'
        assert request.is_emergency is True

    def test_create_plumbing_request(self, db_session):
        """Test factory creates PlumbingRequest instance"""
        request = self.factory.create_request(
            request_type=RequestType.PLUMBING,
            title='Pipe leak',
            description='Water leaking from bathroom sink',
            submitter_id=self.submitter_id,
            asset_id=self.asset_id,
            pipe_type='PVC',
            leak_severity='severe',
            water_shutoff_required=True
        )

        # Verify correct type created
        assert isinstance(request, PlumbingRequest)
        assert request.type == RequestType.PLUMBING.value

        # Verify common fields
        assert request.title == 'Pipe leak'
        assert request.submitter_id == self.submitter_id

        # Verify plumbing-specific fields
        assert request.pipe_type == 'PVC'
        assert request.leak_severity == 'severe'
        assert request.water_shutoff_required is True

    def test_create_hvac_request(self, db_session):
        """Test factory creates HVACRequest instance"""
        request = self.factory.create_request(
            request_type=RequestType.HVAC,
            title='AC not cooling',
            description='Server room temperature too high',
            submitter_id=self.submitter_id,
            asset_id=self.asset_id,
            system_type='cooling',
            temperature_issue='Room at 85°F',
            refrigerant_leak=False
        )

        # Verify correct type created
        assert isinstance(request, HVACRequest)
        assert request.type == RequestType.HVAC.value

        # Verify hvac-specific fields
        assert request.system_type == 'cooling'
        assert request.temperature_issue == 'Room at 85°F'
        assert request.refrigerant_leak is False

    def test_create_electrical_request_convenience_method(self, db_session):
        """Test electrical convenience factory method"""
        request = self.factory.create_electrical_request(
            title='Circuit breaker tripped',
            description='Main breaker keeps tripping',
            submitter_id=self.submitter_id,
            asset_id=self.asset_id,
            breaker_location='Panel A',
            is_emergency=True
        )

        assert isinstance(request, ElectricalRequest)
        assert request.breaker_location == 'Panel A'
        assert request.is_emergency is True

    def test_create_plumbing_request_convenience_method(self, db_session):
        """Test plumbing convenience factory method"""
        request = self.factory.create_plumbing_request(
            title='Clogged drain',
            description='Kitchen sink not draining',
            submitter_id=self.submitter_id,
            asset_id=self.asset_id,
            water_shutoff_required=False
        )

        assert isinstance(request, PlumbingRequest)
        assert request.water_shutoff_required is False

    def test_create_hvac_request_convenience_method(self, db_session):
        """Test HVAC convenience factory method"""
        request = self.factory.create_hvac_request(
            title='Heater malfunction',
            description='Office heating not working',
            submitter_id=self.submitter_id,
            asset_id=self.asset_id,
            system_type='heating',
            priority=RequestPriority.URGENT
        )

        assert isinstance(request, HVACRequest)
        assert request.system_type == 'heating'
        assert request.priority == RequestPriority.URGENT

    def test_create_request_from_dict_electrical(self, db_session):
        """Test creating request from dictionary (API use case)"""
        data = {
            'type': 'electrical',
            'title': 'Faulty wiring',
            'description': 'Sparks from outlet',
            'submitter_id': self.submitter_id,
            'asset_id': self.asset_id,
            'priority': 'urgent',
            'voltage': '240V',
            'is_emergency': True
        }

        request = self.factory.create_request_from_dict(data)

        assert isinstance(request, ElectricalRequest)
        assert request.title == 'Faulty wiring'
        assert request.priority == RequestPriority.URGENT
        assert request.voltage == '240V'
        assert request.is_emergency is True

    def test_create_request_from_dict_plumbing(self, db_session):
        """Test creating plumbing request from dictionary"""
        data = {
            'type': 'plumbing',
            'title': 'Burst pipe',
            'description': 'Water flooding floor',
            'submitter_id': self.submitter_id,
            'asset_id': self.asset_id,
            'leak_severity': 'severe',
            'water_shutoff_required': True
        }

        request = self.factory.create_request_from_dict(data)

        assert isinstance(request, PlumbingRequest)
        assert request.leak_severity == 'severe'
        assert request.water_shutoff_required is True

    def test_create_request_from_dict_hvac(self, db_session):
        """Test creating HVAC request from dictionary"""
        data = {
            'type': 'hvac',
            'title': 'Ventilation issue',
            'description': 'Poor air circulation',
            'submitter_id': self.submitter_id,
            'asset_id': self.asset_id,
            'system_type': 'ventilation'
        }

        request = self.factory.create_request_from_dict(data)

        assert isinstance(request, HVACRequest)
        assert request.system_type == 'ventilation'

    def test_create_request_invalid_type(self, db_session):
        """Test factory raises error for invalid type"""
        with pytest.raises(ValueError, match="Invalid request type"):
            self.factory.create_request(
                request_type='invalid_type',
                title='Test',
                description='Test',
                submitter_id=self.submitter_id,
                asset_id=self.asset_id
            )

    def test_create_request_from_dict_missing_type(self, db_session):
        """Test factory raises error when type missing"""
        data = {
            'title': 'Test',
            'description': 'Test',
            'submitter_id': self.submitter_id,
            'asset_id': self.asset_id
        }

        with pytest.raises(ValueError, match="type is required"):
            self.factory.create_request_from_dict(data)

    def test_create_request_from_dict_missing_required_fields(self, db_session):
        """Test factory raises error when required fields missing"""
        data = {
            'type': 'electrical',
            'title': 'Test'
            # Missing description, submitter_id, asset_id
        }

        with pytest.raises(ValueError, match="is required"):
            self.factory.create_request_from_dict(data)

    def test_create_request_from_dict_invalid_type_value(self, db_session):
        """Test factory raises error for invalid type value"""
        data = {
            'type': 'invalid',
            'title': 'Test',
            'description': 'Test',
            'submitter_id': self.submitter_id,
            'asset_id': self.asset_id
        }

        with pytest.raises(ValueError, match="Invalid request type"):
            self.factory.create_request_from_dict(data)

    def test_electrical_emergency_auto_priority(self, db_session):
        """Test electrical emergency automatically sets urgent priority"""
        request = self.factory.create_electrical_request(
            title='Emergency',
            description='Test',
            submitter_id=self.submitter_id,
            asset_id=self.asset_id,
            is_emergency=True,
            priority=RequestPriority.LOW  # Will be overridden
        )

        # Validation in model should set to URGENT
        request.validate()
        assert request.priority == RequestPriority.URGENT

    def test_plumbing_severe_leak_auto_priority(self, db_session):
        """Test severe leak automatically increases priority"""
        request = self.factory.create_plumbing_request(
            title='Severe leak',
            description='Test',
            submitter_id=self.submitter_id,
            asset_id=self.asset_id,
            leak_severity='severe',
            priority=RequestPriority.LOW  # Will be overridden
        )

        # Validation in model should increase priority
        request.validate()
        assert request.priority in [RequestPriority.HIGH, RequestPriority.URGENT]

    def test_hvac_refrigerant_leak_auto_priority(self, db_session):
        """Test refrigerant leak automatically increases priority"""
        request = self.factory.create_hvac_request(
            title='Refrigerant leak',
            description='Test',
            submitter_id=self.submitter_id,
            asset_id=self.asset_id,
            refrigerant_leak=True,
            priority=RequestPriority.LOW  # Will be overridden
        )

        # Validation in model should increase priority
        request.validate()
        assert request.priority in [RequestPriority.HIGH, RequestPriority.URGENT]

    def test_get_supported_types(self, db_session):
        """Test retrieving list of supported request types"""
        supported_types = self.factory.get_supported_types()

        assert RequestType.ELECTRICAL in supported_types
        assert RequestType.PLUMBING in supported_types
        assert RequestType.HVAC in supported_types
        assert len(supported_types) == 3

    def test_factory_pattern_polymorphism(self, db_session):
        """
        Test Factory Pattern enables polymorphism.

        All subtypes can be treated as MaintenanceRequest.
        """
        # Create different types
        electrical = self.factory.create_electrical_request(
            title='E', description='E', submitter_id=self.submitter_id, asset_id=self.asset_id
        )
        plumbing = self.factory.create_plumbing_request(
            title='P', description='P', submitter_id=self.submitter_id, asset_id=self.asset_id
        )
        hvac = self.factory.create_hvac_request(
            title='H', description='H', submitter_id=self.submitter_id, asset_id=self.asset_id
        )

        # All can be treated uniformly (Liskov Substitution Principle)
        requests = [electrical, plumbing, hvac]

        for request in requests:
            # Common interface works for all
            assert hasattr(request, 'title')
            assert hasattr(request, 'description')
            assert hasattr(request, 'status')
            assert hasattr(request, 'priority')
            assert hasattr(request, 'assign_to')
            assert hasattr(request, 'start_work')
            assert hasattr(request, 'complete')

    def test_request_to_dict_includes_type_specific_fields(self, db_session):
        """Test serialization includes type-specific fields"""
        electrical = self.factory.create_electrical_request(
            title='Test',
            description='Test',
            submitter_id=self.submitter_id,
            asset_id=self.asset_id,
            voltage='120V',
            is_emergency=True
        )

        data = electrical.to_dict()

        assert 'voltage' in data
        assert 'is_emergency' in data
        assert data['voltage'] == '120V'
        assert data['is_emergency'] is True
