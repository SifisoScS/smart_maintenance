"""
Notification Observer

Triggers notifications via NotificationService when events occur.
Decouples notification logic from business logic.
"""

import logging
from app.patterns.observer import Observer, Event
from app.events.event_types import EventTypes

logger = logging.getLogger(__name__)


class NotificationObserver(Observer):
    """
    Observer that triggers notifications based on events.

    This observer listens to domain events and triggers appropriate
    notifications through the NotificationService using the Strategy pattern.
    """

    def __init__(self, notification_service):
        """
        Initialize notification observer.

        Args:
            notification_service: NotificationService instance
        """
        self.notification_service = notification_service
        self._logger = logging.getLogger(f"{__name__}.NotificationObserver")

    @property
    def name(self) -> str:
        """Observer name for logging."""
        return "NotificationObserver"

    def update(self, event: Event) -> None:
        """
        Handle event and trigger appropriate notification.

        Args:
            event: The event that occurred
        """
        try:
            event_type = event.event_type
            data = event.data

            if event_type == EventTypes.REQUEST_CREATED:
                self._notify_request_created(data)
            elif event_type == EventTypes.REQUEST_ASSIGNED:
                self._notify_request_assigned(data)
            elif event_type == EventTypes.REQUEST_STARTED:
                self._notify_request_started(data)
            elif event_type == EventTypes.REQUEST_COMPLETED:
                self._notify_request_completed(data)
            elif event_type == EventTypes.USER_REGISTERED:
                self._notify_user_registered(data)
            else:
                self._logger.debug(f"No notification handler for {event_type}")

        except Exception as e:
            self._logger.error(f"Error handling {event.event_type}: {str(e)}", exc_info=True)
            raise  # Re-raise so EventBus logs the failure

    def _notify_request_created(self, data: dict) -> None:
        """Notify about new request creation."""
        self._logger.info(f"[Notification] Request {data.get('request_id')} created")
        # In production, would call notification_service.notify_admins()
        # For now, just log

    def _notify_request_assigned(self, data: dict) -> None:
        """Notify technician about assignment."""
        self._logger.info(
            f"[Notification] Request {data.get('request_id')} "
            f"assigned to technician {data.get('technician_id')}"
        )
        # In production, would call notification_service.notify_technician()

    def _notify_request_started(self, data: dict) -> None:
        """Notify about work starting."""
        self._logger.info(
            f"[Notification] Work started on request {data.get('request_id')} "
            f"by technician {data.get('technician_id')}"
        )
        # In production, would notify requester

    def _notify_request_completed(self, data: dict) -> None:
        """Notify about request completion."""
        self._logger.info(
            f"[Notification] Request {data.get('request_id')} completed "
            f"by technician {data.get('technician_id')}"
        )
        # In production, would notify requester and admins

    def _notify_user_registered(self, data: dict) -> None:
        """Send welcome notification to new user."""
        self._logger.info(f"[Notification] Welcome email to {data.get('email')}")
        # In production, would send welcome email
