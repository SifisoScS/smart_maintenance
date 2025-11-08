"""
Observer Pattern Implementation

The Observer pattern defines a one-to-many dependency between objects so that when
one object changes state, all its dependents are notified automatically.

Components:
- Event: Data container for domain events
- Observer: Abstract interface for observers
- Subject: Manages observers and notifies them of events
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class Event:
    """
    Domain event with type, data, and metadata.

    Represents something that happened in the system that other
    components may want to react to.
    """

    def __init__(self, event_type: str, data: Dict[str, Any], source: Optional[str] = None):
        """
        Initialize event.

        Args:
            event_type: Type of event (e.g., 'REQUEST_CREATED')
            data: Event payload data
            source: Optional source identifier (e.g., 'MaintenanceService.create_request')
        """
        self.event_type = event_type
        self.data = data
        self.source = source
        self.timestamp = datetime.utcnow()
        self.event_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'data': self.data,
            'source': self.source,
            'timestamp': self.timestamp.isoformat()
        }

    def __repr__(self) -> str:
        """String representation of event."""
        return f"Event(type={self.event_type}, id={self.event_id[:8]}, source={self.source})"


class Observer(ABC):
    """
    Abstract observer that responds to events.

    Observers implement the update method to handle specific events.
    Multiple observers can subscribe to the same event type.
    """

    @abstractmethod
    def update(self, event: Event) -> None:
        """
        Handle event notification.

        Args:
            event: The event that occurred

        Note:
            Implementations should handle exceptions internally to prevent
            one failing observer from affecting others.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Observer name for logging and debugging.

        Returns:
            str: Human-readable observer name
        """
        pass

    def __repr__(self) -> str:
        """String representation of observer."""
        return f"{self.__class__.__name__}(name={self.name})"


class Subject:
    """
    Base subject that manages observers and notifies them of events.

    Maintains a dictionary of event types to lists of observers.
    When an event is published, all observers subscribed to that
    event type are notified.
    """

    def __init__(self):
        """Initialize subject with empty observer registry."""
        self._observers: Dict[str, List[Observer]] = {}
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def attach(self, event_type: str, observer: Observer) -> None:
        """
        Attach observer to specific event type.

        Args:
            event_type: Type of event to observe
            observer: Observer instance to attach

        Example:
            subject.attach('REQUEST_CREATED', notification_observer)
        """
        if event_type not in self._observers:
            self._observers[event_type] = []

        if observer not in self._observers[event_type]:
            self._observers[event_type].append(observer)
            self._logger.debug(f"Attached {observer.name} to {event_type}")
        else:
            self._logger.warning(f"{observer.name} already attached to {event_type}")

    def detach(self, event_type: str, observer: Observer) -> None:
        """
        Detach observer from event type.

        Args:
            event_type: Type of event to stop observing
            observer: Observer instance to detach

        Example:
            subject.detach('REQUEST_CREATED', notification_observer)
        """
        if event_type in self._observers:
            try:
                self._observers[event_type].remove(observer)
                self._logger.debug(f"Detached {observer.name} from {event_type}")

                # Clean up empty observer lists
                if not self._observers[event_type]:
                    del self._observers[event_type]
            except ValueError:
                self._logger.warning(f"{observer.name} not found in {event_type} observers")

    def notify(self, event: Event) -> Dict[str, Any]:
        """
        Notify all observers of event.

        Observers are notified sequentially. If an observer raises an exception,
        it is logged but does not prevent other observers from being notified.

        Args:
            event: Event to notify observers about

        Returns:
            Dict with notification results:
                - success_count: Number of successful notifications
                - failure_count: Number of failed notifications
                - failures: List of observer names that failed

        Example:
            event = Event('REQUEST_CREATED', {'request_id': 1})
            result = subject.notify(event)
        """
        event_type = event.event_type
        observers = self._observers.get(event_type, [])

        if not observers:
            self._logger.debug(f"No observers for event {event_type}")
            return {
                'success_count': 0,
                'failure_count': 0,
                'failures': []
            }

        self._logger.info(f"Notifying {len(observers)} observers of {event_type}")

        success_count = 0
        failure_count = 0
        failures = []

        for observer in observers:
            try:
                observer.update(event)
                success_count += 1
                self._logger.debug(f"✓ {observer.name} handled {event_type}")
            except Exception as e:
                failure_count += 1
                failures.append(observer.name)
                self._logger.error(
                    f"✗ {observer.name} failed to handle {event_type}: {str(e)}",
                    exc_info=True
                )

        return {
            'success_count': success_count,
            'failure_count': failure_count,
            'failures': failures
        }

    def get_observers(self, event_type: Optional[str] = None) -> Dict[str, List[Observer]]:
        """
        Get registered observers.

        Args:
            event_type: Optional event type to filter by

        Returns:
            Dict mapping event types to observer lists

        Example:
            all_observers = subject.get_observers()
            request_observers = subject.get_observers('REQUEST_CREATED')
        """
        if event_type:
            return {event_type: self._observers.get(event_type, [])}
        return self._observers.copy()

    def get_observer_count(self, event_type: Optional[str] = None) -> int:
        """
        Get count of registered observers.

        Args:
            event_type: Optional event type to filter by

        Returns:
            Total count of observers
        """
        if event_type:
            return len(self._observers.get(event_type, []))

        return sum(len(obs_list) for obs_list in self._observers.values())

    def clear_observers(self, event_type: Optional[str] = None) -> None:
        """
        Clear all observers or observers for specific event type.

        Args:
            event_type: Optional event type to clear observers for

        Warning:
            Use with caution - this removes all observer registrations
        """
        if event_type:
            if event_type in self._observers:
                del self._observers[event_type]
                self._logger.info(f"Cleared all observers for {event_type}")
        else:
            self._observers.clear()
            self._logger.info("Cleared all observers")
