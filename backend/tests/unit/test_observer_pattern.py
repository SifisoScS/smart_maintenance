"""
Unit Tests for Observer Pattern

Tests the core observer pattern implementation including Event, Observer, and Subject.
"""

import pytest
from datetime import datetime
from app.patterns.observer import Event, Observer, Subject


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


class TestEvent:
    """Test Event class."""

    def test_event_creation(self):
        """Test creating an event."""
        data = {'request_id': 1, 'status': 'created'}
        event = Event('REQUEST_CREATED', data, source='TestService')

        assert event.event_type == 'REQUEST_CREATED'
        assert event.data == data
        assert event.source == 'TestService'
        assert isinstance(event.timestamp, datetime)
        assert isinstance(event.event_id, str)
        assert len(event.event_id) > 0

    def test_event_without_source(self):
        """Test creating event without source."""
        event = Event('USER_LOGIN', {'user_id': 1})

        assert event.event_type == 'USER_LOGIN'
        assert event.source is None

    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        data = {'key': 'value'}
        event = Event('TEST_EVENT', data, source='TestSource')
        event_dict = event.to_dict()

        assert event_dict['event_id'] == event.event_id
        assert event_dict['event_type'] == 'TEST_EVENT'
        assert event_dict['data'] == data
        assert event_dict['source'] == 'TestSource'
        assert 'timestamp' in event_dict
        assert isinstance(event_dict['timestamp'], str)

    def test_event_repr(self):
        """Test event string representation."""
        event = Event('TEST_EVENT', {}, source='TestSource')
        repr_str = repr(event)

        assert 'Event' in repr_str
        assert 'TEST_EVENT' in repr_str
        assert 'TestSource' in repr_str

    def test_unique_event_ids(self):
        """Test that each event gets unique ID."""
        event1 = Event('TEST', {})
        event2 = Event('TEST', {})

        assert event1.event_id != event2.event_id


class TestObserver:
    """Test Observer abstract class."""

    def test_observer_must_implement_update(self):
        """Test that observer must implement update method."""
        with pytest.raises(TypeError):
            # Cannot instantiate abstract class
            Observer()

    def test_observer_must_implement_name(self):
        """Test that observer must implement name property."""
        class IncompleteObserver(Observer):
            def update(self, event: Event) -> None:
                pass

        with pytest.raises(TypeError):
            IncompleteObserver()

    def test_mock_observer_works(self):
        """Test that mock observer works correctly."""
        observer = MockObserver('TestObserver')

        assert observer.name == 'TestObserver'
        assert len(observer.events_received) == 0

        event = Event('TEST', {})
        observer.update(event)

        assert len(observer.events_received) == 1
        assert observer.events_received[0] == event


class TestSubject:
    """Test Subject class."""

    def test_subject_initialization(self):
        """Test creating a subject."""
        subject = Subject()

        assert isinstance(subject._observers, dict)
        assert len(subject._observers) == 0

    def test_attach_observer(self):
        """Test attaching observer to subject."""
        subject = Subject()
        observer = MockObserver('Observer1')

        subject.attach('TEST_EVENT', observer)

        assert 'TEST_EVENT' in subject._observers
        assert observer in subject._observers['TEST_EVENT']
        assert subject.get_observer_count('TEST_EVENT') == 1

    def test_attach_multiple_observers_to_same_event(self):
        """Test attaching multiple observers to same event type."""
        subject = Subject()
        observer1 = MockObserver('Observer1')
        observer2 = MockObserver('Observer2')

        subject.attach('TEST_EVENT', observer1)
        subject.attach('TEST_EVENT', observer2)

        assert len(subject._observers['TEST_EVENT']) == 2
        assert observer1 in subject._observers['TEST_EVENT']
        assert observer2 in subject._observers['TEST_EVENT']

    def test_attach_same_observer_twice(self):
        """Test that attaching same observer twice doesn't duplicate."""
        subject = Subject()
        observer = MockObserver('Observer1')

        subject.attach('TEST_EVENT', observer)
        subject.attach('TEST_EVENT', observer)

        assert len(subject._observers['TEST_EVENT']) == 1

    def test_attach_observer_to_multiple_events(self):
        """Test attaching observer to multiple event types."""
        subject = Subject()
        observer = MockObserver('Observer1')

        subject.attach('EVENT1', observer)
        subject.attach('EVENT2', observer)

        assert observer in subject._observers['EVENT1']
        assert observer in subject._observers['EVENT2']
        assert subject.get_observer_count() == 2

    def test_detach_observer(self):
        """Test detaching observer from subject."""
        subject = Subject()
        observer = MockObserver('Observer1')

        subject.attach('TEST_EVENT', observer)
        subject.detach('TEST_EVENT', observer)

        assert 'TEST_EVENT' not in subject._observers

    def test_detach_one_of_multiple_observers(self):
        """Test detaching one observer when multiple are attached."""
        subject = Subject()
        observer1 = MockObserver('Observer1')
        observer2 = MockObserver('Observer2')

        subject.attach('TEST_EVENT', observer1)
        subject.attach('TEST_EVENT', observer2)
        subject.detach('TEST_EVENT', observer1)

        assert observer1 not in subject._observers['TEST_EVENT']
        assert observer2 in subject._observers['TEST_EVENT']
        assert len(subject._observers['TEST_EVENT']) == 1

    def test_detach_nonexistent_observer(self):
        """Test detaching observer that isn't attached."""
        subject = Subject()
        observer = MockObserver('Observer1')

        # Should not raise exception
        subject.detach('TEST_EVENT', observer)

    def test_notify_single_observer(self):
        """Test notifying single observer."""
        subject = Subject()
        observer = MockObserver('Observer1')

        subject.attach('TEST_EVENT', observer)
        event = Event('TEST_EVENT', {'data': 'value'})
        result = subject.notify(event)

        assert len(observer.events_received) == 1
        assert observer.events_received[0] == event
        assert result['success_count'] == 1
        assert result['failure_count'] == 0

    def test_notify_multiple_observers(self):
        """Test notifying multiple observers."""
        subject = Subject()
        observer1 = MockObserver('Observer1')
        observer2 = MockObserver('Observer2')

        subject.attach('TEST_EVENT', observer1)
        subject.attach('TEST_EVENT', observer2)

        event = Event('TEST_EVENT', {'data': 'value'})
        result = subject.notify(event)

        assert len(observer1.events_received) == 1
        assert len(observer2.events_received) == 1
        assert result['success_count'] == 2
        assert result['failure_count'] == 0

    def test_notify_with_no_observers(self):
        """Test notifying when no observers are attached."""
        subject = Subject()
        event = Event('UNOBSERVED_EVENT', {})
        result = subject.notify(event)

        assert result['success_count'] == 0
        assert result['failure_count'] == 0

    def test_failed_observer_doesnt_affect_others(self):
        """Test that failed observer doesn't prevent others from being notified."""
        subject = Subject()
        observer1 = MockObserver('Observer1', should_fail=True)
        observer2 = MockObserver('Observer2')
        observer3 = MockObserver('Observer3')

        subject.attach('TEST_EVENT', observer1)
        subject.attach('TEST_EVENT', observer2)
        subject.attach('TEST_EVENT', observer3)

        event = Event('TEST_EVENT', {})
        result = subject.notify(event)

        # Observer1 failed, but 2 and 3 should still receive event
        assert len(observer1.events_received) == 0
        assert len(observer2.events_received) == 1
        assert len(observer3.events_received) == 1
        assert result['success_count'] == 2
        assert result['failure_count'] == 1
        assert 'Observer1' in result['failures']

    def test_get_observers_all(self):
        """Test getting all observers."""
        subject = Subject()
        observer1 = MockObserver('Observer1')
        observer2 = MockObserver('Observer2')

        subject.attach('EVENT1', observer1)
        subject.attach('EVENT2', observer2)

        observers = subject.get_observers()

        assert 'EVENT1' in observers
        assert 'EVENT2' in observers
        assert observer1 in observers['EVENT1']
        assert observer2 in observers['EVENT2']

    def test_get_observers_by_event_type(self):
        """Test getting observers for specific event type."""
        subject = Subject()
        observer1 = MockObserver('Observer1')
        observer2 = MockObserver('Observer2')

        subject.attach('EVENT1', observer1)
        subject.attach('EVENT2', observer2)

        observers = subject.get_observers('EVENT1')

        assert 'EVENT1' in observers
        assert 'EVENT2' not in observers
        assert observer1 in observers['EVENT1']

    def test_get_observer_count(self):
        """Test getting total observer count."""
        subject = Subject()
        observer1 = MockObserver('Observer1')
        observer2 = MockObserver('Observer2')

        subject.attach('EVENT1', observer1)
        subject.attach('EVENT1', observer2)
        subject.attach('EVENT2', observer1)

        assert subject.get_observer_count() == 3
        assert subject.get_observer_count('EVENT1') == 2
        assert subject.get_observer_count('EVENT2') == 1
        assert subject.get_observer_count('EVENT3') == 0

    def test_clear_observers_all(self):
        """Test clearing all observers."""
        subject = Subject()
        observer = MockObserver('Observer1')

        subject.attach('EVENT1', observer)
        subject.attach('EVENT2', observer)

        subject.clear_observers()

        assert len(subject._observers) == 0
        assert subject.get_observer_count() == 0

    def test_clear_observers_by_event_type(self):
        """Test clearing observers for specific event type."""
        subject = Subject()
        observer = MockObserver('Observer1')

        subject.attach('EVENT1', observer)
        subject.attach('EVENT2', observer)

        subject.clear_observers('EVENT1')

        assert 'EVENT1' not in subject._observers
        assert 'EVENT2' in subject._observers
        assert subject.get_observer_count() == 1


class TestObserverIntegration:
    """Integration tests for observer pattern."""

    def test_complete_observer_workflow(self):
        """Test complete workflow: attach, notify, detach."""
        subject = Subject()
        observer = MockObserver('Observer1')

        # Attach
        subject.attach('REQUEST_CREATED', observer)
        assert subject.get_observer_count('REQUEST_CREATED') == 1

        # Notify
        event = Event('REQUEST_CREATED', {'request_id': 1})
        result = subject.notify(event)
        assert result['success_count'] == 1
        assert len(observer.events_received) == 1

        # Detach
        subject.detach('REQUEST_CREATED', observer)
        assert subject.get_observer_count('REQUEST_CREATED') == 0

        # Notify again - observer shouldn't receive it
        event2 = Event('REQUEST_CREATED', {'request_id': 2})
        subject.notify(event2)
        assert len(observer.events_received) == 1  # Still 1, not 2

    def test_multiple_event_types_workflow(self):
        """Test observer handling multiple event types."""
        subject = Subject()
        observer = MockObserver('MultiEventObserver')

        # Subscribe to multiple events
        subject.attach('REQUEST_CREATED', observer)
        subject.attach('REQUEST_COMPLETED', observer)
        subject.attach('USER_LOGIN', observer)

        # Trigger different events
        subject.notify(Event('REQUEST_CREATED', {'id': 1}))
        subject.notify(Event('REQUEST_COMPLETED', {'id': 1}))
        subject.notify(Event('USER_LOGIN', {'user_id': 5}))

        assert len(observer.events_received) == 3
        assert observer.events_received[0].event_type == 'REQUEST_CREATED'
        assert observer.events_received[1].event_type == 'REQUEST_COMPLETED'
        assert observer.events_received[2].event_type == 'USER_LOGIN'
