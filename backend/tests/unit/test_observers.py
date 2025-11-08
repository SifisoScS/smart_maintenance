"""
Unit Tests for Concrete Observers

Tests all four observer implementations.
"""

import pytest
from app.patterns.observer import Event
from app.events.event_types import EventTypes
from app.observers import (
    NotificationObserver,
    LoggingObserver,
    MetricsObserver,
    AssetStatusObserver
)


class TestNotificationObserver:
    """Test NotificationObserver."""

    def test_observer_name(self):
        """Test observer name property."""
        observer = NotificationObserver(notification_service=None)
        assert observer.name == "NotificationObserver"

    def test_handles_request_created(self):
        """Test handling REQUEST_CREATED event."""
        observer = NotificationObserver(notification_service=None)
        event = Event(
            EventTypes.REQUEST_CREATED,
            {'request_id': 1, 'type': 'electrical', 'priority': 'high'},
            source='TestService'
        )

        # Should not raise exception
        observer.update(event)

    def test_handles_request_assigned(self):
        """Test handling REQUEST_ASSIGNED event."""
        observer = NotificationObserver(notification_service=None)
        event = Event(
            EventTypes.REQUEST_ASSIGNED,
            {'request_id': 1, 'technician_id': 5},
            source='TestService'
        )

        observer.update(event)

    def test_handles_unknown_event(self):
        """Test handling unknown event type."""
        observer = NotificationObserver(notification_service=None)
        event = Event('UNKNOWN_EVENT', {})

        # Should handle gracefully
        observer.update(event)


class TestLoggingObserver:
    """Test LoggingObserver."""

    def test_observer_name(self):
        """Test observer name property."""
        observer = LoggingObserver()
        assert observer.name == "LoggingObserver"

    def test_logs_event(self):
        """Test that event is logged."""
        observer = LoggingObserver()
        event = Event(
            EventTypes.REQUEST_CREATED,
            {'request_id': 1, 'user_id': 5},
            source='MaintenanceService'
        )

        # Should not raise exception
        observer.update(event)

    def test_formats_log_entry(self):
        """Test log entry formatting."""
        observer = LoggingObserver()
        event = Event(
            'TEST_EVENT',
            {'key1': 'value1', 'key2': 'value2'},
            source='TestSource'
        )

        log_entry = observer._format_log_entry(event)

        assert 'TEST_EVENT' in log_entry
        assert 'TestSource' in log_entry
        assert 'key1=value1' in log_entry
        assert 'key2=value2' in log_entry

    def test_handles_event_without_source(self):
        """Test logging event without source."""
        observer = LoggingObserver()
        event = Event('TEST_EVENT', {'data': 'value'})

        log_entry = observer._format_log_entry(event)
        assert 'Unknown' in log_entry


class TestMetricsObserver:
    """Test MetricsObserver."""

    def test_observer_name(self):
        """Test observer name property."""
        observer = MetricsObserver()
        assert observer.name == "MetricsObserver"

    def test_tracks_request_created(self):
        """Test tracking request creation."""
        observer = MetricsObserver()

        event = Event(
            EventTypes.REQUEST_CREATED,
            {'request_id': 1, 'type': 'electrical'},
            source='Service'
        )

        observer.update(event)

        metrics = observer.get_metrics()
        assert metrics['requests_created'] == 1
        assert metrics['requests_by_type']['electrical'] == 1

    def test_tracks_multiple_request_types(self):
        """Test tracking multiple request types."""
        observer = MetricsObserver()

        observer.update(Event(EventTypes.REQUEST_CREATED, {'type': 'electrical'}))
        observer.update(Event(EventTypes.REQUEST_CREATED, {'type': 'plumbing'}))
        observer.update(Event(EventTypes.REQUEST_CREATED, {'type': 'electrical'}))

        metrics = observer.get_metrics()
        assert metrics['requests_created'] == 3
        assert metrics['requests_by_type']['electrical'] == 2
        assert metrics['requests_by_type']['plumbing'] == 1

    def test_tracks_request_completed(self):
        """Test tracking request completion."""
        observer = MetricsObserver()

        # Create then complete
        observer.update(Event(EventTypes.REQUEST_CREATED, {'type': 'electrical'}))
        observer.update(Event(EventTypes.REQUEST_COMPLETED, {'request_id': 1}))

        metrics = observer.get_metrics()
        assert metrics['requests_completed'] == 1

    def test_tracks_technician_workload(self):
        """Test tracking technician workload."""
        observer = MetricsObserver()

        observer.update(Event(EventTypes.REQUEST_ASSIGNED, {'technician_id': 5}))
        observer.update(Event(EventTypes.REQUEST_ASSIGNED, {'technician_id': 5}))
        observer.update(Event(EventTypes.REQUEST_ASSIGNED, {'technician_id': 10}))

        metrics = observer.get_metrics()
        assert metrics['technician_workload'][5] == 2
        assert metrics['technician_workload'][10] == 1

    def test_tracks_asset_created(self):
        """Test tracking asset creation."""
        observer = MetricsObserver()

        observer.update(Event(EventTypes.ASSET_CREATED, {'asset_id': 1}))
        observer.update(Event(EventTypes.ASSET_CREATED, {'asset_id': 2}))

        metrics = observer.get_metrics()
        assert metrics['assets_created'] == 2

    def test_tracks_condition_changes(self):
        """Test tracking condition changes."""
        observer = MetricsObserver()

        observer.update(Event(EventTypes.ASSET_CONDITION_CHANGED, {'asset_id': 1}))

        metrics = observer.get_metrics()
        assert metrics['condition_changes'] == 1

    def test_get_metrics_returns_copy(self):
        """Test that get_metrics returns a copy."""
        observer = MetricsObserver()

        metrics1 = observer.get_metrics()
        metrics1['requests_created'] = 999

        metrics2 = observer.get_metrics()
        assert metrics2['requests_created'] == 0

    def test_reset_metrics(self):
        """Test resetting metrics."""
        observer = MetricsObserver()

        observer.update(Event(EventTypes.REQUEST_CREATED, {'type': 'electrical'}))
        observer.update(Event(EventTypes.ASSET_CREATED, {'asset_id': 1}))

        observer.reset_metrics()

        metrics = observer.get_metrics()
        assert metrics['requests_created'] == 0
        assert metrics['assets_created'] == 0


class TestAssetStatusObserver:
    """Test AssetStatusObserver."""

    def test_observer_name(self):
        """Test observer name property."""
        observer = AssetStatusObserver()
        assert observer.name == "AssetStatusObserver"

    def test_handles_request_assigned(self):
        """Test handling request assignment."""
        observer = AssetStatusObserver()

        event = Event(
            EventTypes.REQUEST_ASSIGNED,
            {'asset_id': 1, 'request_id': 10, 'technician_id': 5}
        )

        # Should not raise exception
        observer.update(event)

    def test_handles_request_completed(self):
        """Test handling request completion."""
        observer = AssetStatusObserver()

        event = Event(
            EventTypes.REQUEST_COMPLETED,
            {'asset_id': 1, 'request_id': 10}
        )

        observer.update(event)

    def test_handles_condition_change(self):
        """Test handling condition change."""
        observer = AssetStatusObserver()

        event = Event(
            EventTypes.ASSET_CONDITION_CHANGED,
            {'asset_id': 1, 'new_condition': 'poor', 'old_condition': 'good'}
        )

        observer.update(event)

    def test_handles_missing_asset_id(self):
        """Test handling event without asset_id."""
        observer = AssetStatusObserver()

        event = Event(EventTypes.REQUEST_ASSIGNED, {'request_id': 10})

        # Should handle gracefully
        observer.update(event)


class TestObserverIntegration:
    """Integration tests for observers."""

    def test_all_observers_handle_same_event(self):
        """Test that all observers can handle the same event."""
        notification_obs = NotificationObserver(notification_service=None)
        logging_obs = LoggingObserver()
        metrics_obs = MetricsObserver()
        asset_obs = AssetStatusObserver()

        event = Event(
            EventTypes.REQUEST_CREATED,
            {'request_id': 1, 'type': 'electrical', 'asset_id': 5}
        )

        # All should handle without error
        notification_obs.update(event)
        logging_obs.update(event)
        metrics_obs.update(event)
        asset_obs.update(event)

        # Verify metrics were updated
        metrics = metrics_obs.get_metrics()
        assert metrics['requests_created'] == 1

    def test_observers_are_independent(self):
        """Test that observer failure doesn't affect others."""
        class FailingObserver(NotificationObserver):
            def update(self, event):
                raise RuntimeError("Intentional failure")

        failing_obs = FailingObserver(notification_service=None)
        metrics_obs = MetricsObserver()

        event = Event(EventTypes.REQUEST_CREATED, {'type': 'electrical'})

        # Failing observer raises exception
        with pytest.raises(RuntimeError):
            failing_obs.update(event)

        # But metrics observer works fine
        metrics_obs.update(event)
        assert metrics_obs.get_metrics()['requests_created'] == 1
