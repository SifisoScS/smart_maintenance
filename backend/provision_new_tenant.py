"""
Tenant Provisioning CLI Script

Creates a new tenant with complete setup including admin user, roles, and permissions.
Can be run manually or called by automated provisioning systems.

Usage:
    python provision_new_tenant.py

    (Interactive mode - prompts for all details)

Or with arguments:
    python provision_new_tenant.py --name "Acme Corp" --subdomain acme --email admin@acme.com --password secret123
"""

import sys
import argparse
from getpass import getpass
from app import create_app
from app.services.tenant_service import TenantService


def provision_tenant_interactive():
    """Provision tenant with interactive prompts"""
    print("\n" + "="*60)
    print("Smart Maintenance - New Tenant Provisioning")
    print("="*60 + "\n")

    # Collect tenant information
    print("ORGANIZATION INFORMATION:")
    print("-" * 60)
    name = input("Organization name: ").strip()
    subdomain = input("Subdomain (e.g., 'acme' for acme.smartmaintenance.com): ").strip().lower()

    print("\nADMIN USER INFORMATION:")
    print("-" * 60)
    admin_first_name = input("Admin first name: ").strip()
    admin_last_name = input("Admin last name: ").strip()
    admin_email = input("Admin email: ").strip()
    admin_password = getpass("Admin password (min 6 chars): ")
    admin_password_confirm = getpass("Confirm password: ")

    if admin_password != admin_password_confirm:
        print("\n[ERROR] Passwords do not match!")
        return False

    print("\nSUBSCRIPTION PLAN:")
    print("-" * 60)
    print("Available plans:")
    print("  1. free     - 14-day trial, 3 users, 10 assets, 50 requests/month")
    print("  2. basic    - $29/mo, 10 users, 100 assets, 500 requests/month")
    print("  3. premium  - $99/mo, 50 users, 500 assets, 5000 requests/month")
    print("  4. enterprise - $299/mo, unlimited")

    plan_choice = input("Select plan (1-4) [default: 1]: ").strip() or "1"
    plan_map = {"1": "free", "2": "basic", "3": "premium", "4": "enterprise"}
    plan = plan_map.get(plan_choice, "free")

    print("\nOPTIONAL CONTACT INFORMATION:")
    print("-" * 60)
    billing_email = input("Billing email (press Enter to use admin email): ").strip()
    contact_name = input("Contact name (press Enter to use admin name): ").strip()
    contact_phone = input("Contact phone (optional): ").strip()

    # Confirmation
    print("\n" + "="*60)
    print("REVIEW INFORMATION")
    print("="*60)
    print(f"Organization: {name}")
    print(f"Subdomain: {subdomain}.smartmaintenance.com")
    print(f"Admin: {admin_first_name} {admin_last_name} ({admin_email})")
    print(f"Plan: {plan}")
    print("="*60)

    confirm = input("\nProceed with provisioning? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("\n[CANCELLED] Provisioning cancelled by user.")
        return False

    # Provision tenant
    print("\n" + "="*60)
    print("PROVISIONING TENANT...")
    print("="*60 + "\n")

    try:
        app = create_app()
        with app.app_context():
            tenant_service = TenantService()

            result = tenant_service.provision_tenant(
                name=name,
                subdomain=subdomain,
                admin_email=admin_email,
                admin_password=admin_password,
                admin_first_name=admin_first_name,
                admin_last_name=admin_last_name,
                plan=plan,
                billing_email=billing_email or admin_email,
                contact_name=contact_name or f"{admin_first_name} {admin_last_name}",
                contact_phone=contact_phone if contact_phone else None
            )

            print("[OK] Tenant provisioned successfully!\n")
            print("TENANT DETAILS:")
            print("-" * 60)
            print(f"Organization: {result['tenant']['name']}")
            print(f"Subdomain: {result['tenant']['subdomain']}")
            print(f"Plan: {result['tenant']['plan']}")
            print(f"Status: {result['tenant']['status']}")
            print(f"Trial expires: {result['tenant'].get('trial_ends', 'N/A')}")
            print()
            print("ADMIN USER:")
            print("-" * 60)
            print(f"Name: {result['admin_user']['full_name']}")
            print(f"Email: {result['admin_user']['email']}")
            print(f"User ID: {result['admin_user']['id']}")
            print()
            print("ROLES CREATED:")
            print("-" * 60)
            for role in result['roles_created']:
                print(f"  - {role}")
            print()
            print("ACCESS:")
            print("-" * 60)
            print(f"URL: http://{subdomain}.smartmaintenance.com")
            print(f"     (or http://localhost:5112 with X-Tenant-ID: {result['tenant']['id']})")
            print(f"Login: {admin_email}")
            print(f"Password: ********")
            print("\n" + "="*60)
            print(result['message'])
            print("="*60 + "\n")

            return True

    except ValueError as e:
        print(f"\n[ERROR] Validation error: {str(e)}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Failed to provision tenant: {str(e)}")
        return False


def provision_tenant_with_args(args):
    """Provision tenant with command-line arguments"""
    print("\n" + "="*60)
    print("Smart Maintenance - New Tenant Provisioning")
    print("="*60 + "\n")

    try:
        app = create_app()
        with app.app_context():
            tenant_service = TenantService()

            # Use provided values or defaults
            result = tenant_service.provision_tenant(
                name=args.name,
                subdomain=args.subdomain,
                admin_email=args.email,
                admin_password=args.password,
                admin_first_name=args.first_name or args.name.split()[0],
                admin_last_name=args.last_name or (args.name.split()[1] if len(args.name.split()) > 1 else "Admin"),
                plan=args.plan or 'free',
                billing_email=args.billing_email or args.email,
                contact_name=args.contact_name,
                contact_phone=args.contact_phone
            )

            print("[OK] Tenant provisioned successfully!")
            print(f"\nTenant: {result['tenant']['name']}")
            print(f"Subdomain: {result['tenant']['subdomain']}")
            print(f"Admin: {result['admin_user']['email']}")
            print(f"Plan: {result['tenant']['plan']}")
            print(f"\n{result['message']}\n")

            return True

    except ValueError as e:
        print(f"\n[ERROR] Validation error: {str(e)}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Failed to provision tenant: {str(e)}")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Provision a new tenant in Smart Maintenance system'
    )

    # Optional arguments for non-interactive mode
    parser.add_argument('--name', help='Organization name')
    parser.add_argument('--subdomain', help='Tenant subdomain')
    parser.add_argument('--email', help='Admin email')
    parser.add_argument('--password', help='Admin password')
    parser.add_argument('--first-name', help='Admin first name')
    parser.add_argument('--last-name', help='Admin last name')
    parser.add_argument('--plan', choices=['free', 'basic', 'premium', 'enterprise'],
                       help='Subscription plan')
    parser.add_argument('--billing-email', help='Billing email (optional)')
    parser.add_argument('--contact-name', help='Contact name (optional)')
    parser.add_argument('--contact-phone', help='Contact phone (optional)')

    args = parser.parse_args()

    # Check if all required args provided for non-interactive mode
    required_args = ['name', 'subdomain', 'email', 'password']
    has_all_required = all(getattr(args, arg) is not None for arg in required_args)

    if has_all_required:
        # Non-interactive mode
        success = provision_tenant_with_args(args)
    else:
        # Interactive mode
        if any(getattr(args, arg) is not None for arg in required_args):
            print("[WARNING] Some arguments provided but not all required arguments.")
            print("          Switching to interactive mode.\n")

        success = provision_tenant_interactive()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
