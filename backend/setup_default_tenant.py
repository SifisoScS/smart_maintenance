"""
Setup Default Tenant Script

Creates a default tenant and assigns all existing data to it.
This is a one-time migration script for converting from single-tenant to multi-tenant.
"""

from app import create_app
from app.database import db
from app.models.tenant import Tenant, TenantStatus, SubscriptionPlan

def setup_default_tenant():
    """Create default tenant and assign existing data"""
    app = create_app()

    with app.app_context():
        print("\n" + "="*60)
        print("Setting Up Default Tenant")
        print("="*60 + "\n")

        # Check if default tenant already exists
        existing_tenant = Tenant.query.filter_by(subdomain='app').first()
        if existing_tenant:
            print(f"[OK] Default tenant already exists: {existing_tenant.name}")
            print(f"  ID: {existing_tenant.id}")
            print(f"  Subdomain: {existing_tenant.subdomain}")
            print(f"  Status: {existing_tenant.status}")
            print(f"  Plan: {existing_tenant.plan}")
            default_tenant_id = existing_tenant.id
        else:
            # Create default tenant
            print("Creating default tenant...")
            default_tenant = Tenant(
                name='Default Organization',
                subdomain='app',
                status=TenantStatus.ACTIVE,
                plan=SubscriptionPlan.ENTERPRISE,
                is_active=True,
                onboarded=True,
                billing_email='admin@smartmaintenance.com',
                contact_name='System Administrator',
                primary_color='#667eea',
                secondary_color='#764ba2'
            )

            # Set unlimited resources after initialization
            default_tenant.max_users = None
            default_tenant.max_assets = None
            default_tenant.max_requests_per_month = None

            db.session.add(default_tenant)
            db.session.commit()

            default_tenant_id = default_tenant.id
            print(f"[OK] Default tenant created successfully!")
            print(f"  ID: {default_tenant_id}")
            print(f"  Name: {default_tenant.name}")
            print(f"  Subdomain: {default_tenant.subdomain}")
            print(f"  Plan: {default_tenant.plan} (Unlimited resources)")

        print("\n" + "-"*60)
        print("Migrating Existing Data")
        print("-"*60 + "\n")

        # Migrate existing data to default tenant
        tables = [
            ('users', 'User'),
            ('assets', 'Asset'),
            ('maintenance_requests', 'MaintenanceRequest'),
            ('feature_flags', 'FeatureFlag'),
            ('roles', 'Role'),
            ('permissions', 'Permission')
        ]

        total_migrated = 0

        for table_name, model_name in tables:
            # Count records without tenant_id
            result = db.session.execute(
                db.text(f"SELECT COUNT(*) FROM {table_name} WHERE tenant_id IS NULL")
            )
            count = result.scalar()

            if count > 0:
                print(f"Migrating {count} {model_name} records...")

                # Update records to assign default tenant
                db.session.execute(
                    db.text(f"UPDATE {table_name} SET tenant_id = :tenant_id WHERE tenant_id IS NULL"),
                    {'tenant_id': default_tenant_id}
                )
                db.session.commit()

                print(f"  [OK] {count} {model_name} records migrated")
                total_migrated += count
            else:
                print(f"  [OK] All {model_name} records already have tenant_id")

        print("\n" + "="*60)
        print(f"Migration Complete!")
        print(f"Total records migrated: {total_migrated}")
        print("="*60 + "\n")

        # Display summary
        print("\nTenant Summary:")
        print(f"  ID: {default_tenant_id}")
        print(f"  Name: Default Organization")
        print(f"  Subdomain: app (accessible at app.smartmaintenance.com)")
        print(f"  Plan: Enterprise (Unlimited resources)")
        print(f"  Status: Active")

        # Get counts
        from app.models.user import User
        from app.models.asset import Asset
        from app.models.request import MaintenanceRequest
        from app.models.feature_flag import FeatureFlag
        from app.models.role import Role
        from app.models.permission import Permission

        print(f"\nData assigned to default tenant:")
        print(f"  Users: {User.query.filter_by(tenant_id=default_tenant_id).count()}")
        print(f"  Assets: {Asset.query.filter_by(tenant_id=default_tenant_id).count()}")
        print(f"  Maintenance Requests: {MaintenanceRequest.query.filter_by(tenant_id=default_tenant_id).count()}")
        print(f"  Feature Flags: {FeatureFlag.query.filter_by(tenant_id=default_tenant_id).count()}")
        print(f"  Roles: {Role.query.filter_by(tenant_id=default_tenant_id).count()}")
        print(f"  Permissions: {Permission.query.filter_by(tenant_id=default_tenant_id).count()}")

        print("\n[OK] All existing data has been migrated to the default tenant.")
        print("  You can now safely make tenant_id NOT NULL in a future migration.")
        print()

if __name__ == '__main__':
    setup_default_tenant()
