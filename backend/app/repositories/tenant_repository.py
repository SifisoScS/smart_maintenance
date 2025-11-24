"""
Tenant Repository
Handles database operations for tenants
"""

from typing import Optional, List
from sqlalchemy.exc import SQLAlchemyError
from app.repositories.base_repository import BaseRepository
from app.models.tenant import Tenant, TenantStatus
from app.database import db


class TenantRepository(BaseRepository):
    """
    Repository for Tenant model operations.

    Provides tenant-specific database operations beyond base CRUD:
    - Subdomain management
    - Tenant activation/suspension
    - Active tenant filtering
    """

    def __init__(self):
        """Initialize repository with Tenant model"""
        super().__init__(Tenant)

    def get_by_subdomain(self, subdomain: str) -> Optional[Tenant]:
        """
        Get tenant by subdomain.

        Args:
            subdomain: Tenant subdomain (e.g., 'acme')

        Returns:
            Tenant instance or None if not found
        """
        return self.get_one_by_filter(subdomain=subdomain)

    def check_subdomain_available(self, subdomain: str) -> bool:
        """
        Check if subdomain is available for registration.

        Args:
            subdomain: Subdomain to check

        Returns:
            True if subdomain is available, False if taken
        """
        return self.get_by_subdomain(subdomain) is None

    def get_active_tenants(self) -> List[Tenant]:
        """
        Get all active tenants.

        Returns:
            List of tenants with is_active=True
        """
        return self.get_by_filter(is_active=True)

    def get_by_status(self, status: str) -> List[Tenant]:
        """
        Get tenants by status.

        Args:
            status: Tenant status (active, suspended, trial, cancelled)

        Returns:
            List of tenants with given status
        """
        return self.get_by_filter(status=status)

    def get_by_plan(self, plan: str) -> List[Tenant]:
        """
        Get tenants by subscription plan.

        Args:
            plan: Subscription plan (free, basic, premium, enterprise)

        Returns:
            List of tenants on given plan
        """
        return self.get_by_filter(plan=plan)

    def suspend_tenant(self, tenant_id: int, reason: Optional[str] = None) -> Optional[Tenant]:
        """
        Suspend a tenant account.

        Args:
            tenant_id: ID of tenant to suspend
            reason: Optional reason for suspension

        Returns:
            Updated tenant instance or None if not found

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            tenant = self.get_by_id(tenant_id)
            if not tenant:
                return None

            tenant.status = TenantStatus.SUSPENDED
            tenant.is_active = False

            # Store suspension reason in settings
            if reason:
                if tenant.settings is None:
                    tenant.settings = {}
                tenant.settings['suspension_reason'] = reason
                tenant.settings['suspended_at'] = db.func.now()

            db.session.commit()
            db.session.refresh(tenant)
            return tenant

        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error suspending tenant: {str(e)}")

    def activate_tenant(self, tenant_id: int) -> Optional[Tenant]:
        """
        Activate a suspended or trial tenant.

        Args:
            tenant_id: ID of tenant to activate

        Returns:
            Updated tenant instance or None if not found

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            tenant = self.get_by_id(tenant_id)
            if not tenant:
                return None

            tenant.status = TenantStatus.ACTIVE
            tenant.is_active = True

            # Remove suspension reason from settings
            if tenant.settings and 'suspension_reason' in tenant.settings:
                del tenant.settings['suspension_reason']
                if 'suspended_at' in tenant.settings:
                    del tenant.settings['suspended_at']

            db.session.commit()
            db.session.refresh(tenant)
            return tenant

        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error activating tenant: {str(e)}")

    def cancel_tenant(self, tenant_id: int, reason: Optional[str] = None) -> Optional[Tenant]:
        """
        Cancel a tenant account (soft delete).

        Args:
            tenant_id: ID of tenant to cancel
            reason: Optional reason for cancellation

        Returns:
            Updated tenant instance or None if not found

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            tenant = self.get_by_id(tenant_id)
            if not tenant:
                return None

            tenant.status = TenantStatus.CANCELLED
            tenant.is_active = False

            # Store cancellation reason in settings
            if reason:
                if tenant.settings is None:
                    tenant.settings = {}
                tenant.settings['cancellation_reason'] = reason
                tenant.settings['cancelled_at'] = db.func.now()

            db.session.commit()
            db.session.refresh(tenant)
            return tenant

        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error cancelling tenant: {str(e)}")

    def search_tenants(self, query: str, limit: int = 20) -> List[Tenant]:
        """
        Search tenants by name or subdomain.

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of matching tenants
        """
        search_pattern = f"%{query}%"
        return db.session.query(Tenant).filter(
            db.or_(
                Tenant.name.ilike(search_pattern),
                Tenant.subdomain.ilike(search_pattern),
                Tenant.billing_email.ilike(search_pattern)
            )
        ).limit(limit).all()

    def get_expired_trials(self) -> List[Tenant]:
        """
        Get tenants with expired trial periods.

        Returns:
            List of tenants where trial_ends < now()
        """
        from datetime import datetime
        return db.session.query(Tenant).filter(
            Tenant.status == TenantStatus.TRIAL,
            Tenant.trial_ends < datetime.utcnow()
        ).all()

    def get_expiring_subscriptions(self, days: int = 7) -> List[Tenant]:
        """
        Get tenants with subscriptions expiring soon.

        Args:
            days: Number of days ahead to check

        Returns:
            List of tenants with subscriptions expiring within specified days
        """
        from datetime import datetime, timedelta
        expiry_threshold = datetime.utcnow() + timedelta(days=days)

        return db.session.query(Tenant).filter(
            Tenant.subscription_expires.isnot(None),
            Tenant.subscription_expires <= expiry_threshold,
            Tenant.subscription_expires > datetime.utcnow()
        ).all()

    def update_branding(self, tenant_id: int, logo_url: Optional[str] = None,
                       primary_color: Optional[str] = None,
                       secondary_color: Optional[str] = None) -> Optional[Tenant]:
        """
        Update tenant branding settings.

        Args:
            tenant_id: ID of tenant to update
            logo_url: URL to tenant logo
            primary_color: Primary brand color (hex)
            secondary_color: Secondary brand color (hex)

        Returns:
            Updated tenant instance or None if not found

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            tenant = self.get_by_id(tenant_id)
            if not tenant:
                return None

            if logo_url is not None:
                tenant.logo_url = logo_url
            if primary_color is not None:
                tenant.primary_color = primary_color
            if secondary_color is not None:
                tenant.secondary_color = secondary_color

            db.session.commit()
            db.session.refresh(tenant)
            return tenant

        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error updating tenant branding: {str(e)}")
