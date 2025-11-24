"""
Tenant Service
Business logic for tenant management and provisioning
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
from app.repositories.tenant_repository import TenantRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.permission_repository import PermissionRepository
from app.repositories.user_repository import UserRepository
from app.models.tenant import Tenant, TenantStatus, SubscriptionPlan, SUBSCRIPTION_PLANS
from app.models.tenant_subscription import TenantSubscription, SubscriptionStatus, BillingCycle
from app.database import db


class TenantService:
    """
    Service layer for tenant operations.

    Handles:
    - Tenant provisioning (creating new tenants with default setup)
    - Subscription management
    - Plan limit enforcement
    - Tenant lifecycle (activation, suspension, cancellation)
    """

    def __init__(self, tenant_repo: Optional[TenantRepository] = None,
                 role_repo: Optional[RoleRepository] = None,
                 permission_repo: Optional[PermissionRepository] = None,
                 user_repo: Optional[UserRepository] = None):
        """
        Initialize service with repositories.

        Args:
            tenant_repo: Tenant repository (injected for testability)
            role_repo: Role repository for provisioning
            permission_repo: Permission repository for provisioning
            user_repo: User repository for provisioning
        """
        self.tenant_repo = tenant_repo or TenantRepository()
        self.role_repo = role_repo or RoleRepository()
        self.permission_repo = permission_repo or PermissionRepository()
        self.user_repo = user_repo or UserRepository()

    def provision_tenant(self, name: str, subdomain: str,
                        admin_email: str, admin_password: str,
                        admin_first_name: str, admin_last_name: str,
                        plan: str = SubscriptionPlan.FREE,
                        billing_email: Optional[str] = None,
                        contact_name: Optional[str] = None,
                        contact_phone: Optional[str] = None) -> Dict:
        """
        Provision a new tenant with complete setup.

        Creates:
        - Tenant record
        - Admin user
        - Default roles (Admin, Technician, Client)
        - Permissions assigned to roles
        - Initial subscription record

        Args:
            name: Organization name
            subdomain: Tenant subdomain (must be unique)
            admin_email: Admin user email
            admin_password: Admin user password
            admin_first_name: Admin first name
            admin_last_name: Admin last name
            plan: Subscription plan
            billing_email: Billing contact email
            contact_name: Primary contact name
            contact_phone: Contact phone number

        Returns:
            Dict with tenant, admin user, and subscription details

        Raises:
            ValueError: If subdomain is taken or validation fails
            Exception: If provisioning fails
        """
        try:
            # 1. Validate subdomain availability
            if not self.tenant_repo.check_subdomain_available(subdomain):
                raise ValueError(f"Subdomain '{subdomain}' is already taken")

            # 2. Get plan details
            plan_details = SUBSCRIPTION_PLANS.get(plan)
            if not plan_details:
                raise ValueError(f"Invalid plan: {plan}")

            # 3. Create tenant
            trial_duration = plan_details.get('duration_days', 14)
            tenant = Tenant(
                name=name,
                subdomain=subdomain,
                status=TenantStatus.TRIAL,
                plan=plan,
                max_users=plan_details['max_users'],
                max_assets=plan_details['max_assets'],
                max_requests_per_month=plan_details['max_requests_per_month'],
                billing_email=billing_email or admin_email,
                contact_name=contact_name or f"{admin_first_name} {admin_last_name}",
                contact_phone=contact_phone,
                is_active=True,
                onboarded=False
            )

            # Set trial period
            tenant.trial_ends = datetime.utcnow() + timedelta(days=trial_duration)

            db.session.add(tenant)
            db.session.flush()  # Get tenant.id without committing

            # 4. Create admin user for this tenant
            from app.models.user import User, UserRole
            admin_user = User(
                email=admin_email,
                first_name=admin_first_name,
                last_name=admin_last_name,
                role=UserRole.ADMIN,
                is_active=True,
                tenant_id=tenant.id
            )
            admin_user.set_password(admin_password)
            admin_user.validate()

            db.session.add(admin_user)
            db.session.flush()  # Get admin_user.id

            # 5. Create default roles for this tenant
            roles_created = self._create_default_roles(tenant.id)

            # 6. Assign Super Admin role to admin user
            super_admin_role = next((r for r in roles_created if r.name == 'Super Admin'), None)
            if super_admin_role:
                admin_user.roles.append(super_admin_role)

            # 7. Create subscription record
            subscription = TenantSubscription(
                tenant_id=tenant.id,
                plan=plan,
                status=SubscriptionStatus.ACTIVE,
                billing_cycle=BillingCycle.MONTHLY,
                price=plan_details['price'],
                currency='USD',
                trial_start=datetime.utcnow(),
                trial_end=tenant.trial_ends
            )

            db.session.add(subscription)

            # Commit all changes
            db.session.commit()

            return {
                'tenant': tenant.to_dict(),
                'admin_user': admin_user.to_dict(),
                'subscription': subscription.to_dict(),
                'roles_created': [r.name for r in roles_created],
                'message': f'Tenant "{name}" provisioned successfully with {trial_duration}-day trial'
            }

        except ValueError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to provision tenant: {str(e)}")

    def _create_default_roles(self, tenant_id: int) -> List:
        """
        Create default roles for a new tenant.

        Creates:
        - Super Admin (all permissions)
        - Technician (maintenance operations)
        - Client (submit requests, view own data)

        Args:
            tenant_id: ID of tenant to create roles for

        Returns:
            List of created Role instances
        """
        from app.models.role import Role
        from app.models.permission import Permission

        # Define default roles
        default_roles = [
            {
                'name': 'Super Admin',
                'description': 'Full system access for tenant administrators',
                'is_system': True,
                'permissions': [
                    'view_users', 'create_users', 'edit_users', 'delete_users',
                    'view_roles', 'create_roles', 'edit_roles', 'delete_roles',
                    'view_permissions', 'assign_permissions',
                    'view_requests', 'create_requests', 'edit_requests', 'delete_requests',
                    'assign_requests', 'complete_requests',
                    'view_assets', 'create_assets', 'edit_assets', 'delete_assets',
                    'view_dashboard', 'view_reports', 'export_data',
                    'manage_tenant', 'view_billing', 'manage_subscription'
                ]
            },
            {
                'name': 'Technician',
                'description': 'Maintenance technician with work management access',
                'is_system': True,
                'permissions': [
                    'view_requests', 'edit_requests', 'complete_requests',
                    'view_assets', 'edit_assets',
                    'view_dashboard'
                ]
            },
            {
                'name': 'Client',
                'description': 'Standard user who can submit maintenance requests',
                'is_system': True,
                'permissions': [
                    'view_requests', 'create_requests',
                    'view_assets',
                    'view_dashboard'
                ]
            }
        ]

        roles_created = []

        for role_data in default_roles:
            # Create role
            role = Role(
                name=role_data['name'],
                description=role_data['description'],
                is_system=role_data['is_system'],
                tenant_id=tenant_id
            )
            db.session.add(role)
            db.session.flush()  # Get role.id

            # Create and assign permissions
            for perm_name in role_data['permissions']:
                # Check if permission already exists for this tenant
                permission = Permission.query.filter_by(
                    name=perm_name,
                    tenant_id=tenant_id
                ).first()

                if not permission:
                    # Parse permission name to get resource and action
                    parts = perm_name.split('_', 1)
                    if len(parts) == 2:
                        action, resource = parts
                    else:
                        action, resource = 'view', perm_name

                    # Create permission for this tenant
                    permission = Permission(
                        name=perm_name,
                        description=f'{action.capitalize()} {resource}',
                        resource=resource,
                        action=action,
                        tenant_id=tenant_id
                    )
                    db.session.add(permission)
                    db.session.flush()

                # Assign to role
                role.permissions.append(permission)

            roles_created.append(role)

        return roles_created

    def upgrade_subscription(self, tenant_id: int, new_plan: str,
                            billing_cycle: str = BillingCycle.MONTHLY,
                            stripe_subscription_id: Optional[str] = None) -> Dict:
        """
        Upgrade tenant subscription to a new plan.

        Args:
            tenant_id: Tenant ID
            new_plan: New subscription plan
            billing_cycle: Billing cycle (monthly/annual)
            stripe_subscription_id: Stripe subscription ID

        Returns:
            Dict with updated tenant and subscription info

        Raises:
            ValueError: If tenant not found or invalid plan
        """
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")

        plan_details = SUBSCRIPTION_PLANS.get(new_plan)
        if not plan_details:
            raise ValueError(f"Invalid plan: {new_plan}")

        try:
            # Update tenant
            tenant.plan = new_plan
            tenant.status = TenantStatus.ACTIVE
            tenant.max_users = plan_details['max_users']
            tenant.max_assets = plan_details['max_assets']
            tenant.max_requests_per_month = plan_details['max_requests_per_month']

            # Update or create subscription
            subscription = TenantSubscription.query.filter_by(
                tenant_id=tenant_id,
                status=SubscriptionStatus.ACTIVE
            ).first()

            if subscription:
                subscription.plan = new_plan
                subscription.billing_cycle = billing_cycle
                subscription.price = plan_details['price']
                subscription.status = SubscriptionStatus.ACTIVE
                if stripe_subscription_id:
                    subscription.stripe_subscription_id = stripe_subscription_id
            else:
                subscription = TenantSubscription(
                    tenant_id=tenant_id,
                    plan=new_plan,
                    status=SubscriptionStatus.ACTIVE,
                    billing_cycle=billing_cycle,
                    price=plan_details['price'],
                    current_period_start=datetime.utcnow(),
                    current_period_end=datetime.utcnow() + timedelta(days=30),
                    stripe_subscription_id=stripe_subscription_id
                )
                db.session.add(subscription)

            db.session.commit()

            return {
                'tenant': tenant.to_dict(),
                'subscription': subscription.to_dict(),
                'message': f'Subscription upgraded to {new_plan}'
            }

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to upgrade subscription: {str(e)}")

    def check_plan_limits(self, tenant_id: int, resource: str, count: int = 1) -> Dict:
        """
        Check if tenant can add more of a resource based on plan limits.

        Args:
            tenant_id: Tenant ID
            resource: Resource type ('users', 'assets', 'requests')
            count: Number of resources to add (default 1)

        Returns:
            Dict with 'allowed' boolean and 'message' string
        """
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            return {'allowed': False, 'message': 'Tenant not found'}

        stats = tenant.get_usage_stats()
        resource_stats = stats.get(resource, {})

        if resource == 'users':
            if tenant.max_users is None:  # Unlimited
                return {'allowed': True, 'message': 'Unlimited users'}
            if resource_stats['current'] + count > tenant.max_users:
                return {
                    'allowed': False,
                    'message': f'User limit reached ({tenant.max_users}). Upgrade plan to add more users.'
                }
            return {'allowed': True, 'message': f'{resource_stats["remaining"]} users remaining'}

        elif resource == 'assets':
            if tenant.max_assets is None:
                return {'allowed': True, 'message': 'Unlimited assets'}
            if resource_stats['current'] + count > tenant.max_assets:
                return {
                    'allowed': False,
                    'message': f'Asset limit reached ({tenant.max_assets}). Upgrade plan to add more assets.'
                }
            return {'allowed': True, 'message': f'{resource_stats["remaining"]} assets remaining'}

        elif resource == 'requests':
            if tenant.max_requests_per_month is None:
                return {'allowed': True, 'message': 'Unlimited requests'}
            if resource_stats['current'] + count > tenant.max_requests_per_month:
                return {
                    'allowed': False,
                    'message': f'Monthly request limit reached ({tenant.max_requests_per_month}). Upgrade plan or wait for next cycle.'
                }
            return {'allowed': True, 'message': f'{resource_stats["remaining"]} requests remaining this month'}

        return {'allowed': True, 'message': 'Unknown resource'}

    def suspend_tenant(self, tenant_id: int, reason: Optional[str] = None) -> Dict:
        """Suspend a tenant account"""
        tenant = self.tenant_repo.suspend_tenant(tenant_id, reason)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")

        return {
            'tenant': tenant.to_dict(),
            'message': f'Tenant suspended: {reason or "No reason provided"}'
        }

    def activate_tenant(self, tenant_id: int) -> Dict:
        """Activate a suspended tenant"""
        tenant = self.tenant_repo.activate_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")

        return {
            'tenant': tenant.to_dict(),
            'message': 'Tenant activated successfully'
        }

    def cancel_tenant(self, tenant_id: int, reason: Optional[str] = None) -> Dict:
        """Cancel a tenant account"""
        tenant = self.tenant_repo.cancel_tenant(tenant_id, reason)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")

        return {
            'tenant': tenant.to_dict(),
            'message': f'Tenant cancelled: {reason or "No reason provided"}'
        }

    def get_tenant_by_subdomain(self, subdomain: str) -> Optional[Tenant]:
        """Get tenant by subdomain"""
        return self.tenant_repo.get_by_subdomain(subdomain)

    def get_tenant_by_id(self, tenant_id: int) -> Optional[Tenant]:
        """Get tenant by ID"""
        return self.tenant_repo.get_by_id(tenant_id)

    def list_tenants(self, status: Optional[str] = None,
                    plan: Optional[str] = None,
                    limit: Optional[int] = None) -> List[Tenant]:
        """
        List tenants with optional filters.

        Args:
            status: Filter by status
            plan: Filter by plan
            limit: Maximum results

        Returns:
            List of tenants
        """
        if status:
            return self.tenant_repo.get_by_status(status)
        elif plan:
            return self.tenant_repo.get_by_plan(plan)
        else:
            return self.tenant_repo.get_all(limit=limit)

    def search_tenants(self, query: str, limit: int = 20) -> List[Tenant]:
        """Search tenants by name, subdomain, or email"""
        return self.tenant_repo.search_tenants(query, limit)

    def update_branding(self, tenant_id: int, logo_url: Optional[str] = None,
                       primary_color: Optional[str] = None,
                       secondary_color: Optional[str] = None) -> Dict:
        """Update tenant branding"""
        tenant = self.tenant_repo.update_branding(
            tenant_id, logo_url, primary_color, secondary_color
        )
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")

        return {
            'tenant': tenant.to_dict(),
            'message': 'Branding updated successfully'
        }

    def handle_expired_trials(self) -> Dict:
        """
        Process expired trial accounts.

        Suspends tenants with expired trials that haven't upgraded.
        Should be run as a scheduled task (e.g., daily cron job).

        Returns:
            Dict with count of tenants processed
        """
        expired_tenants = self.tenant_repo.get_expired_trials()
        suspended_count = 0

        for tenant in expired_tenants:
            try:
                self.tenant_repo.suspend_tenant(
                    tenant.id,
                    reason="Trial period expired"
                )
                suspended_count += 1
            except Exception as e:
                # Log error but continue processing
                print(f"Error suspending tenant {tenant.id}: {str(e)}")

        return {
            'total_expired': len(expired_tenants),
            'suspended': suspended_count,
            'message': f'Processed {len(expired_tenants)} expired trials, suspended {suspended_count}'
        }
