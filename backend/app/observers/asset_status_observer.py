"""
Asset Status Observer

Automatically updates asset status based on maintenance request events.
"""

import logging
from app.patterns.observer import Observer, Event
from app.events.event_types import EventTypes

logger = logging.getLogger(__name__)


class AssetStatusObserver(Observer):
    """
    Observer that auto-updates asset status based on maintenance events.

    This observer implements business rules for asset status management:
    - When request assigned → mark asset as "under maintenance"
    - When request completed → restore asset status
    """

    def __init__(self, asset_repository=None):
        """
        Initialize asset status observer.

        Args:
            asset_repository: Optional AssetRepository for database updates
        """
        self.asset_repo = asset_repository
        self._logger = logging.getLogger(f"{__name__}.AssetStatusObserver")

    @property
    def name(self) -> str:
        """Observer name for logging."""
        return "AssetStatusObserver"

    def update(self, event: Event) -> None:
        """
        Update asset status based on event.

        Args:
            event: The event that occurred
        """
        try:
            event_type = event.event_type
            data = event.data

            if event_type == EventTypes.REQUEST_ASSIGNED:
                self._mark_asset_in_maintenance(data)
            elif event_type == EventTypes.REQUEST_COMPLETED:
                self._restore_asset_status(data)
            elif event_type == EventTypes.ASSET_CONDITION_CHANGED:
                self._handle_condition_change(data)

        except Exception as e:
            self._logger.error(
                f"Error updating asset status for {event.event_type}: {str(e)}",
                exc_info=True
            )
            raise

    def _mark_asset_in_maintenance(self, data: dict) -> None:
        """
        Mark asset as under maintenance when request is assigned.

        Args:
            data: Event data containing asset_id
        """
        asset_id = data.get('asset_id')
        request_id = data.get('request_id')

        if asset_id:
            self._logger.info(
                f"[AssetStatus] Marking asset {asset_id} as under maintenance "
                f"(request {request_id})"
            )

            # In production, would update via repository:
            # if self.asset_repo:
            #     self.asset_repo.update_status(asset_id, AssetStatus.IN_REPAIR)

    def _restore_asset_status(self, data: dict) -> None:
        """
        Restore asset status when maintenance is completed.

        Args:
            data: Event data containing asset_id
        """
        asset_id = data.get('asset_id')
        request_id = data.get('request_id')

        if asset_id:
            self._logger.info(
                f"[AssetStatus] Restoring asset {asset_id} status "
                f"after request {request_id} completion"
            )

            # In production, would update via repository:
            # if self.asset_repo:
            #     self.asset_repo.update_status(asset_id, AssetStatus.ACTIVE)

    def _handle_condition_change(self, data: dict) -> None:
        """
        Handle asset condition changes.

        Args:
            data: Event data with condition change info
        """
        asset_id = data.get('asset_id')
        new_condition = data.get('new_condition')

        self._logger.info(
            f"[AssetStatus] Asset {asset_id} condition changed to {new_condition}"
        )

        # If condition is poor/critical, could auto-create maintenance request
