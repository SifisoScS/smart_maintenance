"""
Demo: Complete Workflow - Full Request Lifecycle

Demonstrates:
- User registration and authentication
- Asset creation and management
- Request creation via Factory pattern
- Request assignment with authorization
- Work lifecycle (start -> complete)
- Multi-repository orchestration
- Automated notifications
- All business rules enforced
"""

from app import create_app
from app.repositories import (
    UserRepository, AssetRepository, RequestRepository
)
from app.services import (
    UserService, AssetService, MaintenanceService, NotificationService
)
from app.patterns.factory import MaintenanceRequestFactory
from app.patterns.strategy import EmailNotificationStrategy
from app.models import UserRole, AssetCategory, AssetStatus, AssetCondition


def print_section(title):
    """Print section header."""
    print("\n" + "="*70)
    print(title)
    print("="*70)


def print_result(label, result):
    """Print service result."""
    print(f"\n[{label}]")
    print(f"   Success: {result['success']}")
    if result['success']:
        if 'message' in result:
            print(f"   Message: {result['message']}")
        if 'data' in result and isinstance(result['data'], dict):
            for key, value in result['data'].items():
                if key not in ['password_hash', 'created_at', 'updated_at']:
                    print(f"   {key}: {value}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")


def demo_full_workflow():
    """Demonstrate complete maintenance request workflow."""

    app = create_app('development')

    with app.app_context():
        print_section("SMART MAINTENANCE SYSTEM - COMPLETE WORKFLOW DEMO")

        # Initialize repositories
        user_repo = UserRepository()
        asset_repo = AssetRepository()
        request_repo = RequestRepository()

        # Initialize services
        email_strategy = EmailNotificationStrategy(
            smtp_host='smtp.gmail.com',
            smtp_port=587,
            username='noreply@smartmaintenance.com',
            password='dummy-password'
        )

        notification_service = NotificationService(user_repo, email_strategy)
        user_service = UserService(user_repo)
        asset_service = AssetService(asset_repo)
        factory = MaintenanceRequestFactory()

        maintenance_service = MaintenanceService(
            request_repo, user_repo, asset_repo,
            notification_service, factory
        )

        print("\n[*] All services initialized successfully")
        print("   - UserService: Ready")
        print("   - AssetService: Ready")
        print("   - MaintenanceService: Ready")
        print("   - NotificationService: Email strategy configured")

        # ================================================================
        # STEP 1: User Management
        # ================================================================
        print_section("STEP 1: User Registration & Authentication")

        # Check if users already exist
        admin = user_repo.get_by_email('workflow.admin@example.com')
        tech = user_repo.get_by_email('workflow.tech@example.com')
        client = user_repo.get_by_email('workflow.client@example.com')

        if not admin:
            print("\n[1.1] Registering Admin User...")
            result = user_service.register_user(
                email='workflow.admin@example.com',
                password='SecureAdmin123',
                first_name='Workflow',
                last_name='Administrator',
                role='admin',
                department='Management'
            )
            print_result("Admin Registration", result)
            admin = user_repo.get_by_email('workflow.admin@example.com')
        else:
            print("\n[1.1] Admin user already exists - skipping registration")

        if not tech:
            print("\n[1.2] Registering Technician User...")
            result = user_service.register_user(
                email='workflow.tech@example.com',
                password='SecureTech123',
                first_name='Workflow',
                last_name='Technician',
                role='technician',
                phone='+1-555-0199',
                department='Electrical'
            )
            print_result("Technician Registration", result)
            tech = user_repo.get_by_email('workflow.tech@example.com')
        else:
            print("\n[1.2] Technician user already exists - skipping registration")

        if not client:
            print("\n[1.3] Registering Client User...")
            result = user_service.register_user(
                email='workflow.client@example.com',
                password='SecureClient123',
                first_name='Workflow',
                last_name='Client',
                role='client',
                department='Operations'
            )
            print_result("Client Registration", result)
            client = user_repo.get_by_email('workflow.client@example.com')
        else:
            print("\n[1.3] Client user already exists - skipping registration")

        print("\n[1.4] Authenticating Client User...")
        result = user_service.authenticate(
            email='workflow.client@example.com',
            password='SecureClient123'
        )
        print_result("Client Authentication", result)

        print("\n[1.5] Checking Available Technicians...")
        result = user_service.get_available_technicians()
        print_result("Available Technicians", result)
        print(f"   Found {len(result['data'])} technician(s)")

        # ================================================================
        # STEP 2: Asset Management
        # ================================================================
        print_section("STEP 2: Asset Creation & Management")

        # Check if asset already exists
        asset = asset_repo.get_by_asset_tag('WORKFLOW-SRV-001')

        if not asset:
            print("\n[2.1] Creating New Server Asset...")
            asset = asset_repo.create_asset(
                name='Workflow Demo Server',
                asset_tag='WORKFLOW-SRV-001',
                category=AssetCategory.ELECTRICAL,
                building='Main Building',
                floor='2nd Floor',
                room='Server Room A',
                status=AssetStatus.ACTIVE,
                condition=AssetCondition.GOOD
            )
            print(f"   Asset Created: {asset.name} (ID: {asset.id})")
            print(f"   Asset Tag: {asset.asset_tag}")
            print(f"   Status: {asset.status.value}")
            print(f"   Condition: {asset.condition.value}")
        else:
            print(f"\n[2.1] Asset already exists: {asset.name} (ID: {asset.id})")

        print("\n[2.2] Updating Asset Condition to 'Poor'...")
        result = asset_service.update_asset_condition(
            asset_id=asset.id,
            new_condition='poor'
        )
        print_result("Asset Condition Update", result)

        print("\n[2.3] Getting Assets Needing Maintenance...")
        result = asset_service.get_assets_needing_maintenance()
        print_result("Assets Needing Maintenance", result)
        print(f"   Found {len(result['data'])} asset(s) needing maintenance")

        print("\n[2.4] Getting Asset Statistics...")
        result = asset_service.get_asset_statistics()
        print_result("Asset Statistics", result)

        # ================================================================
        # STEP 3: Maintenance Request Creation
        # ================================================================
        print_section("STEP 3: Maintenance Request Creation")

        print("\n[3.1] Client Creates Electrical Maintenance Request...")
        print("   [BUSINESS RULE] Validating client is active...")
        print("   [BUSINESS RULE] Validating asset exists...")
        print("   [FACTORY PATTERN] Creating ElectricalRequest via Factory...")

        result = maintenance_service.create_request(
            request_type='electrical',
            submitter_id=client.id,
            asset_id=asset.id,
            title='Server Power Issue - Workflow Demo',
            description='Server experiencing intermittent power failures. Needs immediate attention.',
            priority='high',
            voltage='220V',
            circuit_number='Circuit 15',
            breaker_location='Panel A - Bay 3',
            is_emergency=False
        )
        print_result("Request Creation", result)

        request_id = None
        if result['success']:
            request_id = result['data']['id']
            print(f"\n   [NOTIFICATION] Admins automatically notified of new request #{request_id}")
        else:
            print(f"\n   [ERROR] Failed to create request - skipping remaining steps")
            return

        # ================================================================
        # STEP 4: Request Assignment
        # ================================================================
        print_section("STEP 4: Request Assignment (Admin Action)")

        print("\n[4.1] Admin Assigns Request to Technician...")
        print(f"   [BUSINESS RULE] Validating admin has admin role...")
        print(f"   [BUSINESS RULE] Validating technician exists and is active...")
        print(f"   [BUSINESS RULE] Validating technician has technician role...")
        print(f"   [BUSINESS RULE] Validating request is in assignable state...")

        result = maintenance_service.assign_request(
            request_id=request_id,
            technician_id=tech.id,
            assigned_by_user_id=admin.id
        )
        print_result("Request Assignment", result)

        if result['success']:
            print(f"\n   [CROSS-ENTITY UPDATE] Asset #{asset.id} status -> IN_REPAIR")
            print(f"   [NOTIFICATION] Technician notified of assignment")

        print("\n[4.2] Testing Authorization: Client Tries to Assign (Should Fail)...")
        result = maintenance_service.assign_request(
            request_id=request_id,
            technician_id=tech.id,
            assigned_by_user_id=client.id  # Client, not admin
        )
        print_result("Unauthorized Assignment Attempt", result)

        # ================================================================
        # STEP 5: Work Lifecycle - Start Work
        # ================================================================
        print_section("STEP 5: Technician Starts Work")

        print("\n[5.1] Assigned Technician Starts Work...")
        print(f"   [BUSINESS RULE] Validating technician is assigned to this request...")

        result = maintenance_service.start_work(
            request_id=request_id,
            technician_id=tech.id
        )
        print_result("Start Work", result)

        if result['success']:
            print(f"\n   [NOTIFICATION] Client notified that work has started")

        print("\n[5.2] Testing Authorization: Different Technician Tries to Start (Should Fail)...")
        # Try with admin ID (not the assigned technician)
        result = maintenance_service.start_work(
            request_id=request_id,
            technician_id=admin.id
        )
        print_result("Unauthorized Start Work Attempt", result)

        # ================================================================
        # STEP 6: Work Lifecycle - Complete Work
        # ================================================================
        print_section("STEP 6: Technician Completes Work")

        print("\n[6.1] Assigned Technician Completes Request...")
        print(f"   [BUSINESS RULE] Validating completion notes are provided...")
        print(f"   [BUSINESS RULE] Validating technician is assigned to this request...")

        result = maintenance_service.complete_request(
            request_id=request_id,
            technician_id=tech.id,
            completion_notes='Replaced faulty power supply unit and tested all connections. '
                           'Server is now running stable. Voltage readings normal at 220V. '
                           'Circuit breaker CB-15 checked and functioning properly.',
            actual_hours=2.5
        )
        print_result("Complete Request", result)

        if result['success']:
            print(f"\n   [CROSS-ENTITY UPDATE] Asset #{asset.id} status -> ACTIVE (repaired)")
            print(f"   [NOTIFICATION] Client notified of completion")
            print(f"   [NOTIFICATION] All admins notified of completion")

        print("\n[6.2] Testing Business Rule: Completion Without Notes (Should Fail)...")
        # Create another request to test
        result2 = maintenance_service.create_request(
            request_type='plumbing',
            submitter_id=client.id,
            asset_id=asset.id,
            title='Test Request for Validation',
            description='Test',
            priority='low'
        )

        if result2['success']:
            test_request_id = result2['data']['id']
            maintenance_service.assign_request(test_request_id, tech.id, admin.id)
            maintenance_service.start_work(test_request_id, tech.id)

            result = maintenance_service.complete_request(
                request_id=test_request_id,
                technician_id=tech.id,
                completion_notes=''  # Empty notes - should fail
            )
            print_result("Complete Without Notes", result)

        # ================================================================
        # STEP 7: Reporting & Analytics
        # ================================================================
        print_section("STEP 7: Reporting & Analytics")

        print("\n[7.1] Getting Technician Workload...")
        result = maintenance_service.get_technician_workload(
            technician_id=tech.id
        )
        print_result("Technician Workload", result)

        print("\n[7.2] Getting Unassigned Requests...")
        result = maintenance_service.get_unassigned_requests()
        print_result("Unassigned Requests", result)

        print("\n[7.3] Getting Asset Statistics (Updated)...")
        result = asset_service.get_asset_statistics()
        print_result("Final Asset Statistics", result)

        # ================================================================
        # SUMMARY
        # ================================================================
        print_section("WORKFLOW DEMONSTRATION COMPLETE")

        print("""
[+] COMPLETE WORKFLOW DEMONSTRATED:
   1. User Registration & Authentication
      - Admin, Technician, and Client users created
      - Authentication successful
      - Available technicians listed

   2. Asset Management
      - Server asset created
      - Condition updated to 'poor'
      - Assets needing maintenance tracked
      - Asset statistics generated

   3. Request Creation
      - Client created maintenance request
      - Factory pattern used for ElectricalRequest
      - Admins automatically notified

   4. Request Assignment
      - Admin assigned request to technician
      - Authorization validated (client cannot assign)
      - Asset status updated to IN_REPAIR
      - Technician notified

   5. Work Lifecycle - Start
      - Technician started work
      - Authorization validated (only assigned tech can start)
      - Client notified

   6. Work Lifecycle - Complete
      - Technician completed work with notes
      - Business rules validated (notes required)
      - Asset status updated to ACTIVE
      - Client and admins notified

   7. Reporting & Analytics
      - Technician workload retrieved
      - Unassigned requests listed
      - Asset statistics generated

[+] PATTERNS & PRINCIPLES DEMONSTRATED:
   - Repository Pattern: Clean data access abstraction
   - Factory Pattern: Polymorphic request creation
   - Strategy Pattern: Pluggable notification methods
   - Service Layer: Business logic orchestration
   - Dependency Injection: Loose coupling throughout
   - SOLID Principles: All five principles in action

[+] BUSINESS RULES ENFORCED:
   - Authorization checks (admin-only operations)
   - Validation rules (active users, valid enums)
   - State transitions (request lifecycle)
   - Cross-entity updates (asset status with requests)
   - Automated notifications (Observer-like pattern)

[+] MULTI-REPOSITORY ORCHESTRATION:
   - UserRepository: User lookups and validation
   - AssetRepository: Asset status updates
   - RequestRepository: Request lifecycle management
   - All coordinated seamlessly by services

Ready for Phase 3: API Layer & Controllers!
        """)

        print("="*70)
        print("Run tests: pytest tests/unit/ -v")
        print("="*70)


if __name__ == '__main__':
    demo_full_workflow()
