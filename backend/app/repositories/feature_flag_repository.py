"""
Feature Flag Repository

Data access layer for feature flags.
"""

from typing import List, Optional
from app.database import db
from app.models.feature_flag import FeatureFlag


class FeatureFlagRepository:
    """
    Repository for feature flag operations.

    Provides CRUD operations and query methods for feature flags.
    """

    def get_all(self) -> List[FeatureFlag]:
        """
        Get all feature flags.

        Returns:
            List[FeatureFlag]: All feature flags in the system
        """
        return FeatureFlag.query.all()

    def get_enabled(self) -> List[FeatureFlag]:
        """
        Get all enabled feature flags.

        Returns:
            List[FeatureFlag]: All enabled feature flags
        """
        return FeatureFlag.query.filter_by(enabled=True).all()

    def get_by_id(self, flag_id: int) -> Optional[FeatureFlag]:
        """
        Get feature flag by ID.

        Args:
            flag_id: Feature flag ID

        Returns:
            Optional[FeatureFlag]: Feature flag if found, None otherwise
        """
        return FeatureFlag.query.filter_by(id=flag_id).first()

    def get_by_key(self, feature_key: str) -> Optional[FeatureFlag]:
        """
        Get feature flag by key.

        Args:
            feature_key: Feature key (e.g., 'advanced_reporting')

        Returns:
            Optional[FeatureFlag]: Feature flag if found, None otherwise
        """
        return FeatureFlag.query.filter_by(feature_key=feature_key).first()

    def is_enabled(self, feature_key: str, user_id: Optional[int] = None) -> bool:
        """
        Check if a feature is enabled.

        Args:
            feature_key: Feature key to check
            user_id: Optional user ID for rollout percentage calculation

        Returns:
            bool: True if feature is enabled, False otherwise
        """
        flag = self.get_by_key(feature_key)
        if not flag:
            return False  # Unknown features are disabled by default

        return flag.is_enabled_for_user(user_id)

    def create(self, feature_flag: FeatureFlag) -> FeatureFlag:
        """
        Create a new feature flag.

        Args:
            feature_flag: FeatureFlag instance to create

        Returns:
            FeatureFlag: Created feature flag
        """
        db.session.add(feature_flag)
        db.session.commit()
        db.session.refresh(feature_flag)
        return feature_flag

    def update(self, flag_id: int, **kwargs) -> Optional[FeatureFlag]:
        """
        Update a feature flag.

        Args:
            flag_id: Feature flag ID
            **kwargs: Fields to update

        Returns:
            Optional[FeatureFlag]: Updated feature flag if found
        """
        flag = self.get_by_id(flag_id)
        if not flag:
            return None

        # Update allowed fields
        allowed_fields = {'name', 'description', 'category', 'enabled',
                         'rollout_percentage', 'config_data'}
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(flag, key, value)

        db.session.commit()
        db.session.refresh(flag)
        return flag

    def toggle(self, flag_id: int) -> Optional[FeatureFlag]:
        """
        Toggle a feature flag on/off.

        Args:
            flag_id: Feature flag ID

        Returns:
            Optional[FeatureFlag]: Updated feature flag if found
        """
        flag = self.get_by_id(flag_id)
        if not flag:
            return None

        flag.enabled = not flag.enabled
        db.session.commit()
        db.session.refresh(flag)
        return flag

    def delete(self, flag_id: int) -> bool:
        """
        Delete a feature flag.

        Args:
            flag_id: Feature flag ID

        Returns:
            bool: True if deleted, False if not found
        """
        flag = self.get_by_id(flag_id)
        if not flag:
            return False

        db.session.delete(flag)
        db.session.commit()
        return True

    def bulk_create(self, feature_flags: List[FeatureFlag]) -> List[FeatureFlag]:
        """
        Create multiple feature flags at once.

        Args:
            feature_flags: List of FeatureFlag instances

        Returns:
            List[FeatureFlag]: Created feature flags
        """
        for flag in feature_flags:
            db.session.add(flag)

        db.session.commit()

        for flag in feature_flags:
            db.session.refresh(flag)

        return feature_flags
