"""
Integration Tests for Event-Driven Architecture

Tests end-to-end event flow:
Service → EventBus → Observers

Verifies that:
- Services publish events when actions occur
- EventBus delivers events to subscribed observers
- All observers handle events correctly
- Metrics are tracked accurately
"""

import pytest
from app.patterns.event_bus import EventBus
from app.events.event_types import EventTypes
from app.observers import (
    NotificationObserver,
    LoggingObserver,
    MetricsObserver,
    AssetStatusObserver
)
from app.services.maintenance_service import MaintenanceService
from app.services.asset_service import AssetService
from app.repositories import RequestRepository, UserRepository, AssetRepository
from app.services.notification_service import NotificationService
from app.patterns.factory import MaintenanceRequestFactory
from app.models import (
    User, Asset, MaintenanceRequest,
    UserRole, AssetCondition, AssetStatus,
    RequestType, RequestPriority, RequestStatus
)


@pytest.fixture
def event_bus():
    """Get fresh EventBus instance for each test."""
    bus = EventBus()
    # Clear any existing subscriptions
    bus._observers = {}
    bus._event_history = []
    return bus


@pytest.fixture
def observers(event_bus):
    """Create and register all observers."""
    notification_obs = NotificationObserver(notification_service=None)
    logging_obs = LoggingObserver()
    metrics_obs = MetricsObserver()
    asset_status_obs = AssetStatusObserver()

    # Subscribe to relevant events
    event_bus.subscribe(EventTypes.REQUEST_CREATED, notification_obs)
    event_bus.subscribe(EventTypes.REQUEST_CREATED, logging_obs)
    event_bus.subscribe(EventTypes.REQUEST_CREATED, metrics_obs)

    event_bus.subscribe(EventTypes.REQUEST_ASSIGNED, notification_obs)
    event_bus.subscribe(EventTypes.REQUEST_ASSIGNED, logging_obs)
    event_bus.subscribe(EventTypes.REQUEST_ASSIGNED, metrics_obs)
    event_bus.subscribe(EventTypes.REQUEST_ASSIGNED, asset_status_obs)

    event_bus.subscribe(EventTypes.REQUEST_STARTED, notification_obs)
    event_bus.subscribe(EventTypes.REQUEST_STARTED, logging_obs)

    event_bus.subscribe(EventTypes.REQUEST_COMPLETED, notification_obs)
    event_bus.subscribe(EventTypes.REQUEST_COMPLETED, logging_obs)
    event_bus.subscribe(EventTypes.REQUEST_COMPLETED, metrics_obs)
    event_bus.subscribe(EventTypes.REQUEST_COMPLETED, asset_status_obs)

    event_bus.subscribe(EventTypes.ASSET_CONDITION_CHANGED, logging_obs)
    event_bus.subscribe(EventTypes.ASSET_CONDITION_CHANGED, metrics_obs)
    event_bus.subscribe(EventTypes.ASSET_CONDITION_CHANGED, asset_status_obs)

    return {
        'notification': notification_obs,
        'logging': logging_obs,
        'metrics': metrics_obs,
        'asset_status': asset_status_obs
    }


@pytest.fixture
def sample_request(db_session, sample_user, sample_asset):
    """Create a sample maintenance request."""
    from app.database import db
    request = MaintenanceRequest(
        type=RequestType.ELECTRICAL,
        title="Test Request",
        description="Test description",
        submitter_id=sample_user.id,
        asset_id=sample_asset.id,
        priority=RequestPriority.HIGH,
        status=RequestStatus.SUBMITTED
    )
    db.session.add(request)
    db.session.commit()
    db.session.refresh(request)
    return request


@pytest.fixture
def sample_assigned_request(db_session, sample_user, sample_asset, sample_technician):
    """Create a sample assigned maintenance request."""
    from app.database import db
    request = MaintenanceRequest(
        type=RequestType.ELECTRICAL,
        title="Test Request",
        description="Test description",
        submitter_id=sample_user.id,
        asset_id=sample_asset.id,
        priority=RequestPriority.HIGH,
        status=RequestStatus.ASSIGNED,
        assigned_technician_id=sample_technician.id
    )
    db.session.add(request)
    db.session.commit()
    db.session.refresh(request)
    return request


class TestRequestLifecycleEventFlow:
    """Test complete request lifecycle with event propagation."""

    def test_create_request_publishes_event(self, client, sample_user, sample_asset, observers):
        """Test that creating a request publishes REQUEST_CREATED event."""
        event_bus = EventBus()
        metrics_obs = observers['metrics']

        # Create maintenance service
        request_repo = RequestRepository()
        user_repo = UserRepository()
        asset_repo = AssetRepository()
        notification_service = NotificationService(user_repository=user_repo)
        factory = MaintenanceRequestFactory()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        # Get initial metrics
        initial_metrics = metrics_obs.get_metrics()
        initial_count = initial_metrics['requests_created']

        # Create request
        result = service.create_request(
            request_type='electrical',
            submitter_id=sample_user.id,
            asset_id=sample_asset.id,
            title='Test Request',
            description='Test description',
            priority='high'
        )

        assert result['success'] is True

        # Verify event was published and observers notified
        metrics = metrics_obs.get_metrics()
        assert metrics['requests_created'] == initial_count + 1
        assert metrics['requests_by_type']['electrical'] == 1

        # Verify event in history
        history = event_bus.get_history(event_type=EventTypes.REQUEST_CREATED, limit=1)
        assert len(history) > 0
        assert history[0].event_type == EventTypes.REQUEST_CREATED
        assert history[0].data['type'] == 'electrical'

    def test_assign_request_publishes_event(self, client, sample_request,
                                           sample_user, sample_technician, observers):
        """Test that assigning a request publishes REQUEST_ASSIGNED event."""
        event_bus = EventBus()
        metrics_obs = observers['metrics']

        request_repo = RequestRepository()
        user_repo = UserRepository()
        asset_repo = AssetRepository()
        notification_service = NotificationService(user_repository=user_repo)
        factory = MaintenanceRequestFactory()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        # Get initial metrics
        initial_workload = metrics_obs.get_metrics()['technician_workload'].copy()

        # Assign request
        result = service.assign_request(
            request_id=sample_request.id,
            technician_id=sample_technician.id,
            assigned_by_user_id=sample_user.id
        )

        assert result['success'] is True

        # Verify metrics updated
        metrics = metrics_obs.get_metrics()
        assert metrics['technician_workload'][sample_technician.id] == \
               initial_workload.get(sample_technician.id, 0) + 1

        # Verify event in history
        history = event_bus.get_history(event_type=EventTypes.REQUEST_ASSIGNED, limit=1)
        assert len(history) > 0
        assert history[0].data['technician_id'] == sample_technician.id

    def test_complete_request_publishes_event(self, client, sample_assigned_request,
                                             sample_technician, observers):
        """Test that completing a request publishes REQUEST_COMPLETED event."""
        event_bus = EventBus()
        metrics_obs = observers['metrics']

        request_repo = RequestRepository()
        user_repo = UserRepository()
        asset_repo = AssetRepository()
        notification_service = NotificationService(user_repository=user_repo)
        factory = MaintenanceRequestFactory()

        service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        # Start work first
        service.start_work(
            request_id=sample_assigned_request.id,
            technician_id=sample_technician.id
        )

        # Get initial completion count
        initial_completed = metrics_obs.get_metrics()['requests_completed']

        # Complete request
        result = service.complete_request(
            request_id=sample_assigned_request.id,
            technician_id=sample_technician.id,
            completion_notes="Fixed the issue",
            actual_hours=2.5
        )

        assert result['success'] is True

        # Verify metrics updated
        metrics = metrics_obs.get_metrics()
        assert metrics['requests_completed'] == initial_completed + 1

        # Verify event in history
        history = event_bus.get_history(event_type=EventTypes.REQUEST_COMPLETED, limit=1)
        assert len(history) > 0
        assert history[0].data['completion_notes'] == "Fixed the issue"
        assert history[0].data['actual_hours'] == 2.5


class TestAssetEventFlow:
    """Test asset-related event flow."""

    def test_update_condition_publishes_event(self, client, sample_asset, observers):
        """Test that updating asset condition publishes ASSET_CONDITION_CHANGED event."""
        event_bus = EventBus()
        metrics_obs = observers['metrics']

        asset_repo = AssetRepository()
        service = AssetService(asset_repo)

        # Get initial condition change count
        initial_changes = metrics_obs.get_metrics()['condition_changes']

        # Update condition
        result = service.update_asset_condition(
            asset_id=sample_asset.id,
            new_condition='poor'
        )

        assert result['success'] is True

        # Verify metrics updated
        metrics = metrics_obs.get_metrics()
        assert metrics['condition_changes'] == initial_changes + 1

        # Verify event in history
        history = event_bus.get_history(event_type=EventTypes.ASSET_CONDITION_CHANGED, limit=1)
        assert len(history) > 0
        assert history[0].data['new_condition'] == 'poor'
        assert history[0].data['asset_id'] == sample_asset.id


class TestMultipleObserversReceiveEvents:
    """Test that multiple observers all receive the same events."""

    def test_all_observers_notified(self, event_bus, observers):
        """Test that all subscribed observers receive published events."""
        metrics_obs = observers['metrics']

        # Publish a REQUEST_CREATED event
        event_bus.publish(
            EventTypes.REQUEST_CREATED,
            {
                'request_id': 999,
                'type': 'plumbing',
                'priority': 'medium'
            },
            source='TestCase'
        )

        # Verify metrics observer received it
        metrics = metrics_obs.get_metrics()
        assert 'plumbing' in metrics['requests_by_type']

        # Verify event in history
        history = event_bus.get_history(event_type=EventTypes.REQUEST_CREATED, limit=1)
        assert len(history) > 0
        assert history[0].data['type'] == 'plumbing'

    def test_multiple_events_in_sequence(self, event_bus, observers):
        """Test that observers correctly handle multiple sequential events."""
        metrics_obs = observers['metrics']

        # Publish multiple events
        event_bus.publish(EventTypes.REQUEST_CREATED, {'type': 'electrical'})
        event_bus.publish(EventTypes.REQUEST_CREATED, {'type': 'plumbing'})
        event_bus.publish(EventTypes.REQUEST_CREATED, {'type': 'electrical'})
        event_bus.publish(EventTypes.REQUEST_ASSIGNED, {'technician_id': 5})
        event_bus.publish(EventTypes.REQUEST_COMPLETED, {'request_id': 1})

        # Verify all events tracked
        metrics = metrics_obs.get_metrics()
        assert metrics['requests_created'] == 3
        assert metrics['requests_by_type']['electrical'] == 2
        assert metrics['requests_by_type']['plumbing'] == 1
        assert metrics['technician_workload'][5] == 1
        assert metrics['requests_completed'] == 1


class TestEventBusHistory:
    """Test EventBus history and query functionality."""

    def test_event_history_recorded(self, event_bus):
        """Test that events are recorded in history."""
        event_bus.publish(EventTypes.REQUEST_CREATED, {'request_id': 1})
        event_bus.publish(EventTypes.REQUEST_ASSIGNED, {'request_id': 1, 'technician_id': 5})

        history = event_bus.get_history(limit=10)
        assert len(history) >= 2

    def test_history_filtering_by_type(self, event_bus):
        """Test filtering history by event type."""
        event_bus.publish(EventTypes.REQUEST_CREATED, {'request_id': 1})
        event_bus.publish(EventTypes.REQUEST_CREATED, {'request_id': 2})
        event_bus.publish(EventTypes.REQUEST_ASSIGNED, {'request_id': 1})

        created_history = event_bus.get_history(event_type=EventTypes.REQUEST_CREATED, limit=10)
        assert all(e.event_type == EventTypes.REQUEST_CREATED for e in created_history)

    def test_history_filtering_by_source(self, event_bus):
        """Test filtering history by source."""
        event_bus.publish(EventTypes.REQUEST_CREATED, {'id': 1}, source='ServiceA')
        event_bus.publish(EventTypes.REQUEST_CREATED, {'id': 2}, source='ServiceB')
        event_bus.publish(EventTypes.REQUEST_CREATED, {'id': 3}, source='ServiceA')

        service_a_history = event_bus.get_history(source='ServiceA', limit=10)
        assert all(e.source == 'ServiceA' for e in service_a_history)


class TestObserverIndependence:
    """Test that observer failures don't affect others."""

    def test_failed_observer_doesnt_stop_others(self, event_bus):
        """Test that one failing observer doesn't prevent others from executing."""
        # Create observers
        metrics_obs = MetricsObserver()
        logging_obs = LoggingObserver()

        # Create a failing observer
        class FailingObserver(NotificationObserver):
            def update(self, event):
                raise RuntimeError("Intentional failure")

        failing_obs = FailingObserver(notification_service=None)

        # Subscribe all observers
        event_bus.subscribe(EventTypes.REQUEST_CREATED, failing_obs)
        event_bus.subscribe(EventTypes.REQUEST_CREATED, metrics_obs)
        event_bus.subscribe(EventTypes.REQUEST_CREATED, logging_obs)

        # Publish event - should not raise exception
        event_bus.publish(EventTypes.REQUEST_CREATED, {'type': 'electrical'})

        # Verify metrics observer still received it
        metrics = metrics_obs.get_metrics()
        assert metrics['requests_created'] == 1
