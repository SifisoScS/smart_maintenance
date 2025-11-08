"""
Logging Observer

Logs all events to a dedicated event log for audit and debugging purposes.
"""

import logging
from datetime import datetime
from app.patterns.observer import Observer, Event

logger = logging.getLogger(__name__)


class LoggingObserver(Observer):
    """
    Observer that logs all events for audit trail.

    This observer maintains a comprehensive log of all system events,
    useful for debugging, auditing, and compliance.
    """

    def __init__(self):
        """Initialize logging observer."""
        self._logger = logging.getLogger("EventLog")
        # Configure dedicated logger for events
        self._logger.setLevel(logging.INFO)

    @property
    def name(self) -> str:
        """Observer name for logging."""
        return "LoggingObserver"

    def update(self, event: Event) -> None:
        """
        Log event with full details.

        Args:
            event: The event that occurred
        """
        try:
            log_entry = self._format_log_entry(event)
            self._logger.info(log_entry)

        except Exception as e:
            logger.error(f"Error logging event {event.event_type}: {str(e)}", exc_info=True)
            raise

    def _format_log_entry(self, event: Event) -> str:
        """
        Format event as log entry.

        Args:
            event: Event to format

        Returns:
            Formatted log string
        """
        timestamp = event.timestamp.isoformat()
        event_id = event.event_id[:8]
        source = event.source or "Unknown"

        # Format data as key-value pairs
        data_str = ", ".join(f"{k}={v}" for k, v in event.data.items())

        return (
            f"[EVENT] {timestamp} | "
            f"Type={event.event_type} | "
            f"ID={event_id} | "
            f"Source={source} | "
            f"Data=({data_str})"
        )
