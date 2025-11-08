"""
Unit tests for AssetRepository.

Tests asset management, status transitions, and condition tracking.
"""

import pytest
from app.repositories.asset_repository import AssetRepository
from app.models import Asset, AssetCategory, AssetStatus, AssetCondition


class TestAssetRepository:
    """Test suite for AssetRepository"""

    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        """Set up test dependencies"""
        self.repo = AssetRepository()

    def test_create_asset_success(self, db_session):
        """Test creating an asset with valid data"""
        asset = self.repo.create_asset(
            name='Test Equipment',
            asset_tag='EQUIP-001',
            category=AssetCategory.ELECTRICAL,
            status=AssetStatus.ACTIVE,
            condition=AssetCondition.GOOD,
            building='Main Building',
            floor='2',
            room='201'
        )

        assert asset.id is not None
        assert asset.name == 'Test Equipment'
        assert asset.asset_tag == 'EQUIP-001'
        assert asset.category == AssetCategory.ELECTRICAL
        assert asset.status == AssetStatus.ACTIVE
        assert asset.condition == AssetCondition.GOOD

    def test_create_asset_duplicate_tag(self, db_session, sample_asset):
        """Test creating asset with duplicate tag raises error"""
        with pytest.raises(ValueError, match="already exists"):
            self.repo.create_asset(
                name='Duplicate',
                asset_tag=sample_asset.asset_tag,
                category=AssetCategory.PLUMBING
            )

    def test_get_by_asset_tag(self, db_session, sample_asset):
        """Test retrieving asset by tag"""
        asset = self.repo.get_by_asset_tag(sample_asset.asset_tag)

        assert asset is not None
        assert asset.id == sample_asset.id
        assert asset.asset_tag == sample_asset.asset_tag

    def test_asset_tag_exists(self, db_session, sample_asset):
        """Test checking if asset tag exists"""
        assert self.repo.asset_tag_exists(sample_asset.asset_tag) is True
        assert self.repo.asset_tag_exists('NONEXISTENT') is False

    def test_get_by_category(self, db_session, multiple_assets):
        """Test retrieving assets by category"""
        electrical = self.repo.get_by_category(AssetCategory.ELECTRICAL)
        plumbing = self.repo.get_by_category(AssetCategory.PLUMBING)
        hvac = self.repo.get_by_category(AssetCategory.HVAC)

        # With 10 assets cycling through 3 categories
        assert len(electrical) >= 3
        assert len(plumbing) >= 3
        assert len(hvac) >= 3

        assert all(a.category == AssetCategory.ELECTRICAL for a in electrical)
        assert all(a.category == AssetCategory.PLUMBING for a in plumbing)
        assert all(a.category == AssetCategory.HVAC for a in hvac)

    def test_get_by_status(self, db_session, multiple_assets):
        """Test retrieving assets by status"""
        active = self.repo.get_by_status(AssetStatus.ACTIVE)
        in_repair = self.repo.get_by_status(AssetStatus.IN_REPAIR)

        assert len(active) > 0
        assert len(in_repair) > 0
        assert all(a.status == AssetStatus.ACTIVE for a in active)
        assert all(a.status == AssetStatus.IN_REPAIR for a in in_repair)

    def test_get_by_condition(self, db_session, multiple_assets):
        """Test retrieving assets by condition"""
        excellent = self.repo.get_by_condition(AssetCondition.EXCELLENT)
        poor = self.repo.get_by_condition(AssetCondition.POOR)

        assert len(excellent) > 0
        assert len(poor) > 0
        assert all(a.condition == AssetCondition.EXCELLENT for a in excellent)
        assert all(a.condition == AssetCondition.POOR for a in poor)

    def test_get_by_location(self, db_session, multiple_assets):
        """Test retrieving assets by location"""
        # All test assets are in Building A
        building_assets = self.repo.get_by_location(building='Building A')
        assert len(building_assets) == len(multiple_assets)

        # Floor 1 assets
        floor1_assets = self.repo.get_by_location(building='Building A', floor='1')
        assert len(floor1_assets) > 0
        assert all(a.floor == '1' for a in floor1_assets)

    def test_get_operational_assets(self, db_session, multiple_assets):
        """Test retrieving operational (active) assets"""
        operational = self.repo.get_operational_assets()

        assert all(a.status == AssetStatus.ACTIVE for a in operational)
        assert all(a.is_operational for a in operational)

    def test_get_assets_needing_maintenance(self, db_session, multiple_assets):
        """Test retrieving assets in poor or critical condition"""
        needing_maintenance = self.repo.get_assets_needing_maintenance()

        assert all(
            a.condition in [AssetCondition.POOR, AssetCondition.CRITICAL]
            for a in needing_maintenance
        )
        assert all(a.needs_maintenance for a in needing_maintenance)

    def test_get_assets_under_repair(self, db_session, multiple_assets):
        """Test retrieving assets under repair"""
        under_repair = self.repo.get_assets_under_repair()

        assert all(a.status == AssetStatus.IN_REPAIR for a in under_repair)

    def test_search_assets(self, db_session, multiple_assets):
        """Test searching assets by name/description/tag"""
        # Search by name
        results = self.repo.search_assets('Asset 1')
        assert len(results) > 0

        # Search by tag
        results = self.repo.search_assets('ASSET-001')
        assert len(results) == 1

    def test_mark_asset_under_repair(self, db_session, sample_asset):
        """Test marking asset as under repair"""
        assert sample_asset.status == AssetStatus.ACTIVE

        result = self.repo.mark_asset_under_repair(sample_asset.id)

        assert result is True
        db_session.session.refresh(sample_asset)
        assert sample_asset.status == AssetStatus.IN_REPAIR

    def test_mark_retired_asset_under_repair_fails(self, db_session, sample_asset):
        """Test cannot mark retired asset under repair"""
        sample_asset.retire()
        db_session.session.commit()

        with pytest.raises(ValueError, match="Cannot repair retired asset"):
            self.repo.mark_asset_under_repair(sample_asset.id)

    def test_mark_asset_repaired(self, db_session, sample_asset):
        """Test marking asset as repaired"""
        sample_asset.mark_under_repair()
        db_session.session.commit()

        result = self.repo.mark_asset_repaired(sample_asset.id, AssetCondition.EXCELLENT)

        assert result is True
        db_session.session.refresh(sample_asset)
        assert sample_asset.status == AssetStatus.ACTIVE
        assert sample_asset.condition == AssetCondition.EXCELLENT

    def test_update_asset_condition(self, db_session, sample_asset):
        """Test updating asset condition"""
        assert sample_asset.condition == AssetCondition.GOOD

        result = self.repo.update_asset_condition(sample_asset.id, AssetCondition.POOR)

        assert result is True
        db_session.session.refresh(sample_asset)
        assert sample_asset.condition == AssetCondition.POOR

    def test_retire_asset(self, db_session, sample_asset):
        """Test retiring an asset"""
        result = self.repo.retire_asset(sample_asset.id)

        assert result is True
        db_session.session.refresh(sample_asset)
        assert sample_asset.status == AssetStatus.RETIRED

    def test_asset_full_location_property(self, db_session, sample_asset):
        """Test computed full_location property"""
        expected = "Building: Main Building, Floor: 1, Room: 101"
        assert sample_asset.full_location == expected

    def test_asset_needs_maintenance_property(self, db_session, sample_asset):
        """Test needs_maintenance computed property"""
        sample_asset.condition = AssetCondition.GOOD
        assert sample_asset.needs_maintenance is False

        sample_asset.condition = AssetCondition.POOR
        assert sample_asset.needs_maintenance is True

        sample_asset.condition = AssetCondition.CRITICAL
        assert sample_asset.needs_maintenance is True

    def test_asset_is_operational_property(self, db_session, sample_asset):
        """Test is_operational computed property"""
        assert sample_asset.is_operational is True

        sample_asset.mark_under_repair()
        assert sample_asset.is_operational is False

        sample_asset.mark_repaired()
        assert sample_asset.is_operational is True

    def test_get_asset_statistics(self, db_session, multiple_assets):
        """Test asset statistics aggregation"""
        stats = self.repo.get_asset_statistics()

        assert stats['total'] == len(multiple_assets)
        assert 'by_status' in stats
        assert 'by_condition' in stats
        assert 'needs_maintenance' in stats

        # Verify counts add up
        status_total = sum(stats['by_status'].values())
        assert status_total == stats['total']

    def test_asset_to_dict(self, db_session, sample_asset):
        """Test asset serialization to dictionary"""
        data = sample_asset.to_dict()

        assert data['name'] == sample_asset.name
        assert data['asset_tag'] == sample_asset.asset_tag
        assert data['category'] == AssetCategory.ELECTRICAL.value
        assert data['status'] == AssetStatus.ACTIVE.value
        assert data['condition'] == AssetCondition.GOOD.value
        assert 'full_location' in data
        assert 'needs_maintenance' in data
        assert 'is_operational' in data

    def test_count_assets(self, db_session, multiple_assets):
        """Test counting assets"""
        total = self.repo.count()
        assert total == len(multiple_assets)

        active_count = self.repo.count(status=AssetStatus.ACTIVE)
        assert active_count > 0

    def test_delete_asset(self, db_session, sample_asset):
        """Test deleting an asset"""
        asset_id = sample_asset.id

        result = self.repo.delete(sample_asset)

        assert result is True
        assert self.repo.get_by_id(asset_id) is None
