"""
EventBus - Centralized Event Dispatcher

The EventBus is a singleton that manages all application events using the Observer pattern.
It provides a centralized point for publishing and subscribing to domain events, enabling
loose coupling between system components.

Key Features:
- Singleton pattern ensures one event bus instance
- Event history storage for debugging and audit
- Subscribe/unsubscribe functionality
- Query history by event type or time range
- Automatic event timestamping and ID generation
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from app.patterns.singleton import SingletonMeta
from app.patterns.observer import Subject, Event, Observer

logger = logging.getLogger(__name__)


class EventBus(Subject, metaclass=SingletonMeta):
    """
    Centralized event bus for application-wide event distribution.

    The EventBus acts as a mediator between event publishers (services) and
    event subscribers (observers). It maintains event history for debugging
    and audit purposes.

    Example:
        # Get singleton instance
        event_bus = EventBus()

        # Subscribe observer to event
        event_bus.subscribe('REQUEST_CREATED', notification_observer)

        # Publish event
        event_bus.publish('REQUEST_CREATED', {'request_id': 1})
    """

    def __init__(self):
        """Initialize EventBus with empty history."""
        super().__init__()
        self._event_history: List[Event] = []
        self._max_history_size = 1000
        self._logger = logging.getLogger(f"{__name__}.EventBus")
        self._logger.info("EventBus initialized")

    def publish(self, event_type: str, data: Dict[str, Any], source: Optional[str] = None) -> Event:
        """
        Publish event to all subscribed observers.

        Creates an Event object and notifies all observers subscribed to the event type.
        The event is also stored in history for later retrieval.

        Args:
            event_type: Type of event (e.g., 'REQUEST_CREATED')
            data: Event payload data
            source: Optional source identifier (e.g., 'MaintenanceService.create_request')

        Returns:
            Event: The published event object

        Example:
            event = event_bus.publish(
                'REQUEST_CREATED',
                {'request_id': 1, 'priority': 'high'},
                source='MaintenanceService'
            )
        """
        # Create event
        event = Event(event_type, data, source)

        # Add to history
        self._add_to_history(event)

        # Notify observers
        result = self.notify(event)

        self._logger.info(
            f"Published {event_type} (id={event.event_id[:8]}) - "
            f"{result['success_count']} successful, {result['failure_count']} failed"
        )

        return event

    def subscribe(self, event_type: str, observer: Observer) -> None:
        """
        Subscribe observer to event type.

        Args:
            event_type: Type of event to observe
            observer: Observer instance to subscribe

        Example:
            event_bus.subscribe('REQUEST_CREATED', notification_observer)
        """
        self.attach(event_type, observer)
        self._logger.info(f"Subscribed {observer.name} to {event_type}")

    def unsubscribe(self, event_type: str, observer: Observer) -> None:
        """
        Unsubscribe observer from event type.

        Args:
            event_type: Type of event to stop observing
            observer: Observer instance to unsubscribe

        Example:
            event_bus.unsubscribe('REQUEST_CREATED', notification_observer)
        """
        self.detach(event_type, observer)
        self._logger.info(f"Unsubscribed {observer.name} from {event_type}")

    def get_history(
        self,
        event_type: Optional[str] = None,
        limit: int = 100,
        since: Optional[datetime] = None,
        source: Optional[str] = None
    ) -> List[Event]:
        """
        Get event history with optional filtering.

        Args:
            event_type: Optional filter by event type
            limit: Maximum number of events to return (default 100)
            since: Optional filter for events after this time
            source: Optional filter by event source

        Returns:
            List of events matching filters, newest first

        Example:
            # Get last 50 REQUEST_CREATED events
            events = event_bus.get_history('REQUEST_CREATED', limit=50)

            # Get events from last hour
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            events = event_bus.get_history(since=one_hour_ago)
        """
        filtered_events = self._event_history.copy()

        # Filter by event type
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]

        # Filter by timestamp
        if since:
            filtered_events = [e for e in filtered_events if e.timestamp >= since]

        # Filter by source
        if source:
            filtered_events = [e for e in filtered_events if e.source == source]

        # Sort by timestamp (newest first) and limit
        filtered_events.sort(key=lambda e: e.timestamp, reverse=True)
        return filtered_events[:limit]

    def get_history_count(
        self,
        event_type: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> int:
        """
        Get count of events in history.

        Args:
            event_type: Optional filter by event type
            since: Optional filter for events after this time

        Returns:
            Count of events matching filters

        Example:
            total_events = event_bus.get_history_count()
            request_events = event_bus.get_history_count('REQUEST_CREATED')
        """
        return len(self.get_history(event_type=event_type, since=since, limit=999999))

    def clear_history(self, event_type: Optional[str] = None) -> int:
        """
        Clear event history.

        Args:
            event_type: Optional filter to clear only specific event type

        Returns:
            Number of events cleared

        Warning:
            Use with caution - this permanently removes event history
        """
        if event_type:
            events_to_remove = [e for e in self._event_history if e.event_type == event_type]
            for event in events_to_remove:
                self._event_history.remove(event)
            count = len(events_to_remove)
            self._logger.warning(f"Cleared {count} events of type {event_type} from history")
        else:
            count = len(self._event_history)
            self._event_history.clear()
            self._logger.warning(f"Cleared all {count} events from history")

        return count

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get EventBus statistics.

        Returns:
            Dictionary containing:
                - total_events: Total events in history
                - event_type_counts: Count by event type
                - observer_count: Total observers registered
                - observers_by_event: Observers per event type
                - oldest_event: Timestamp of oldest event
                - newest_event: Timestamp of newest event

        Example:
            stats = event_bus.get_statistics()
            print(f"Total events: {stats['total_events']}")
        """
        if not self._event_history:
            return {
                'total_events': 0,
                'event_type_counts': {},
                'observer_count': self.get_observer_count(),
                'observers_by_event': {},
                'oldest_event': None,
                'newest_event': None
            }

        # Count events by type
        event_type_counts = {}
        for event in self._event_history:
            event_type_counts[event.event_type] = event_type_counts.get(event.event_type, 0) + 1

        # Count observers by event type
        observers_by_event = {}
        for event_type, observer_list in self._observers.items():
            observers_by_event[event_type] = len(observer_list)

        return {
            'total_events': len(self._event_history),
            'event_type_counts': event_type_counts,
            'observer_count': self.get_observer_count(),
            'observers_by_event': observers_by_event,
            'oldest_event': self._event_history[0].timestamp.isoformat() if self._event_history else None,
            'newest_event': self._event_history[-1].timestamp.isoformat() if self._event_history else None
        }

    def _add_to_history(self, event: Event) -> None:
        """
        Add event to history, maintaining max size.

        Args:
            event: Event to add to history

        Note:
            If history exceeds max size, oldest events are removed.
        """
        self._event_history.append(event)

        # Trim history if it exceeds max size
        if len(self._event_history) > self._max_history_size:
            overflow = len(self._event_history) - self._max_history_size
            self._event_history = self._event_history[overflow:]
            self._logger.debug(f"Trimmed {overflow} old events from history")

    def set_max_history_size(self, size: int) -> None:
        """
        Set maximum history size.

        Args:
            size: Maximum number of events to keep in history

        Raises:
            ValueError: If size is less than 1

        Example:
            event_bus.set_max_history_size(5000)
        """
        if size < 1:
            raise ValueError("Max history size must be at least 1")

        old_size = self._max_history_size
        self._max_history_size = size

        # Trim if current history exceeds new max
        if len(self._event_history) > size:
            overflow = len(self._event_history) - size
            self._event_history = self._event_history[overflow:]
            self._logger.info(f"Trimmed {overflow} events after reducing max history size")

        self._logger.info(f"Max history size changed from {old_size} to {size}")

    def get_max_history_size(self) -> int:
        """
        Get maximum history size.

        Returns:
            Maximum number of events kept in history
        """
        return self._max_history_size

    def __repr__(self) -> str:
        """String representation of EventBus."""
        return (
            f"EventBus(observers={self.get_observer_count()}, "
            f"history={len(self._event_history)}/{self._max_history_size})"
        )
