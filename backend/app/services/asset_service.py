"""
Asset Service for Asset Management

Business logic for tracking and managing organizational assets.
"""

from typing import List, Dict
from app.services.base_service import BaseService
from app.repositories import AssetRepository
from app.models import AssetCondition, AssetStatus
from app.patterns.event_bus import EventBus
from app.events.event_types import EventTypes


class AssetService(BaseService):
    """Service for asset management operations."""

    def __init__(self, asset_repository: AssetRepository):
        super().__init__()
        self.asset_repo = asset_repository
        self.event_bus = EventBus()

    def get_assets_needing_maintenance(self) -> dict:
        """Get all assets requiring maintenance (poor/critical condition)."""
        try:
            assets = self.asset_repo.get_assets_needing_maintenance()
            return self._build_success_response(
                data=[asset.to_dict() for asset in assets],
                message=f"Found {len(assets)} assets needing maintenance"
            )
        except Exception as e:
            return self._handle_exception(e, "get_assets_needing_maintenance")

    def update_asset_condition(self, asset_id: int, new_condition: str) -> dict:
        """
        Update asset condition.

        Business Rule: Automatically flag for maintenance if poor/critical
        """
        try:
            self._validate_positive(asset_id, 'asset_id')

            try:
                condition_enum = AssetCondition(new_condition.lower())
            except ValueError:
                return self._build_error_response(f"Invalid condition: {new_condition}")

            # Get asset to capture old condition
            asset_before_update = self.asset_repo.get_by_id(asset_id)
            old_condition = asset_before_update.condition.value if asset_before_update else 'unknown'

            success = self.asset_repo.update_asset_condition(asset_id, condition_enum)

            if success:
                self._log_action(f"Asset {asset_id} condition updated to {new_condition}")

                # Publish ASSET_CONDITION_CHANGED event
                self.event_bus.publish(
                    EventTypes.ASSET_CONDITION_CHANGED,
                    {
                        'asset_id': asset_id,
                        'old_condition': old_condition,
                        'new_condition': new_condition,
                        'asset_name': asset_before_update.name if asset_before_update else f'Asset {asset_id}'
                    },
                    source='AssetService.update_asset_condition'
                )

                # Get updated asset to return full data
                asset = self.asset_repo.get_by_id(asset_id)
                return self._build_success_response(
                    data=asset.to_dict() if asset else {'asset_id': asset_id, 'condition': new_condition},
                    message="Asset condition updated"
                )
            return self._build_error_response("Asset not found")

        except Exception as e:
            return self._handle_exception(e, "update_asset_condition")

    def get_asset_statistics(self) -> dict:
        """Get asset statistics summary."""
        try:
            stats = self.asset_repo.get_asset_statistics()
            return self._build_success_response(data=stats)
        except Exception as e:
            return self._handle_exception(e, "get_asset_statistics")
