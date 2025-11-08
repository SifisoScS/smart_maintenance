"""
Unit Tests for AssetService

Tests:
- Asset condition management
- Assets needing maintenance
- Asset statistics
- Business rule enforcement
"""

import pytest
from unittest.mock import Mock, MagicMock
from app.services.asset_service import AssetService
from app.models import AssetCondition, AssetStatus


class TestGetAssetsNeedingMaintenance:
    """Test retrieval of assets needing maintenance."""

    def test_get_assets_needing_maintenance_success(self):
        """Test successful retrieval of assets needing maintenance."""
        asset_repo = Mock()
        service = AssetService(asset_repo)

        mock_asset1 = Mock()
        mock_asset1.to_dict.return_value = {
            'id': 1,
            'name': 'Server A',
            'condition': 'poor'
        }

        mock_asset2 = Mock()
        mock_asset2.to_dict.return_value = {
            'id': 2,
            'name': 'Server B',
            'condition': 'critical'
        }

        asset_repo.get_assets_needing_maintenance.return_value = [mock_asset1, mock_asset2]

        result = service.get_assets_needing_maintenance()

        assert result['success'] is True
        assert len(result['data']) == 2
        assert 'Found 2 assets needing maintenance' in result['message']
        asset_repo.get_assets_needing_maintenance.assert_called_once()

    def test_get_assets_needing_maintenance_empty(self):
        """Test when no assets need maintenance."""
        asset_repo = Mock()
        asset_repo.get_assets_needing_maintenance.return_value = []

        service = AssetService(asset_repo)

        result = service.get_assets_needing_maintenance()

        assert result['success'] is True
        assert len(result['data']) == 0
        assert 'Found 0 assets needing maintenance' in result['message']

    def test_get_assets_needing_maintenance_exception(self):
        """Test exception handling."""
        asset_repo = Mock()
        asset_repo.get_assets_needing_maintenance.side_effect = Exception('Database error')

        service = AssetService(asset_repo)

        result = service.get_assets_needing_maintenance()

        assert result['success'] is False
        assert 'error' in result


class TestUpdateAssetCondition:
    """Test asset condition update functionality."""

    def test_update_asset_condition_success(self):
        """Test successful asset condition update."""
        from app.models import AssetCondition

        asset_repo = Mock()
        asset_repo.update_asset_condition.return_value = True

        # Mock the asset returned by get_by_id
        mock_asset_before = Mock()
        mock_asset_before.condition = AssetCondition.GOOD
        mock_asset_before.name = "Test Asset"

        mock_asset_after = Mock()
        mock_asset_after.to_dict.return_value = {'asset_id': 1, 'condition': 'poor', 'name': 'Test Asset'}

        asset_repo.get_by_id.side_effect = [mock_asset_before, mock_asset_after]

        service = AssetService(asset_repo)

        result = service.update_asset_condition(
            asset_id=1,
            new_condition='poor'
        )

        assert result['success'] is True
        assert result['data']['asset_id'] == 1
        assert result['data']['condition'] == 'poor'
        assert 'Asset condition updated' in result['message']
        asset_repo.update_asset_condition.assert_called_once()

    def test_update_asset_condition_all_valid_conditions(self):
        """Test update with all valid condition values."""
        from app.models import AssetCondition

        asset_repo = Mock()
        asset_repo.update_asset_condition.return_value = True

        service = AssetService(asset_repo)

        valid_conditions = ['excellent', 'good', 'fair', 'poor', 'critical']

        for condition in valid_conditions:
            # Mock asset for each iteration
            mock_asset_before = Mock()
            mock_asset_before.condition = AssetCondition.GOOD
            mock_asset_before.name = "Test Asset"

            mock_asset_after = Mock()
            mock_asset_after.to_dict.return_value = {'asset_id': 1, 'condition': condition}

            asset_repo.get_by_id.side_effect = [mock_asset_before, mock_asset_after]

            result = service.update_asset_condition(
                asset_id=1,
                new_condition=condition
            )
            assert result['success'] is True
            assert result['data']['condition'] == condition

    def test_update_asset_condition_case_insensitive(self):
        """Test condition update handles different cases."""
        asset_repo = Mock()
        asset_repo.update_asset_condition.return_value = True

        service = AssetService(asset_repo)

        # Test various cases
        for condition_input in ['poor', 'POOR', 'Poor', 'PoOr']:
            result = service.update_asset_condition(
                asset_id=1,
                new_condition=condition_input
            )
            assert result['success'] is True

            # Verify enum was passed to repository
            call_args = asset_repo.update_asset_condition.call_args[0]
            assert call_args[1] == AssetCondition.POOR

    def test_update_asset_condition_invalid_condition(self):
        """Test update fails with invalid condition."""
        asset_repo = Mock()
        service = AssetService(asset_repo)

        result = service.update_asset_condition(
            asset_id=1,
            new_condition='invalid_condition'
        )

        assert result['success'] is False
        assert 'Invalid condition' in result['error']
        asset_repo.update_asset_condition.assert_not_called()

    def test_update_asset_condition_asset_not_found(self):
        """Test update fails when asset doesn't exist."""
        asset_repo = Mock()
        asset_repo.update_asset_condition.return_value = False

        service = AssetService(asset_repo)

        result = service.update_asset_condition(
            asset_id=999,
            new_condition='poor'
        )

        assert result['success'] is False
        assert 'Asset not found' in result['error']

    def test_update_asset_condition_validation_errors(self):
        """Test validation of required fields."""
        asset_repo = Mock()
        service = AssetService(asset_repo)

        # Invalid asset_id (0 or negative)
        result = service.update_asset_condition(
            asset_id=0,
            new_condition='poor'
        )
        assert result['success'] is False

        result = service.update_asset_condition(
            asset_id=-5,
            new_condition='poor'
        )
        assert result['success'] is False

    def test_update_asset_condition_triggers_business_logic(self):
        """Test business rule: poor/critical conditions flag for maintenance."""
        asset_repo = Mock()
        asset_repo.update_asset_condition.return_value = True

        service = AssetService(asset_repo)

        # Update to poor condition
        result = service.update_asset_condition(
            asset_id=1,
            new_condition='poor'
        )

        assert result['success'] is True

        # Verify repository was called with correct enum
        call_args = asset_repo.update_asset_condition.call_args[0]
        assert call_args[0] == 1
        assert call_args[1] == AssetCondition.POOR

    def test_update_asset_condition_exception_handling(self):
        """Test exception handling during update."""
        asset_repo = Mock()
        asset_repo.update_asset_condition.side_effect = Exception('Database error')

        service = AssetService(asset_repo)

        result = service.update_asset_condition(
            asset_id=1,
            new_condition='poor'
        )

        assert result['success'] is False
        assert 'error' in result


class TestGetAssetStatistics:
    """Test asset statistics retrieval."""

    def test_get_asset_statistics_success(self):
        """Test successful statistics retrieval."""
        asset_repo = Mock()
        service = AssetService(asset_repo)

        mock_stats = {
            'total_assets': 50,
            'by_status': {
                'active': 40,
                'inactive': 5,
                'in_repair': 3,
                'retired': 2
            },
            'by_condition': {
                'excellent': 10,
                'good': 20,
                'fair': 12,
                'poor': 6,
                'critical': 2
            },
            'needs_maintenance': 8
        }

        asset_repo.get_asset_statistics.return_value = mock_stats

        result = service.get_asset_statistics()

        assert result['success'] is True
        assert result['data']['total_assets'] == 50
        assert result['data']['by_status']['active'] == 40
        assert result['data']['by_condition']['excellent'] == 10
        assert result['data']['needs_maintenance'] == 8
        asset_repo.get_asset_statistics.assert_called_once()

    def test_get_asset_statistics_empty_database(self):
        """Test statistics with no assets."""
        asset_repo = Mock()
        service = AssetService(asset_repo)

        empty_stats = {
            'total_assets': 0,
            'by_status': {},
            'by_condition': {},
            'needs_maintenance': 0
        }

        asset_repo.get_asset_statistics.return_value = empty_stats

        result = service.get_asset_statistics()

        assert result['success'] is True
        assert result['data']['total_assets'] == 0

    def test_get_asset_statistics_exception(self):
        """Test exception handling."""
        asset_repo = Mock()
        asset_repo.get_asset_statistics.side_effect = Exception('Database error')

        service = AssetService(asset_repo)

        result = service.get_asset_statistics()

        assert result['success'] is False
        assert 'error' in result


class TestAssetServiceIntegration:
    """Test service integration and business logic."""

    def test_service_uses_base_service_validation(self):
        """Test service inherits validation from BaseService."""
        asset_repo = Mock()
        service = AssetService(asset_repo)

        # Test positive number validation (inherited from BaseService)
        result = service.update_asset_condition(
            asset_id=-1,
            new_condition='poor'
        )

        assert result['success'] is False
        # BaseService validation should catch negative ID

    def test_service_uses_base_service_error_responses(self):
        """Test service uses BaseService response format."""
        asset_repo = Mock()
        asset_repo.update_asset_condition.return_value = True

        service = AssetService(asset_repo)

        result = service.update_asset_condition(
            asset_id=1,
            new_condition='poor'
        )

        # Verify response follows BaseService format
        assert 'success' in result
        assert 'data' in result
        assert 'message' in result

    def test_condition_enum_conversion(self):
        """Test proper conversion of condition strings to enums."""
        asset_repo = Mock()
        asset_repo.update_asset_condition.return_value = True

        service = AssetService(asset_repo)

        result = service.update_asset_condition(
            asset_id=1,
            new_condition='poor'
        )

        assert result['success'] is True

        # Verify enum was passed to repository, not string
        call_args = asset_repo.update_asset_condition.call_args[0]
        condition_arg = call_args[1]
        assert isinstance(condition_arg, AssetCondition)
        assert condition_arg == AssetCondition.POOR

    def test_repository_abstraction(self):
        """Test service properly abstracts repository operations."""
        asset_repo = Mock()
        service = AssetService(asset_repo)

        # Service should delegate to repository for data access
        service.get_assets_needing_maintenance()
        asset_repo.get_assets_needing_maintenance.assert_called_once()

        service.get_asset_statistics()
        asset_repo.get_asset_statistics.assert_called_once()

        service.update_asset_condition(1, 'poor')
        asset_repo.update_asset_condition.assert_called_once()


class TestBusinessRules:
    """Test asset service business rules."""

    def test_poor_and_critical_conditions_flagged_for_maintenance(self):
        """Test business rule: poor/critical assets should be tracked for maintenance."""
        asset_repo = Mock()

        poor_asset = Mock()
        poor_asset.to_dict.return_value = {'id': 1, 'condition': 'poor'}

        critical_asset = Mock()
        critical_asset.to_dict.return_value = {'id': 2, 'condition': 'critical'}

        asset_repo.get_assets_needing_maintenance.return_value = [poor_asset, critical_asset]

        service = AssetService(asset_repo)

        result = service.get_assets_needing_maintenance()

        assert result['success'] is True
        assert len(result['data']) == 2

        # Verify both poor and critical conditions are included
        conditions = [asset['condition'] for asset in result['data']]
        assert 'poor' in conditions
        assert 'critical' in conditions

    def test_condition_update_logging(self):
        """Test that condition updates are logged."""
        asset_repo = Mock()
        asset_repo.update_asset_condition.return_value = True

        service = AssetService(asset_repo)

        # Update condition
        result = service.update_asset_condition(
            asset_id=1,
            new_condition='poor'
        )

        assert result['success'] is True
        # Service should log the action (via BaseService._log_action)

    def test_asset_statistics_provide_actionable_insights(self):
        """Test statistics provide useful business insights."""
        asset_repo = Mock()
        service = AssetService(asset_repo)

        mock_stats = {
            'total_assets': 100,
            'by_status': {
                'active': 80,
                'in_repair': 10,
                'inactive': 5,
                'retired': 5
            },
            'by_condition': {
                'excellent': 20,
                'good': 40,
                'fair': 20,
                'poor': 15,
                'critical': 5
            },
            'needs_maintenance': 20
        }

        asset_repo.get_asset_statistics.return_value = mock_stats

        result = service.get_asset_statistics()

        assert result['success'] is True

        # Statistics should provide:
        # 1. Overall asset count
        assert result['data']['total_assets'] == 100

        # 2. Status breakdown for operational insights
        assert result['data']['by_status']['active'] == 80
        assert result['data']['by_status']['in_repair'] == 10

        # 3. Condition breakdown for maintenance planning
        assert result['data']['by_condition']['poor'] == 15
        assert result['data']['by_condition']['critical'] == 5

        # 4. Maintenance flagged assets (actionable)
        assert result['data']['needs_maintenance'] == 20

    def test_condition_transition_validates_enum(self):
        """Test condition transitions are validated through enum."""
        asset_repo = Mock()
        service = AssetService(asset_repo)

        # Valid conditions should succeed
        valid_conditions = ['excellent', 'good', 'fair', 'poor', 'critical']
        asset_repo.update_asset_condition.return_value = True

        for condition in valid_conditions:
            result = service.update_asset_condition(
                asset_id=1,
                new_condition=condition
            )
            assert result['success'] is True

        # Invalid conditions should fail
        invalid_conditions = ['broken', 'damaged', 'ok', 'bad']

        for condition in invalid_conditions:
            result = service.update_asset_condition(
                asset_id=1,
                new_condition=condition
            )
            assert result['success'] is False
            assert 'Invalid condition' in result['error']


class TestServiceLayerPattern:
    """Test Service Layer pattern implementation."""

    def test_service_encapsulates_business_logic(self):
        """Test service encapsulates business logic, not just pass-through."""
        asset_repo = Mock()
        service = AssetService(asset_repo)

        # Service adds business logic on top of repository:
        # 1. Validation (asset_id must be positive)
        result = service.update_asset_condition(
            asset_id=-1,
            new_condition='poor'
        )
        assert result['success'] is False

        # 2. Enum conversion (string -> AssetCondition enum)
        asset_repo.update_asset_condition.return_value = True
        result = service.update_asset_condition(
            asset_id=1,
            new_condition='poor'
        )
        call_args = asset_repo.update_asset_condition.call_args[0]
        assert isinstance(call_args[1], AssetCondition)

        # 3. Consistent response format (success/error/data/message)
        assert 'success' in result
        assert 'data' in result
        assert 'message' in result

    def test_service_handles_repository_failures(self):
        """Test service gracefully handles repository failures."""
        asset_repo = Mock()
        asset_repo.get_assets_needing_maintenance.side_effect = Exception('DB connection lost')

        service = AssetService(asset_repo)

        result = service.get_assets_needing_maintenance()

        # Service should catch exception and return error response
        assert result['success'] is False
        assert 'error' in result

    def test_service_provides_consistent_interface(self):
        """Test all service methods return consistent response format."""
        asset_repo = Mock()
        asset_repo.get_assets_needing_maintenance.return_value = []
        asset_repo.update_asset_condition.return_value = True
        asset_repo.get_asset_statistics.return_value = {'total_assets': 0}

        service = AssetService(asset_repo)

        # All methods should return dict with 'success' key
        result1 = service.get_assets_needing_maintenance()
        result2 = service.update_asset_condition(1, 'poor')
        result3 = service.get_asset_statistics()

        for result in [result1, result2, result3]:
            assert isinstance(result, dict)
            assert 'success' in result
