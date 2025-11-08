"""
Asset Repository with asset-specific data access methods.

Extends BaseRepository with location and condition-based queries.
"""

from typing import List, Optional
from app.repositories.base_repository import BaseRepository
from app.models.asset import Asset, AssetCategory, AssetCondition, AssetStatus


class AssetRepository(BaseRepository[Asset]):
    """
    Repository for Asset model.

    OOP Principles:
    - Inheritance: Extends BaseRepository functionality
    - Single Responsibility: Handles only asset data access
    - Encapsulation: Complex queries hidden behind simple methods
    """

    def __init__(self):
        """Initialize with Asset model class"""
        super().__init__(Asset)

    def get_by_asset_tag(self, asset_tag: str) -> Optional[Asset]:
        """
        Get asset by unique asset tag.

        Args:
            asset_tag: Asset tag identifier

        Returns:
            Asset instance or None if not found
        """
        return self.get_one_by_filter(asset_tag=asset_tag)

    def asset_tag_exists(self, asset_tag: str) -> bool:
        """
        Check if asset tag already exists.

        Args:
            asset_tag: Asset tag to check

        Returns:
            True if exists, False otherwise
        """
        return self.get_by_asset_tag(asset_tag) is not None

    def get_by_category(self, category: AssetCategory) -> List[Asset]:
        """
        Get all assets of specific category.

        Args:
            category: AssetCategory enum value

        Returns:
            List of assets in the category
        """
        return self.get_by_filter(category=category)

    def get_by_status(self, status: AssetStatus) -> List[Asset]:
        """
        Get all assets with specific status.

        Args:
            status: AssetStatus enum value

        Returns:
            List of assets with the status
        """
        return self.get_by_filter(status=status)

    def get_by_condition(self, condition: AssetCondition) -> List[Asset]:
        """
        Get all assets with specific condition.

        Args:
            condition: AssetCondition enum value

        Returns:
            List of assets with the condition
        """
        return self.get_by_filter(condition=condition)

    def get_by_location(self, building: Optional[str] = None,
                       floor: Optional[str] = None,
                       room: Optional[str] = None) -> List[Asset]:
        """
        Get assets by location criteria.

        Args:
            building: Building name (optional)
            floor: Floor identifier (optional)
            room: Room identifier (optional)

        Returns:
            List of assets matching location criteria
        """
        filters = {}
        if building:
            filters['building'] = building
        if floor:
            filters['floor'] = floor
        if room:
            filters['room'] = room

        return self.get_by_filter(**filters)

    def get_operational_assets(self) -> List[Asset]:
        """
        Get all operational (active status) assets.

        Returns:
            List of active assets
        """
        return self.get_by_status(AssetStatus.ACTIVE)

    def get_assets_needing_maintenance(self) -> List[Asset]:
        """
        Get assets in poor or critical condition.

        Returns:
            List of assets that need maintenance

        Use case: Proactive maintenance scheduling
        """
        poor_assets = self.get_by_condition(AssetCondition.POOR)
        critical_assets = self.get_by_condition(AssetCondition.CRITICAL)

        # Combine and remove duplicates
        return list(set(poor_assets + critical_assets))

    def get_assets_under_repair(self) -> List[Asset]:
        """
        Get all assets currently under repair.

        Returns:
            List of assets with IN_REPAIR status
        """
        return self.get_by_status(AssetStatus.IN_REPAIR)

    def get_assets_out_of_service(self) -> List[Asset]:
        """
        Get all assets out of service.

        Returns:
            List of out-of-service assets
        """
        return self.get_by_status(AssetStatus.OUT_OF_SERVICE)

    def get_retired_assets(self) -> List[Asset]:
        """
        Get all retired assets.

        Returns:
            List of retired assets
        """
        return self.get_by_status(AssetStatus.RETIRED)

    def search_assets(self, search_term: str) -> List[Asset]:
        """
        Search assets by name, description, or asset tag.

        Args:
            search_term: Search string

        Returns:
            List of matching assets
        """
        from app.database import db

        search_pattern = f"%{search_term}%"

        return db.session.query(Asset).filter(
            db.or_(
                Asset.name.ilike(search_pattern),
                Asset.description.ilike(search_pattern),
                Asset.asset_tag.ilike(search_pattern)
            )
        ).all()

    def get_assets_by_manufacturer(self, manufacturer: str) -> List[Asset]:
        """
        Get assets by manufacturer.

        Args:
            manufacturer: Manufacturer name

        Returns:
            List of assets from manufacturer
        """
        return self.get_by_filter(manufacturer=manufacturer)

    def create_asset(self, name: str, asset_tag: str, category: AssetCategory, **kwargs) -> Asset:
        """
        Create new asset with validation.

        Args:
            name: Asset name
            asset_tag: Unique asset tag
            category: AssetCategory enum value
            **kwargs: Additional asset fields

        Returns:
            Created asset instance

        Raises:
            ValueError: If asset tag already exists or validation fails
        """
        # Check if asset tag already exists
        if self.asset_tag_exists(asset_tag):
            raise ValueError(f"Asset tag {asset_tag} already exists")

        # Use base repository create method
        return self.create(
            name=name,
            asset_tag=asset_tag,
            category=category,
            **kwargs
        )

    def mark_asset_under_repair(self, asset_id: int) -> bool:
        """
        Mark asset as under repair.

        Args:
            asset_id: Asset ID

        Returns:
            True if successful, False if asset not found
        """
        asset = self.get_by_id(asset_id)

        if asset:
            asset.mark_under_repair()
            self.update(asset)
            return True

        return False

    def mark_asset_repaired(self, asset_id: int, new_condition: Optional[AssetCondition] = None) -> bool:
        """
        Mark asset as repaired and return to active status.

        Args:
            asset_id: Asset ID
            new_condition: Updated condition after repair (optional)

        Returns:
            True if successful, False if asset not found
        """
        asset = self.get_by_id(asset_id)

        if asset:
            asset.mark_repaired(new_condition)
            self.update(asset)
            return True

        return False

    def update_asset_condition(self, asset_id: int, new_condition: AssetCondition) -> bool:
        """
        Update asset condition.

        Args:
            asset_id: Asset ID
            new_condition: New condition value

        Returns:
            True if successful, False if asset not found
        """
        asset = self.get_by_id(asset_id)

        if asset:
            asset.update_condition(new_condition)
            self.update(asset)
            return True

        return False

    def retire_asset(self, asset_id: int) -> bool:
        """
        Retire an asset.

        Args:
            asset_id: Asset ID

        Returns:
            True if successful, False if asset not found
        """
        asset = self.get_by_id(asset_id)

        if asset:
            asset.retire()
            self.update(asset)
            return True

        return False

    def get_asset_statistics(self) -> dict:
        """
        Get asset statistics summary.

        Returns:
            Dictionary with asset counts by status and condition
        """
        return {
            'total_assets': self.count(),
            'by_status': {
                'active': self.count(status=AssetStatus.ACTIVE),
                'in_repair': self.count(status=AssetStatus.IN_REPAIR),
                'out_of_service': self.count(status=AssetStatus.OUT_OF_SERVICE),
                'retired': self.count(status=AssetStatus.RETIRED),
            },
            'by_condition': {
                'excellent': self.count(condition=AssetCondition.EXCELLENT),
                'good': self.count(condition=AssetCondition.GOOD),
                'fair': self.count(condition=AssetCondition.FAIR),
                'poor': self.count(condition=AssetCondition.POOR),
                'critical': self.count(condition=AssetCondition.CRITICAL),
            },
            'needs_maintenance': len(self.get_assets_needing_maintenance())
        }
