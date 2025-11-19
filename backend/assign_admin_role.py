"""
Assign Super Admin role to admin@smartmaintenance.com user
"""
from app import create_app
from app.database import db
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository

# Create Flask app
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        try:
            user_repo = UserRepository()
            role_repo = RoleRepository()

            # Find admin user
            admin_user = user_repo.get_by_email('admin@smartmaintenance.com')
            if not admin_user:
                print("ERROR: Admin user (admin@smartmaintenance.com) not found!")
                print("Please run: python seed_data.py first")
                exit(1)

            # Find Super Admin role
            super_admin_role = role_repo.get_by_name('Super Admin')
            if not super_admin_role:
                print("ERROR: Super Admin role not found!")
                print("Please run: python seed_rbac.py first")
                exit(1)

            # Check if user already has the role
            if super_admin_role in admin_user.roles:
                print(f"✓ User {admin_user.email} already has Super Admin role")
            else:
                # Assign Super Admin role to admin user
                admin_user.roles.append(super_admin_role)
                db.session.commit()
                print(f"✓ Successfully assigned Super Admin role to {admin_user.email}")

            # Show summary
            print("\n" + "="*60)
            print("ADMIN USER SUMMARY")
            print("="*60)
            print(f"Email: {admin_user.email}")
            print(f"Name: {admin_user.full_name}")
            print(f"Role: {admin_user.role.value}")
            print(f"\nRBAC Roles Assigned:")
            for role in admin_user.roles:
                perm_count = len(role.permissions)
                print(f"  - {role.name} ({perm_count} permissions)")

            print("\n" + "="*60)
            print("✓ Admin user is ready with full RBAC permissions!")
            print("="*60)

        except Exception as e:
            print(f"\nError: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
