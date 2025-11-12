"""
Feature Flag Service

Business logic layer for feature flag management.
"""

import logging
from typing import List, Optional, Dict, Any
from app.repositories.feature_flag_repository import FeatureFlagRepository
from app.models.feature_flag import FeatureFlag, FeatureCategory

logger = logging.getLogger(__name__)


class FeatureFlagService:
    """
    Service for managing feature flags.

    Provides business logic for enabling/disabling features,
    checking feature availability, and managing flag lifecycle.
    """

    def __init__(self, repository: Optional[FeatureFlagRepository] = None):
        """
        Initialize feature flag service.

        Args:
            repository: Optional FeatureFlagRepository instance
        """
        self.repository = repository or FeatureFlagRepository()

    def is_enabled(self, feature_key: str, user_id: Optional[int] = None) -> bool:
        """
        Check if a feature is enabled.

        Args:
            feature_key: Feature key to check
            user_id: Optional user ID for rollout percentage calculation

        Returns:
            bool: True if feature is enabled for this user/context

        Example:
            >>> service = FeatureFlagService()
            >>> if service.is_enabled('advanced_reporting', user_id=5):
            >>>     # Show advanced reporting UI
            >>>     pass
        """
        return self.repository.is_enabled(feature_key, user_id)

    def get_all_flags(self) -> Dict[str, Any]:
        """
        Get all feature flags.

        Returns:
            Dict containing:
                - success: bool
                - data: List of feature flags
                - total: int
        """
        try:
            flags = self.repository.get_all()
            return {
                'success': True,
                'data': [flag.to_dict() for flag in flags],
                'total': len(flags)
            }
        except Exception as e:
            logger.error(f"Error getting all flags: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'data': []
            }

    def get_enabled_flags(self) -> Dict[str, Any]:
        """
        Get all enabled feature flags.

        Returns:
            Dict containing enabled flags
        """
        try:
            flags = self.repository.get_enabled()
            return {
                'success': True,
                'data': [flag.to_dict() for flag in flags],
                'total': len(flags)
            }
        except Exception as e:
            logger.error(f"Error getting enabled flags: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'data': []
            }

    def get_flag_by_key(self, feature_key: str) -> Dict[str, Any]:
        """
        Get feature flag by key.

        Args:
            feature_key: Feature key

        Returns:
            Dict containing flag data or error
        """
        try:
            flag = self.repository.get_by_key(feature_key)
            if not flag:
                return {
                    'success': False,
                    'error': f"Feature flag '{feature_key}' not found"
                }

            return {
                'success': True,
                'data': flag.to_dict()
            }
        except Exception as e:
            logger.error(f"Error getting flag {feature_key}: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def create_flag(self, feature_key: str, name: str, description: str = None,
                   category: FeatureCategory = FeatureCategory.EXPERIMENTAL,
                   enabled: bool = False, rollout_percentage: int = 100,
                   config_data: dict = None) -> Dict[str, Any]:
        """
        Create a new feature flag.

        Args:
            feature_key: Unique feature identifier
            name: Human-readable name
            description: What the feature does
            category: Feature category
            enabled: Whether to enable immediately
            rollout_percentage: Percentage of users to enable for (0-100)
            config_data: Additional configuration

        Returns:
            Dict with success status and created flag data
        """
        try:
            # Check if already exists
            existing = self.repository.get_by_key(feature_key)
            if existing:
                return {
                    'success': False,
                    'error': f"Feature flag '{feature_key}' already exists"
                }

            # Create new flag
            flag = FeatureFlag(
                feature_key=feature_key,
                name=name,
                description=description,
                category=category,
                enabled=enabled,
                rollout_percentage=rollout_percentage,
                config_data=config_data
            )

            created_flag = self.repository.create(flag)

            logger.info(f"Created feature flag: {feature_key} (enabled={enabled})")

            return {
                'success': True,
                'data': created_flag.to_dict(),
                'message': f"Feature flag '{feature_key}' created successfully"
            }

        except Exception as e:
            logger.error(f"Error creating flag {feature_key}: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def update_flag(self, flag_id: int, **kwargs) -> Dict[str, Any]:
        """
        Update a feature flag.

        Args:
            flag_id: Feature flag ID
            **kwargs: Fields to update

        Returns:
            Dict with success status and updated flag data
        """
        try:
            updated_flag = self.repository.update(flag_id, **kwargs)

            if not updated_flag:
                return {
                    'success': False,
                    'error': f"Feature flag with ID {flag_id} not found"
                }

            logger.info(f"Updated feature flag: {updated_flag.feature_key}")

            return {
                'success': True,
                'data': updated_flag.to_dict(),
                'message': "Feature flag updated successfully"
            }

        except Exception as e:
            logger.error(f"Error updating flag {flag_id}: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def toggle_flag(self, flag_id: int) -> Dict[str, Any]:
        """
        Toggle a feature flag on/off.

        Args:
            flag_id: Feature flag ID

        Returns:
            Dict with success status and updated flag data
        """
        try:
            toggled_flag = self.repository.toggle(flag_id)

            if not toggled_flag:
                return {
                    'success': False,
                    'error': f"Feature flag with ID {flag_id} not found"
                }

            status = "enabled" if toggled_flag.enabled else "disabled"
            logger.info(f"Toggled feature flag {toggled_flag.feature_key}: {status}")

            return {
                'success': True,
                'data': toggled_flag.to_dict(),
                'message': f"Feature flag {status} successfully"
            }

        except Exception as e:
            logger.error(f"Error toggling flag {flag_id}: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def delete_flag(self, flag_id: int) -> Dict[str, Any]:
        """
        Delete a feature flag.

        Args:
            flag_id: Feature flag ID

        Returns:
            Dict with success status
        """
        try:
            deleted = self.repository.delete(flag_id)

            if not deleted:
                return {
                    'success': False,
                    'error': f"Feature flag with ID {flag_id} not found"
                }

            logger.info(f"Deleted feature flag with ID {flag_id}")

            return {
                'success': True,
                'message': "Feature flag deleted successfully"
            }

        except Exception as e:
            logger.error(f"Error deleting flag {flag_id}: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def get_flags_by_category(self, category: FeatureCategory) -> Dict[str, Any]:
        """
        Get feature flags by category.

        Args:
            category: Feature category

        Returns:
            Dict containing flags in the category
        """
        try:
            all_flags = self.repository.get_all()
            category_flags = [f for f in all_flags if f.category == category]

            return {
                'success': True,
                'data': [flag.to_dict() for flag in category_flags],
                'total': len(category_flags)
            }
        except Exception as e:
            logger.error(f"Error getting flags for category {category}: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
