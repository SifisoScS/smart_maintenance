"""
Seed script for RBAC system - Permissions and Roles
"""
from app import create_app
from app.database import db
from app.repositories.permission_repository import PermissionRepository
from app.repositories.role_repository import RoleRepository

# Create Flask app
app = create_app()

def seed_permissions():
    """Create default permissions"""
    print("Seeding permissions...")

    permissions_data = [
        # Request Permissions
        {"name": "view_requests", "resource": "requests", "action": "view",
         "description": "View maintenance requests"},
        {"name": "create_requests", "resource": "requests", "action": "create",
         "description": "Create maintenance requests"},
        {"name": "edit_requests", "resource": "requests", "action": "edit",
         "description": "Edit maintenance requests"},
        {"name": "delete_requests", "resource": "requests", "action": "delete",
         "description": "Delete maintenance requests"},
        {"name": "assign_requests", "resource": "requests", "action": "assign",
         "description": "Assign requests to technicians"},
        {"name": "start_work", "resource": "requests", "action": "start",
         "description": "Start work on assigned requests"},
        {"name": "complete_requests", "resource": "requests", "action": "complete",
         "description": "Complete maintenance requests"},

        # Asset Permissions
        {"name": "view_assets", "resource": "assets", "action": "view",
         "description": "View assets"},
        {"name": "create_assets", "resource": "assets", "action": "create",
         "description": "Create new assets"},
        {"name": "edit_assets", "resource": "assets", "action": "edit",
         "description": "Edit asset details"},
        {"name": "delete_assets", "resource": "assets", "action": "delete",
         "description": "Delete assets"},
        {"name": "update_asset_condition", "resource": "assets", "action": "update_condition",
         "description": "Update asset condition status"},
        {"name": "view_asset_history", "resource": "assets", "action": "view_history",
         "description": "View asset maintenance history"},

        # User Permissions
        {"name": "view_users", "resource": "users", "action": "view",
         "description": "View user list"},
        {"name": "create_users", "resource": "users", "action": "create",
         "description": "Create new users"},
        {"name": "edit_users", "resource": "users", "action": "edit",
         "description": "Edit user details"},
        {"name": "delete_users", "resource": "users", "action": "delete",
         "description": "Delete users"},
        {"name": "assign_roles", "resource": "users", "action": "assign_roles",
         "description": "Assign roles to users"},
        {"name": "remove_roles", "resource": "users", "action": "remove_roles",
         "description": "Remove roles from users"},

        # Analytics Permissions
        {"name": "view_dashboard", "resource": "analytics", "action": "view_dashboard",
         "description": "View analytics dashboard"},
        {"name": "view_reports", "resource": "analytics", "action": "view_reports",
         "description": "View detailed reports"},
        {"name": "export_data", "resource": "analytics", "action": "export",
         "description": "Export analytics data"},

        # Feature Flag Permissions
        {"name": "view_feature_flags", "resource": "feature_flags", "action": "view",
         "description": "View feature flags"},
        {"name": "toggle_feature_flags", "resource": "feature_flags", "action": "toggle",
         "description": "Toggle feature flags on/off"},
        {"name": "manage_feature_flags", "resource": "feature_flags", "action": "manage",
         "description": "Full feature flag management"},

        # RBAC System Permissions
        {"name": "view_roles", "resource": "roles", "action": "view",
         "description": "View roles"},
        {"name": "manage_roles", "resource": "roles", "action": "manage",
         "description": "Create, update, delete roles"},
        {"name": "view_permissions", "resource": "permissions", "action": "view",
         "description": "View permissions"},
        {"name": "manage_permissions", "resource": "permissions", "action": "manage",
         "description": "Create, update, delete permissions"},

        # System Permissions
        {"name": "view_audit_logs", "resource": "system", "action": "view_logs",
         "description": "View audit logs"},
    ]

    perm_repo = PermissionRepository()
    created_permissions = perm_repo.bulk_create(permissions_data)
    print(f"Created {len(created_permissions)} permissions")

    return perm_repo


def seed_roles(perm_repo):
    """Create default roles with permissions"""
    print("\nSeeding roles...")

    role_repo = RoleRepository()

    # 1. Super Admin Role
    print("Creating Super Admin role...")
    super_admin = role_repo.create({
        'name': 'Super Admin',
        'description': 'Full system access with all permissions',
        'is_system': True
    })

    # Assign ALL permissions to Super Admin
    all_permissions = perm_repo.get_all()
    all_permission_ids = [p.id for p in all_permissions]
    role_repo.set_permissions(super_admin.id, all_permission_ids)
    print(f"  - Assigned {len(all_permission_ids)} permissions")

    # 2. Admin Role
    print("Creating Admin role...")
    admin_permissions = [
        'view_requests', 'create_requests', 'edit_requests', 'delete_requests', 'assign_requests',
        'view_assets', 'create_assets', 'edit_assets', 'delete_assets', 'update_asset_condition', 'view_asset_history',
        'view_users', 'create_users', 'edit_users',
        'view_dashboard', 'view_reports', 'export_data',
        'view_feature_flags', 'toggle_feature_flags',
        'view_roles', 'view_permissions'
    ]
    admin = role_repo.create({
        'name': 'Admin',
        'description': 'Administrative access without RBAC management',
        'is_system': True
    })
    admin_perm_ids = [p.id for p in all_permissions if p.name in admin_permissions]
    role_repo.set_permissions(admin.id, admin_perm_ids)
    print(f"  - Assigned {len(admin_perm_ids)} permissions")

    # 3. Manager Role
    print("Creating Manager role...")
    manager_permissions = [
        'view_requests', 'create_requests', 'edit_requests', 'assign_requests',
        'view_assets', 'edit_assets', 'update_asset_condition', 'view_asset_history',
        'view_users',
        'view_dashboard', 'view_reports', 'export_data'
    ]
    manager = role_repo.create({
        'name': 'Manager',
        'description': 'Department manager with oversight capabilities',
        'is_system': True
    })
    manager_perm_ids = [p.id for p in all_permissions if p.name in manager_permissions]
    role_repo.set_permissions(manager.id, manager_perm_ids)
    print(f"  - Assigned {len(manager_perm_ids)} permissions")

    # 4. Technician Role
    print("Creating Technician role...")
    technician_permissions = [
        'view_requests', 'start_work', 'complete_requests',
        'view_assets', 'update_asset_condition', 'view_asset_history',
        'view_dashboard'
    ]
    technician = role_repo.create({
        'name': 'Technician',
        'description': 'Field technician with work execution permissions',
        'is_system': True
    })
    tech_perm_ids = [p.id for p in all_permissions if p.name in technician_permissions]
    role_repo.set_permissions(technician.id, tech_perm_ids)
    print(f"  - Assigned {len(tech_perm_ids)} permissions")

    # 5. Client Role
    print("Creating Client role...")
    client_permissions = [
        'view_requests', 'create_requests',
        'view_assets',
        'view_dashboard'
    ]
    client = role_repo.create({
        'name': 'Client',
        'description': 'End user who can submit and track requests',
        'is_system': True
    })
    client_perm_ids = [p.id for p in all_permissions if p.name in client_permissions]
    role_repo.set_permissions(client.id, client_perm_ids)
    print(f"  - Assigned {len(client_perm_ids)} permissions")

    print(f"\nCreated 5 system roles")
    return role_repo


def print_summary(perm_repo, role_repo):
    """Print summary of seeded data"""
    print("\n" + "="*60)
    print("RBAC SEEDING COMPLETE")
    print("="*60)

    # Permissions summary
    permissions = perm_repo.get_all()
    grouped = perm_repo.get_grouped_by_resource()

    print(f"\nTotal Permissions: {len(permissions)}")
    print("\nPermissions by Resource:")
    for resource, perms in sorted(grouped.items()):
        print(f"  {resource:20} : {len(perms)} permissions")

    # Roles summary
    roles = role_repo.get_all()
    print(f"\n\nTotal Roles: {len(roles)}")
    print("\nRoles and Permission Counts:")
    for role in roles:
        role_data = role_repo.get_by_id(role.id)
        perm_count = len(role_data.permissions)
        is_system = "(System)" if role_data.is_system else "(Custom)"
        print(f"  {role.name:20} : {perm_count:2} permissions {is_system}")

    print("\n" + "="*60)
    print("Next Steps:")
    print("  1. Assign roles to existing users")
    print("  2. Update API endpoints with @require_permission decorators")
    print("  3. Test permission enforcement")
    print("="*60 + "\n")


if __name__ == '__main__':
    with app.app_context():
        try:
            # Check if permissions already exist
            perm_repo = PermissionRepository()
            existing_perms = perm_repo.count()

            if existing_perms > 0:
                print(f"Warning: {existing_perms} permissions already exist.")
                response = input("Do you want to continue and create additional permissions? (yes/no): ")
                if response.lower() not in ['yes', 'y']:
                    print("Seeding cancelled.")
                    exit(0)

            # Seed permissions
            perm_repo = seed_permissions()

            # Seed roles
            role_repo = seed_roles(perm_repo)

            # Print summary
            print_summary(perm_repo, role_repo)

            print("RBAC seeding completed successfully!")

        except Exception as e:
            print(f"\nError during seeding: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
