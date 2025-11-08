"""
Unit Tests for EventBus

Tests the EventBus singleton including publishing, subscribing, history, and statistics.
"""

import pytest
from datetime import datetime, timedelta
from app.patterns.event_bus import EventBus
from app.patterns.observer import Event, Observer


class MockObserver(Observer):
    """Mock observer for testing."""

    def __init__(self, observer_name: str, should_fail: bool = False):
        self._name = observer_name
        self.should_fail = should_fail
        self.events_received = []

    @property
    def name(self) -> str:
        return self._name

    def update(self, event: Event) -> None:
        """Record event or raise exception if configured to fail."""
        if self.should_fail:
            raise RuntimeError(f"{self.name} intentionally failed")
        self.events_received.append(event)


@pytest.fixture
def event_bus():
    """Provide clean EventBus instance for each test."""
    # Clear singleton instance
    if hasattr(EventBus, '_instances'):
        EventBus._instances.clear()

    bus = EventBus()
    bus.clear_history()
    bus.clear_observers()
    yield bus

    # Cleanup
    bus.clear_history()
    bus.clear_observers()


class TestEventBusSingleton:
    """Test EventBus singleton behavior."""

    def test_event_bus_is_singleton(self, event_bus):
        """Test that EventBus follows singleton pattern."""
        bus1 = EventBus()
        bus2 = EventBus()

        assert bus1 is bus2
        assert bus1 is event_bus

    def test_singleton_preserves_state(self, event_bus):
        """Test that singleton preserves state across instances."""
        observer = MockObserver('Observer1')
        event_bus.subscribe('TEST_EVENT', observer)

        # Get "new" instance
        bus2 = EventBus()

        assert bus2.get_observer_count() == 1


class TestEventBusPublish:
    """Test event publishing functionality."""

    def test_publish_creates_event(self, event_bus):
        """Test that publish creates an Event object."""
        event = event_bus.publish('TEST_EVENT', {'key': 'value'})

        assert isinstance(event, Event)
        assert event.event_type == 'TEST_EVENT'
        assert event.data == {'key': 'value'}
        assert event.source is None

    def test_publish_with_source(self, event_bus):
        """Test publishing event with source."""
        event = event_bus.publish(
            'TEST_EVENT',
            {'key': 'value'},
            source='TestService.method'
        )

        assert event.source == 'TestService.method'

    def test_publish_notifies_observers(self, event_bus):
        """Test that publishing notifies subscribed observers."""
        observer1 = MockObserver('Observer1')
        observer2 = MockObserver('Observer2')

        event_bus.subscribe('TEST_EVENT', observer1)
        event_bus.subscribe('TEST_EVENT', observer2)

        event_bus.publish('TEST_EVENT', {'data': 'value'})

        assert len(observer1.events_received) == 1
        assert len(observer2.events_received) == 1

    def test_publish_adds_to_history(self, event_bus):
        """Test that published events are added to history."""
        event_bus.publish('EVENT1', {'data': 1})
        event_bus.publish('EVENT2', {'data': 2})

        history = event_bus.get_history()

        assert len(history) == 2

    def test_publish_returns_event_with_id(self, event_bus):
        """Test that published event has unique ID."""
        event1 = event_bus.publish('TEST', {})
        event2 = event_bus.publish('TEST', {})

        assert event1.event_id != event2.event_id


class TestEventBusSubscribe:
    """Test subscription functionality."""

    def test_subscribe_attaches_observer(self, event_bus):
        """Test subscribing observer to event type."""
        observer = MockObserver('Observer1')

        event_bus.subscribe('TEST_EVENT', observer)

        assert event_bus.get_observer_count('TEST_EVENT') == 1

    def test_subscribe_multiple_observers(self, event_bus):
        """Test subscribing multiple observers to same event."""
        observer1 = MockObserver('Observer1')
        observer2 = MockObserver('Observer2')

        event_bus.subscribe('TEST_EVENT', observer1)
        event_bus.subscribe('TEST_EVENT', observer2)

        assert event_bus.get_observer_count('TEST_EVENT') == 2

    def test_unsubscribe_removes_observer(self, event_bus):
        """Test unsubscribing observer from event type."""
        observer = MockObserver('Observer1')

        event_bus.subscribe('TEST_EVENT', observer)
        event_bus.unsubscribe('TEST_EVENT', observer)

        assert event_bus.get_observer_count('TEST_EVENT') == 0


class TestEventBusHistory:
    """Test event history functionality."""

    def test_get_history_returns_all_events(self, event_bus):
        """Test getting all events from history."""
        event_bus.publish('EVENT1', {'data': 1})
        event_bus.publish('EVENT2', {'data': 2})
        event_bus.publish('EVENT3', {'data': 3})

        history = event_bus.get_history(limit=100)

        assert len(history) == 3

    def test_get_history_filtered_by_type(self, event_bus):
        """Test filtering history by event type."""
        event_bus.publish('EVENT_A', {'data': 1})
        event_bus.publish('EVENT_B', {'data': 2})
        event_bus.publish('EVENT_A', {'data': 3})

        history = event_bus.get_history(event_type='EVENT_A')

        assert len(history) == 2
        assert all(e.event_type == 'EVENT_A' for e in history)

    def test_get_history_with_limit(self, event_bus):
        """Test limiting history results."""
        for i in range(10):
            event_bus.publish('TEST', {'index': i})

        history = event_bus.get_history(limit=5)

        assert len(history) == 5

    def test_get_history_returns_newest_first(self, event_bus):
        """Test that history is returned newest first."""
        import time
        event_bus.publish('TEST', {'index': 1})
        time.sleep(0.01)  # Small delay to ensure different timestamps
        event_bus.publish('TEST', {'index': 2})
        time.sleep(0.01)
        event_bus.publish('TEST', {'index': 3})

        history = event_bus.get_history()

        assert history[0].data['index'] == 3
        assert history[1].data['index'] == 2
        assert history[2].data['index'] == 1

    def test_get_history_filtered_by_time(self, event_bus):
        """Test filtering history by timestamp."""
        import time
        event_bus.publish('TEST', {'old': True})

        time.sleep(0.01)  # Small delay to ensure cutoff is after old event

        # Events published after this should be returned
        cutoff = datetime.utcnow()

        time.sleep(0.01)
        event_bus.publish('TEST', {'new': True})

        history = event_bus.get_history(since=cutoff)

        assert len(history) == 1
        assert history[0].data.get('new') == True

    def test_get_history_filtered_by_source(self, event_bus):
        """Test filtering history by source."""
        event_bus.publish('TEST', {}, source='ServiceA')
        event_bus.publish('TEST', {}, source='ServiceB')
        event_bus.publish('TEST', {}, source='ServiceA')

        history = event_bus.get_history(source='ServiceA')

        assert len(history) == 2
        assert all(e.source == 'ServiceA' for e in history)

    def test_get_history_count(self, event_bus):
        """Test getting event count."""
        event_bus.publish('EVENT_A', {})
        event_bus.publish('EVENT_B', {})
        event_bus.publish('EVENT_A', {})

        assert event_bus.get_history_count() == 3
        assert event_bus.get_history_count(event_type='EVENT_A') == 2

    def test_clear_history_all(self, event_bus):
        """Test clearing all history."""
        event_bus.publish('EVENT1', {})
        event_bus.publish('EVENT2', {})

        count = event_bus.clear_history()

        assert count == 2
        assert event_bus.get_history_count() == 0

    def test_clear_history_by_type(self, event_bus):
        """Test clearing history for specific event type."""
        event_bus.publish('EVENT_A', {})
        event_bus.publish('EVENT_B', {})
        event_bus.publish('EVENT_A', {})

        count = event_bus.clear_history(event_type='EVENT_A')

        assert count == 2
        assert event_bus.get_history_count() == 1
        assert event_bus.get_history_count(event_type='EVENT_B') == 1


class TestEventBusHistoryManagement:
    """Test history size management."""

    def test_max_history_size_default(self, event_bus):
        """Test default max history size."""
        assert event_bus.get_max_history_size() == 1000

    def test_set_max_history_size(self, event_bus):
        """Test setting max history size."""
        event_bus.set_max_history_size(500)

        assert event_bus.get_max_history_size() == 500

    def test_set_max_history_size_invalid(self, event_bus):
        """Test setting invalid max history size."""
        with pytest.raises(ValueError):
            event_bus.set_max_history_size(0)

    def test_history_trim_on_overflow(self, event_bus):
        """Test that history is trimmed when exceeding max size."""
        import time
        event_bus.set_max_history_size(5)

        # Publish more events than max size
        for i in range(10):
            event_bus.publish('TEST', {'index': i})
            time.sleep(0.001)  # Tiny delay for ordering

        history = event_bus.get_history(limit=100)

        # Should only keep last 5
        assert len(history) == 5
        # Should keep newest events (indices 5-9)
        indices = sorted([h.data['index'] for h in history])
        assert indices == [5, 6, 7, 8, 9]

    def test_history_trim_when_reducing_max_size(self, event_bus):
        """Test trimming history when reducing max size."""
        event_bus.set_max_history_size(100)

        # Publish 50 events
        for i in range(50):
            event_bus.publish('TEST', {'index': i})

        # Reduce max size
        event_bus.set_max_history_size(20)

        history = event_bus.get_history(limit=100)

        # Should only keep last 20
        assert len(history) == 20


class TestEventBusStatistics:
    """Test statistics functionality."""

    def test_get_statistics_empty(self, event_bus):
        """Test statistics when no events."""
        stats = event_bus.get_statistics()

        assert stats['total_events'] == 0
        assert stats['event_type_counts'] == {}
        assert stats['observer_count'] == 0
        assert stats['oldest_event'] is None
        assert stats['newest_event'] is None

    def test_get_statistics_with_events(self, event_bus):
        """Test statistics with events."""
        event_bus.publish('EVENT_A', {})
        event_bus.publish('EVENT_B', {})
        event_bus.publish('EVENT_A', {})

        stats = event_bus.get_statistics()

        assert stats['total_events'] == 3
        assert stats['event_type_counts']['EVENT_A'] == 2
        assert stats['event_type_counts']['EVENT_B'] == 1
        assert stats['oldest_event'] is not None
        assert stats['newest_event'] is not None

    def test_get_statistics_with_observers(self, event_bus):
        """Test statistics includes observer counts."""
        observer1 = MockObserver('Observer1')
        observer2 = MockObserver('Observer2')

        event_bus.subscribe('EVENT_A', observer1)
        event_bus.subscribe('EVENT_A', observer2)
        event_bus.subscribe('EVENT_B', observer1)

        # Need at least one event for statistics
        event_bus.publish('EVENT_A', {})

        stats = event_bus.get_statistics()

        assert stats['observer_count'] == 3
        assert stats['observers_by_event']['EVENT_A'] == 2
        assert stats['observers_by_event']['EVENT_B'] == 1


class TestEventBusIntegration:
    """Integration tests for EventBus."""

    def test_complete_workflow(self, event_bus):
        """Test complete publish-subscribe workflow."""
        observer = MockObserver('TestObserver')

        # Subscribe
        event_bus.subscribe('REQUEST_CREATED', observer)

        # Publish
        event = event_bus.publish(
            'REQUEST_CREATED',
            {'request_id': 1, 'priority': 'high'},
            source='MaintenanceService'
        )

        # Verify observer received event
        assert len(observer.events_received) == 1
        assert observer.events_received[0] == event

        # Verify history
        history = event_bus.get_history('REQUEST_CREATED')
        assert len(history) == 1
        assert history[0] == event

        # Verify statistics
        stats = event_bus.get_statistics()
        assert stats['total_events'] == 1
        assert stats['observer_count'] == 1

    def test_multiple_event_types(self, event_bus):
        """Test handling multiple event types."""
        observer_all = MockObserver('AllEvents')
        observer_created = MockObserver('CreatedOnly')

        event_bus.subscribe('REQUEST_CREATED', observer_all)
        event_bus.subscribe('REQUEST_CREATED', observer_created)
        event_bus.subscribe('REQUEST_COMPLETED', observer_all)

        event_bus.publish('REQUEST_CREATED', {'id': 1})
        event_bus.publish('REQUEST_COMPLETED', {'id': 1})

        assert len(observer_all.events_received) == 2
        assert len(observer_created.events_received) == 1

    def test_observer_failure_isolation(self, event_bus):
        """Test that failed observer doesn't affect others."""
        good_observer = MockObserver('GoodObserver')
        bad_observer = MockObserver('BadObserver', should_fail=True)

        event_bus.subscribe('TEST', good_observer)
        event_bus.subscribe('TEST', bad_observer)

        event_bus.publish('TEST', {})

        # Good observer should still receive event
        assert len(good_observer.events_received) == 1

    def test_repr(self, event_bus):
        """Test string representation."""
        event_bus.publish('TEST', {})
        observer = MockObserver('TestObserver')
        event_bus.subscribe('TEST', observer)

        repr_str = repr(event_bus)

        assert 'EventBus' in repr_str
        assert 'observers=1' in repr_str
        assert 'history=' in repr_str
