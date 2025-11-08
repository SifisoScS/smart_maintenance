"""
Metrics Observer

Tracks KPIs and metrics based on system events.
"""

import logging
from datetime import datetime
from typing import Dict
from app.patterns.observer import Observer, Event
from app.events.event_types import EventTypes

logger = logging.getLogger(__name__)


class MetricsObserver(Observer):
    """
    Observer that tracks system metrics and KPIs.

    This observer monitors events to calculate metrics like:
    - Average request completion time
    - Technician workload
    - Request volume by type
    - Asset condition trends
    """

    def __init__(self):
        """Initialize metrics observer."""
        self._logger = logging.getLogger(f"{__name__}.MetricsObserver")
        self._metrics: Dict[str, any] = {
            'requests_created': 0,
            'requests_completed': 0,
            'requests_by_type': {},
            'technician_workload': {},
            'assets_created': 0,
            'condition_changes': 0
        }

    @property
    def name(self) -> str:
        """Observer name for logging."""
        return "MetricsObserver"

    def update(self, event: Event) -> None:
        """
        Update metrics based on event.

        Args:
            event: The event that occurred
        """
        try:
            event_type = event.event_type
            data = event.data

            if event_type == EventTypes.REQUEST_CREATED:
                self._track_request_created(data)
            elif event_type == EventTypes.REQUEST_COMPLETED:
                self._track_request_completed(data)
            elif event_type == EventTypes.REQUEST_ASSIGNED:
                self._track_request_assigned(data)
            elif event_type == EventTypes.ASSET_CREATED:
                self._track_asset_created(data)
            elif event_type == EventTypes.ASSET_CONDITION_CHANGED:
                self._track_condition_change(data)

        except Exception as e:
            self._logger.error(f"Error updating metrics for {event.event_type}: {str(e)}", exc_info=True)
            raise

    def _track_request_created(self, data: dict) -> None:
        """Track new request creation."""
        self._metrics['requests_created'] += 1

        request_type = data.get('type', 'unknown')
        if request_type not in self._metrics['requests_by_type']:
            self._metrics['requests_by_type'][request_type] = 0
        self._metrics['requests_by_type'][request_type] += 1

        self._logger.debug(f"[Metrics] Total requests created: {self._metrics['requests_created']}")

    def _track_request_completed(self, data: dict) -> None:
        """Track request completion."""
        self._metrics['requests_completed'] += 1

        completion_rate = (
            self._metrics['requests_completed'] / self._metrics['requests_created'] * 100
            if self._metrics['requests_created'] > 0 else 0
        )

        self._logger.info(
            f"[Metrics] Request completed. "
            f"Completion rate: {completion_rate:.1f}% "
            f"({self._metrics['requests_completed']}/{self._metrics['requests_created']})"
        )

    def _track_request_assigned(self, data: dict) -> None:
        """Track technician workload."""
        technician_id = data.get('technician_id')
        if technician_id:
            if technician_id not in self._metrics['technician_workload']:
                self._metrics['technician_workload'][technician_id] = 0
            self._metrics['technician_workload'][technician_id] += 1

            self._logger.debug(
                f"[Metrics] Technician {technician_id} workload: "
                f"{self._metrics['technician_workload'][technician_id]} requests"
            )

    def _track_asset_created(self, data: dict) -> None:
        """Track asset creation."""
        self._metrics['assets_created'] += 1
        self._logger.debug(f"[Metrics] Total assets: {self._metrics['assets_created']}")

    def _track_condition_change(self, data: dict) -> None:
        """Track asset condition changes."""
        self._metrics['condition_changes'] += 1
        self._logger.debug(f"[Metrics] Condition changes: {self._metrics['condition_changes']}")

    def get_metrics(self) -> Dict:
        """
        Get current metrics.

        Returns:
            Dictionary of current metrics
        """
        return self._metrics.copy()

    def reset_metrics(self) -> None:
        """Reset all metrics to zero."""
        self._metrics = {
            'requests_created': 0,
            'requests_completed': 0,
            'requests_by_type': {},
            'technician_workload': {},
            'assets_created': 0,
            'condition_changes': 0
        }
        self._logger.info("[Metrics] Metrics reset")
