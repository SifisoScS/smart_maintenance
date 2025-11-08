"""
Unit Tests for MaintenanceService

Tests:
- Multi-repository orchestration
- Complex business rule enforcement
- Factory pattern integration
- Notification triggers
- Authorization checks
- State transitions
"""

import pytest
from unittest.mock import Mock, MagicMock, call, patch
from app.services.maintenance_service import MaintenanceService
from app.models import (
    UserRole, RequestStatus, RequestPriority, RequestType,
    AssetStatus, AssetCondition
)


class TestCreateRequest:
    """Test maintenance request creation."""

    @patch('app.services.maintenance_service.db')
    def test_create_request_success(self, mock_db):
        """Test successful request creation."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        # Mock submitter
        submitter = Mock()
        submitter.id = 1
        submitter.email = 'client@example.com'
        submitter.is_active = True
        user_repo.get_by_id.return_value = submitter

        # Mock asset
        asset = Mock()
        asset.id = 10
        asset.name = 'Server A'
        asset_repo.get_by_id.return_value = asset

        # Mock created request
        mock_request = Mock()
        mock_request.id = 100
        mock_request.title = 'Fix Electrical'
        mock_request.type = RequestType.ELECTRICAL
        mock_request.priority = RequestPriority.MEDIUM
        mock_request.to_dict.return_value = {
            'id': 100,
            'title': 'Fix Electrical',
            'type': 'electrical',
            'priority': 'medium'
        }
        factory.create_request.return_value = mock_request

        # Mock notification success
        notification_service.notify_by_role.return_value = {'success': True}

        result = service.create_request(
            request_type='electrical',
            submitter_id=1,
            asset_id=10,
            title='Fix Electrical',
            description='Lights not working',
            priority='medium'
        )

        assert result['success'] is True
        assert result['data']['id'] == 100
        assert 'created successfully' in result['message']

        # Verify factory was used
        factory.create_request.assert_called_once()

        # Verify notification was sent to admins
        notification_service.notify_by_role.assert_called_once()
        call_args = notification_service.notify_by_role.call_args[1]
        assert call_args['role'] == 'admin'

    def test_create_request_validates_submitter_exists(self):
        """Test business rule: submitter must exist."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        # Submitter doesn't exist
        user_repo.get_by_id.return_value = None

        result = service.create_request(
            request_type='electrical',
            submitter_id=999,
            asset_id=10,
            title='Fix',
            description='Desc',
            priority='medium'
        )

        assert result['success'] is False
        assert 'Submitter not found' in result['error']
        factory.create_request.assert_not_called()

    def test_create_request_validates_submitter_active(self):
        """Test business rule: submitter must be active."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        # Submitter exists but is inactive
        submitter = Mock()
        submitter.id = 1
        submitter.is_active = False
        user_repo.get_by_id.return_value = submitter

        result = service.create_request(
            request_type='electrical',
            submitter_id=1,
            asset_id=10,
            title='Fix',
            description='Desc',
            priority='medium'
        )

        assert result['success'] is False
        assert 'not active' in result['error']
        factory.create_request.assert_not_called()

    def test_create_request_validates_asset_exists(self):
        """Test business rule: asset must exist."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        # Submitter exists
        submitter = Mock()
        submitter.is_active = True
        user_repo.get_by_id.return_value = submitter

        # Asset doesn't exist
        asset_repo.get_by_id.return_value = None

        result = service.create_request(
            request_type='electrical',
            submitter_id=1,
            asset_id=999,
            title='Fix',
            description='Desc',
            priority='medium'
        )

        assert result['success'] is False
        assert 'Asset not found' in result['error']
        factory.create_request.assert_not_called()

    @patch('app.services.maintenance_service.db')
    def test_create_request_validation_errors(self, mock_db):
        """Test validation of required fields."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        # Missing request_type (empty string)
        result = service.create_request(
            request_type='',
            submitter_id=1,
            asset_id=10,
            title='Fix',
            description='Desc'
        )
        assert result['success'] is False
        assert 'request_type cannot be empty' in result['error']

        # Invalid submitter_id
        result = service.create_request(
            request_type='electrical',
            submitter_id=-1,
            asset_id=10,
            title='Fix',
            description='Desc'
        )
        assert result['success'] is False

        # Missing title (empty string)
        result = service.create_request(
            request_type='electrical',
            submitter_id=1,
            asset_id=10,
            title='',
            description='Desc'
        )
        assert result['success'] is False
        assert 'title cannot be empty' in result['error']

    def test_create_request_invalid_type_or_priority(self):
        """Test validation of enum values."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        submitter = Mock()
        submitter.is_active = True
        user_repo.get_by_id.return_value = submitter

        asset = Mock()
        asset_repo.get_by_id.return_value = asset

        # Invalid request type
        result = service.create_request(
            request_type='invalid_type',
            submitter_id=1,
            asset_id=10,
            title='Fix',
            description='Desc',
            priority='medium'
        )
        assert result['success'] is False
        assert 'Invalid value' in result['error']

        # Invalid priority
        result = service.create_request(
            request_type='electrical',
            submitter_id=1,
            asset_id=10,
            title='Fix',
            description='Desc',
            priority='invalid_priority'
        )
        assert result['success'] is False
        assert 'Invalid value' in result['error']

    @patch('app.services.maintenance_service.db')
    def test_create_request_uses_factory_pattern(self, mock_db):
        """Test request creation uses Factory pattern."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        submitter = Mock()
        submitter.id = 1
        submitter.email = 'client@example.com'
        submitter.is_active = True
        user_repo.get_by_id.return_value = submitter

        asset = Mock()
        asset.id = 10
        asset.name = 'Server'
        asset_repo.get_by_id.return_value = asset

        mock_request = Mock()
        mock_request.id = 100
        mock_request.to_dict.return_value = {'id': 100}
        factory.create_request.return_value = mock_request

        notification_service.notify_by_role.return_value = {'success': True}

        service.create_request(
            request_type='electrical',
            submitter_id=1,
            asset_id=10,
            title='Fix',
            description='Desc',
            priority='high',
            voltage='220V'  # Type-specific field
        )

        # Verify factory was called with correct parameters
        factory.create_request.assert_called_once()
        call_kwargs = factory.create_request.call_args[1]
        assert call_kwargs['request_type'] == RequestType.ELECTRICAL
        assert call_kwargs['title'] == 'Fix'
        assert call_kwargs['submitter_id'] == 1
        assert call_kwargs['asset_id'] == 10
        assert call_kwargs['priority'] == RequestPriority.HIGH
        assert call_kwargs['voltage'] == '220V'


class TestAssignRequest:
    """Test request assignment functionality."""

    def test_assign_request_success(self):
        """Test successful request assignment."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        # Mock admin
        admin = Mock()
        admin.id = 1
        admin.email = 'admin@example.com'
        admin.is_admin = True
        user_repo.get_by_id.side_effect = lambda uid: admin if uid == 1 else technician

        # Mock technician
        technician = Mock()
        technician.id = 2
        technician.email = 'tech@example.com'
        technician.full_name = 'Tech User'
        technician.is_technician = True
        technician.is_active = True

        # Mock request
        request = Mock()
        request.id = 100
        request.status = RequestStatus.SUBMITTED
        request.asset_id = 10
        request.assign_to = Mock()
        request_repo.get_by_id.return_value = request

        # Mock updated request
        updated_request = Mock()
        updated_request.id = 100
        updated_request.to_dict.return_value = {'id': 100, 'status': 'assigned'}
        request_repo.update.return_value = updated_request

        # Mock asset
        asset = Mock()
        asset.id = 10
        asset.name = 'Server A'
        asset.status = AssetStatus.ACTIVE
        asset_repo.get_by_id.return_value = asset

        # Mock notification success
        notification_service.notify_user.return_value = {'success': True}

        result = service.assign_request(
            request_id=100,
            technician_id=2,
            assigned_by_user_id=1
        )

        assert result['success'] is True
        assert 'assigned to Tech User' in result['message']

        # Verify assignment happened
        request.assign_to.assert_called_once_with(2)

        # Verify asset status updated
        asset_repo.mark_asset_under_repair.assert_called_once_with(10)

        # Verify technician notified
        notification_service.notify_user.assert_called_once()

    def test_assign_request_only_admin_can_assign(self):
        """Test business rule: only admins can assign requests."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        # Non-admin user
        non_admin = Mock()
        non_admin.id = 1
        non_admin.is_admin = False
        user_repo.get_by_id.return_value = non_admin

        result = service.assign_request(
            request_id=100,
            technician_id=2,
            assigned_by_user_id=1
        )

        assert result['success'] is False
        assert 'Only administrators can assign' in result['error']

    def test_assign_request_validates_request_exists(self):
        """Test assignment fails when request doesn't exist."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        admin = Mock()
        admin.is_admin = True
        user_repo.get_by_id.return_value = admin

        # Request doesn't exist
        request_repo.get_by_id.return_value = None

        result = service.assign_request(
            request_id=999,
            technician_id=2,
            assigned_by_user_id=1
        )

        assert result['success'] is False
        assert 'Request not found' in result['error']

    def test_assign_request_validates_assignable_state(self):
        """Test business rule: request must be in assignable state."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        admin = Mock()
        admin.is_admin = True
        user_repo.get_by_id.return_value = admin

        # Request in non-assignable state (e.g., completed)
        request = Mock()
        request.status = RequestStatus.COMPLETED
        request_repo.get_by_id.return_value = request

        result = service.assign_request(
            request_id=100,
            technician_id=2,
            assigned_by_user_id=1
        )

        assert result['success'] is False
        assert 'Cannot assign request' in result['error']

    def test_assign_request_validates_technician_exists(self):
        """Test business rule: technician must exist."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        admin = Mock()
        admin.is_admin = True

        request = Mock()
        request.status = RequestStatus.SUBMITTED

        user_repo.get_by_id.side_effect = lambda uid: admin if uid == 1 else None
        request_repo.get_by_id.return_value = request

        result = service.assign_request(
            request_id=100,
            technician_id=999,
            assigned_by_user_id=1
        )

        assert result['success'] is False
        assert 'Technician not found' in result['error']

    def test_assign_request_validates_technician_role(self):
        """Test business rule: assigned user must be a technician."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        admin = Mock()
        admin.is_admin = True

        # User is not a technician
        non_tech = Mock()
        non_tech.id = 2
        non_tech.is_technician = False

        request = Mock()
        request.status = RequestStatus.SUBMITTED

        user_repo.get_by_id.side_effect = lambda uid: admin if uid == 1 else non_tech
        request_repo.get_by_id.return_value = request

        result = service.assign_request(
            request_id=100,
            technician_id=2,
            assigned_by_user_id=1
        )

        assert result['success'] is False
        assert 'User is not a technician' in result['error']

    def test_assign_request_validates_technician_active(self):
        """Test business rule: technician must be active."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        admin = Mock()
        admin.is_admin = True

        # Technician is inactive
        tech = Mock()
        tech.id = 2
        tech.is_technician = True
        tech.is_active = False

        request = Mock()
        request.status = RequestStatus.SUBMITTED

        user_repo.get_by_id.side_effect = lambda uid: admin if uid == 1 else tech
        request_repo.get_by_id.return_value = request

        result = service.assign_request(
            request_id=100,
            technician_id=2,
            assigned_by_user_id=1
        )

        assert result['success'] is False
        assert 'Technician account is not active' in result['error']

    def test_assign_request_updates_asset_status(self):
        """Test business rule: asset status updated to IN_REPAIR."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        admin = Mock()
        admin.is_admin = True
        admin.email = 'admin@example.com'

        tech = Mock()
        tech.id = 2
        tech.is_technician = True
        tech.is_active = True
        tech.email = 'tech@example.com'
        tech.full_name = 'Tech'

        user_repo.get_by_id.side_effect = lambda uid: admin if uid == 1 else tech

        request = Mock()
        request.status = RequestStatus.SUBMITTED
        request.asset_id = 10
        request.assign_to = Mock()
        request_repo.get_by_id.return_value = request

        updated_request = Mock()
        updated_request.to_dict.return_value = {}
        request_repo.update.return_value = updated_request

        asset = Mock()
        asset.id = 10
        asset.name = 'Server'
        asset.status = AssetStatus.ACTIVE
        asset_repo.get_by_id.return_value = asset

        notification_service.notify_user.return_value = {'success': True}

        service.assign_request(
            request_id=100,
            technician_id=2,
            assigned_by_user_id=1
        )

        # Verify asset marked under repair
        asset_repo.mark_asset_under_repair.assert_called_once_with(10)


class TestStartWork:
    """Test starting work on request."""

    def test_start_work_success(self):
        """Test successful work start."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        request = Mock()
        request.id = 100
        request.title = 'Fix Server'
        request.assigned_technician_id = 2
        request.submitter_id = 1
        request.start_work = Mock()
        request_repo.get_by_id.return_value = request

        updated_request = Mock()
        updated_request.to_dict.return_value = {'id': 100, 'status': 'in_progress'}
        request_repo.update.return_value = updated_request

        notification_service.notify_user.return_value = {'success': True}

        result = service.start_work(
            request_id=100,
            technician_id=2
        )

        assert result['success'] is True
        assert 'Work started' in result['message']

        # Verify work started
        request.start_work.assert_called_once()

        # Verify submitter notified
        notification_service.notify_user.assert_called_once()
        call_args = notification_service.notify_user.call_args[1]
        assert call_args['user_id'] == 1

    def test_start_work_only_assigned_technician(self):
        """Test business rule: only assigned technician can start work."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        request = Mock()
        request.assigned_technician_id = 2
        request_repo.get_by_id.return_value = request

        # Different technician tries to start
        result = service.start_work(
            request_id=100,
            technician_id=3
        )

        assert result['success'] is False
        assert 'Only the assigned technician can start' in result['error']

    def test_start_work_request_not_found(self):
        """Test start work fails when request doesn't exist."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        request_repo.get_by_id.return_value = None

        result = service.start_work(
            request_id=999,
            technician_id=2
        )

        assert result['success'] is False
        assert 'Request not found' in result['error']


class TestCompleteRequest:
    """Test request completion functionality."""

    def test_complete_request_success(self):
        """Test successful request completion."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        request = Mock()
        request.id = 100
        request.title = 'Fix Server'
        request.assigned_technician_id = 2
        request.submitter_id = 1
        request.asset_id = 10
        request.complete = Mock()
        request_repo.get_by_id.return_value = request

        updated_request = Mock()
        updated_request.to_dict.return_value = {'id': 100, 'status': 'completed'}
        request_repo.update.return_value = updated_request

        asset = Mock()
        asset.id = 10
        asset.status = AssetStatus.IN_REPAIR
        asset_repo.get_by_id.return_value = asset

        notification_service.notify_user.return_value = {'success': True}
        notification_service.notify_by_role.return_value = {'success': True}

        result = service.complete_request(
            request_id=100,
            technician_id=2,
            completion_notes='Fixed successfully',
            actual_hours=3.5
        )

        assert result['success'] is True
        assert 'completed successfully' in result['message']

        # Verify completion
        request.complete.assert_called_once_with('Fixed successfully', 3.5)

        # Verify asset marked as repaired
        asset_repo.mark_asset_repaired.assert_called_once_with(10)

        # Verify notifications sent (submitter + admins)
        assert notification_service.notify_user.call_count == 1
        assert notification_service.notify_by_role.call_count == 1

    def test_complete_request_only_assigned_technician(self):
        """Test business rule: only assigned technician can complete."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        request = Mock()
        request.assigned_technician_id = 2
        request_repo.get_by_id.return_value = request

        # Different technician tries to complete
        result = service.complete_request(
            request_id=100,
            technician_id=3,
            completion_notes='Done'
        )

        assert result['success'] is False
        assert 'Only the assigned technician can complete' in result['error']

    def test_complete_request_requires_completion_notes(self):
        """Test business rule: completion notes are required."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        request = Mock()
        request.assigned_technician_id = 2
        request_repo.get_by_id.return_value = request

        # Empty completion notes
        result = service.complete_request(
            request_id=100,
            technician_id=2,
            completion_notes=''
        )

        assert result['success'] is False
        assert 'Completion notes are required' in result['error']

        # Whitespace-only completion notes
        result = service.complete_request(
            request_id=100,
            technician_id=2,
            completion_notes='   '
        )

        assert result['success'] is False
        assert 'Completion notes are required' in result['error']

    def test_complete_request_marks_asset_repaired(self):
        """Test business rule: asset marked as repaired when request completed."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        request = Mock()
        request.assigned_technician_id = 2
        request.submitter_id = 1
        request.asset_id = 10
        request.complete = Mock()
        request_repo.get_by_id.return_value = request

        updated_request = Mock()
        updated_request.to_dict.return_value = {}
        request_repo.update.return_value = updated_request

        # Asset is in repair
        asset = Mock()
        asset.id = 10
        asset.status = AssetStatus.IN_REPAIR
        asset_repo.get_by_id.return_value = asset

        notification_service.notify_user.return_value = {'success': True}
        notification_service.notify_by_role.return_value = {'success': True}

        service.complete_request(
            request_id=100,
            technician_id=2,
            completion_notes='Fixed'
        )

        # Verify asset marked as repaired
        asset_repo.mark_asset_repaired.assert_called_once_with(10)

    def test_complete_request_notifies_submitter_and_admins(self):
        """Test business rule: submitter and admins notified on completion."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        request = Mock()
        request.id = 100
        request.title = 'Fix Server'
        request.assigned_technician_id = 2
        request.submitter_id = 1
        request.asset_id = 10
        request.complete = Mock()
        request_repo.get_by_id.return_value = request

        updated_request = Mock()
        updated_request.to_dict.return_value = {}
        request_repo.update.return_value = updated_request

        asset = Mock()
        asset.status = AssetStatus.IN_REPAIR
        asset_repo.get_by_id.return_value = asset

        notification_service.notify_user.return_value = {'success': True}
        notification_service.notify_by_role.return_value = {'success': True}

        service.complete_request(
            request_id=100,
            technician_id=2,
            completion_notes='All fixed',
            actual_hours=2.0
        )

        # Verify submitter notified
        notification_service.notify_user.assert_called_once()
        user_call = notification_service.notify_user.call_args[1]
        assert user_call['user_id'] == 1
        assert 'Completed' in user_call['subject']

        # Verify admins notified
        notification_service.notify_by_role.assert_called_once()
        role_call = notification_service.notify_by_role.call_args[1]
        assert role_call['role'] == 'admin'


class TestGetTechnicianWorkload:
    """Test technician workload retrieval."""

    def test_get_technician_workload_success(self):
        """Test successful workload retrieval."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        mock_workload = {
            'technician_id': 2,
            'active_requests': 5,
            'completed_requests': 20,
            'total_hours': 80.5
        }

        request_repo.get_technician_workload.return_value = mock_workload

        result = service.get_technician_workload(technician_id=2)

        assert result['success'] is True
        assert result['data']['technician_id'] == 2
        assert result['data']['active_requests'] == 5


class TestGetUnassignedRequests:
    """Test unassigned requests retrieval."""

    def test_get_unassigned_requests_success(self):
        """Test successful retrieval of unassigned requests."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        req1 = Mock()
        req1.to_dict.return_value = {'id': 1, 'status': 'submitted'}

        req2 = Mock()
        req2.to_dict.return_value = {'id': 2, 'status': 'submitted'}

        request_repo.get_unassigned_requests.return_value = [req1, req2]

        result = service.get_unassigned_requests()

        assert result['success'] is True
        assert len(result['data']) == 2
        assert 'Found 2 unassigned requests' in result['message']


class TestMultiRepositoryOrchestration:
    """Test service orchestrates multiple repositories."""

    @patch('app.services.maintenance_service.db')
    def test_create_request_orchestrates_all_repositories(self, mock_db):
        """Test create_request coordinates user, asset, and request repositories."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        submitter = Mock()
        submitter.id = 1
        submitter.email = 'client@example.com'
        submitter.is_active = True

        asset = Mock()
        asset.id = 10
        asset.name = 'Server'

        mock_request = Mock()
        mock_request.id = 100
        mock_request.to_dict.return_value = {}

        user_repo.get_by_id.return_value = submitter
        asset_repo.get_by_id.return_value = asset
        factory.create_request.return_value = mock_request
        notification_service.notify_by_role.return_value = {'success': True}

        service.create_request(
            request_type='electrical',
            submitter_id=1,
            asset_id=10,
            title='Fix',
            description='Desc',
            priority='medium'
        )

        # Verify all repositories were used
        user_repo.get_by_id.assert_called_once()
        asset_repo.get_by_id.assert_called_once()
        factory.create_request.assert_called_once()
        notification_service.notify_by_role.assert_called_once()

    def test_assign_request_orchestrates_user_asset_request(self):
        """Test assign_request coordinates multiple entities."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        admin = Mock()
        admin.is_admin = True
        admin.email = 'admin@example.com'

        tech = Mock()
        tech.id = 2
        tech.is_technician = True
        tech.is_active = True
        tech.full_name = 'Tech'

        request = Mock()
        request.status = RequestStatus.SUBMITTED
        request.asset_id = 10
        request.assign_to = Mock()

        updated_request = Mock()
        updated_request.to_dict.return_value = {}

        asset = Mock()
        asset.id = 10
        asset.name = 'Server'
        asset.status = AssetStatus.ACTIVE

        user_repo.get_by_id.side_effect = lambda uid: admin if uid == 1 else tech
        request_repo.get_by_id.return_value = request
        request_repo.update.return_value = updated_request
        asset_repo.get_by_id.return_value = asset
        notification_service.notify_user.return_value = {'success': True}

        service.assign_request(
            request_id=100,
            technician_id=2,
            assigned_by_user_id=1
        )

        # Verify coordination across repositories
        assert user_repo.get_by_id.call_count >= 2  # Admin and technician
        request_repo.get_by_id.assert_called_once()
        request_repo.update.assert_called_once()
        asset_repo.get_by_id.assert_called_once()
        asset_repo.mark_asset_under_repair.assert_called_once()
        notification_service.notify_user.assert_called_once()


class TestBusinessRuleEnforcement:
    """Test comprehensive business rule enforcement."""

    def test_authorization_rules_enforced(self):
        """Test authorization rules are consistently enforced."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        # Only admins can assign
        non_admin = Mock()
        non_admin.is_admin = False
        user_repo.get_by_id.return_value = non_admin

        result = service.assign_request(100, 2, 1)
        assert result['success'] is False
        assert 'Only administrators' in result['error']

    def test_state_transition_rules_enforced(self):
        """Test request state transitions are validated."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        admin = Mock()
        admin.is_admin = True
        user_repo.get_by_id.return_value = admin

        # Cannot assign completed request
        request = Mock()
        request.status = RequestStatus.COMPLETED
        request_repo.get_by_id.return_value = request

        result = service.assign_request(100, 2, 1)
        assert result['success'] is False
        assert 'Cannot assign request' in result['error']

    def test_cross_entity_updates_enforced(self):
        """Test updates across entities are consistent."""
        request_repo = Mock()
        user_repo = Mock()
        asset_repo = Mock()
        notification_service = Mock()
        factory = Mock()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        # When request assigned, asset should be marked IN_REPAIR
        admin = Mock()
        admin.is_admin = True
        admin.email = 'admin@example.com'

        tech = Mock()
        tech.is_technician = True
        tech.is_active = True
        tech.full_name = 'Tech'

        request = Mock()
        request.status = RequestStatus.SUBMITTED
        request.asset_id = 10
        request.assign_to = Mock()

        updated_request = Mock()
        updated_request.to_dict.return_value = {}

        asset = Mock()
        asset.id = 10
        asset.name = 'Server'
        asset.status = AssetStatus.ACTIVE

        user_repo.get_by_id.side_effect = lambda uid: admin if uid == 1 else tech
        request_repo.get_by_id.return_value = request
        request_repo.update.return_value = updated_request
        asset_repo.get_by_id.return_value = asset
        notification_service.notify_user.return_value = {'success': True}

        service.assign_request(100, 2, 1)

        # Asset status should be updated
        asset_repo.mark_asset_under_repair.assert_called_once_with(10)
