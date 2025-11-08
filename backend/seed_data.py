"""
Seed database with sample data for development.

Creates sample users, assets, and maintenance requests.
"""

from app import create_app
from app.database import db
from app.models import User, Asset, UserRole, AssetCategory, AssetStatus, AssetCondition
from app.repositories import UserRepository, AssetRepository
from app.patterns.factory import MaintenanceRequestFactory
from app.models.request import RequestPriority

def seed_database():
    """Seed the database with sample data"""
    app = create_app('development')

    with app.app_context():
        print("Seeding database with sample data...")

        # Initialize repositories
        user_repo = UserRepository()
        asset_repo = AssetRepository()
        factory = MaintenanceRequestFactory()

        # Create Users
        print("\n1. Creating users...")

        # Admin user
        admin = user_repo.get_by_email('admin@smartmaintenance.com')
        if not admin:
            admin = user_repo.create_user(
                email='admin@smartmaintenance.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                role=UserRole.ADMIN,
                department='Administration'
            )
            print(f"   Created admin: {admin.email}")
        else:
            print(f"   Admin already exists: {admin.email}")

        # Technicians
        tech1 = user_repo.get_by_email('john.tech@smartmaintenance.com')
        if not tech1:
            tech1 = user_repo.create_user(
                email='john.tech@smartmaintenance.com',
                password='tech123',
                first_name='John',
                last_name='Electrician',
                role=UserRole.TECHNICIAN,
                department='Electrical',
                phone='555-0101'
            )
            print(f"   Created technician: {tech1.email}")
        else:
            print(f"   Technician already exists: {tech1.email}")

        tech2 = user_repo.get_by_email('jane.plumber@smartmaintenance.com')
        if not tech2:
            tech2 = user_repo.create_user(
                email='jane.plumber@smartmaintenance.com',
                password='tech123',
                first_name='Jane',
                last_name='Plumber',
                role=UserRole.TECHNICIAN,
                department='Plumbing',
                phone='555-0102'
            )
            print(f"   Created technician: {tech2.email}")
        else:
            print(f"   Technician already exists: {tech2.email}")

        tech3 = user_repo.get_by_email('mike.hvac@smartmaintenance.com')
        if not tech3:
            tech3 = user_repo.create_user(
                email='mike.hvac@smartmaintenance.com',
                password='tech123',
                first_name='Mike',
                last_name='HVAC',
                role=UserRole.TECHNICIAN,
                department='HVAC',
                phone='555-0103'
            )
            print(f"   Created technician: {tech3.email}")
        else:
            print(f"   Technician already exists: {tech3.email}")

        # Clients
        client1 = user_repo.get_by_email('sarah.client@smartmaintenance.com')
        if not client1:
            client1 = user_repo.create_user(
                email='sarah.client@smartmaintenance.com',
                password='client123',
                first_name='Sarah',
                last_name='Johnson',
                role=UserRole.CLIENT,
                department='Marketing',
                phone='555-0201'
            )
            print(f"   Created client: {client1.email}")
        else:
            print(f"   Client already exists: {client1.email}")

        client2 = user_repo.get_by_email('bob.client@smartmaintenance.com')
        if not client2:
            client2 = user_repo.create_user(
                email='bob.client@smartmaintenance.com',
                password='client123',
                first_name='Bob',
                last_name='Smith',
                role=UserRole.CLIENT,
                department='Sales',
                phone='555-0202'
            )
            print(f"   Created client: {client2.email}")
        else:
            print(f"   Client already exists: {client2.email}")

        # Create Assets
        print("\n2. Creating assets...")

        asset1 = asset_repo.create_asset(
            name='Main Office AC Unit',
            asset_tag='HVAC-001',
            category=AssetCategory.HVAC,
            status=AssetStatus.ACTIVE,
            condition=AssetCondition.GOOD,
            building='Main Building',
            floor='3',
            room='Server Room',
            manufacturer='CoolAir Inc',
            model='CA-5000'
        )
        print(f"   Created asset: {asset1.name}")

        asset2 = asset_repo.create_asset(
            name='Conference Room Lights',
            asset_tag='ELEC-001',
            category=AssetCategory.ELECTRICAL,
            status=AssetStatus.ACTIVE,
            condition=AssetCondition.EXCELLENT,
            building='Main Building',
            floor='2',
            room='Conference Room A',
            manufacturer='BrightLight Co',
            model='LED-200'
        )
        print(f"   Created asset: {asset2.name}")

        asset3 = asset_repo.create_asset(
            name='Kitchen Sink',
            asset_tag='PLUMB-001',
            category=AssetCategory.PLUMBING,
            status=AssetStatus.ACTIVE,
            condition=AssetCondition.FAIR,
            building='Main Building',
            floor='1',
            room='Break Room',
            manufacturer='FlowMaster',
            model='FM-3000'
        )
        print(f"   Created asset: {asset3.name}")

        asset4 = asset_repo.create_asset(
            name='Parking Lot Lights',
            asset_tag='ELEC-002',
            category=AssetCategory.ELECTRICAL,
            status=AssetStatus.ACTIVE,
            condition=AssetCondition.POOR,
            building='Main Building',
            floor='Ground',
            room='Parking Lot',
            location_details='North side of building'
        )
        print(f"   Created asset: {asset4.name}")

        asset5 = asset_repo.create_asset(
            name='Server Room Cooling',
            asset_tag='HVAC-002',
            category=AssetCategory.HVAC,
            status=AssetStatus.IN_REPAIR,
            condition=AssetCondition.POOR,
            building='Main Building',
            floor='3',
            room='Server Room',
            manufacturer='CoolTech',
            model='CT-8000'
        )
        print(f"   Created asset: {asset5.name}")

        # Create Maintenance Requests
        print("\n3. Creating maintenance requests...")

        # Electrical request
        request1 = factory.create_electrical_request(
            title='Conference room lights flickering',
            description='Lights in Conference Room A are flickering intermittently',
            submitter_id=client1.id,
            asset_id=asset2.id,
            priority=RequestPriority.MEDIUM,
            voltage='120V',
            circuit_number='C-12'
        )
        db.session.add(request1)
        print(f"   Created electrical request: {request1.title}")

        # Plumbing request
        request2 = factory.create_plumbing_request(
            title='Kitchen sink draining slowly',
            description='Break room sink is draining very slowly, possible clog',
            submitter_id=client2.id,
            asset_id=asset3.id,
            priority=RequestPriority.LOW,
            leak_severity='minor'
        )
        db.session.add(request2)
        print(f"   Created plumbing request: {request2.title}")

        # HVAC request - assigned
        request3 = factory.create_hvac_request(
            title='Server room temperature high',
            description='Server room temperature is 85°F, should be 68°F',
            submitter_id=client1.id,
            asset_id=asset1.id,
            priority=RequestPriority.HIGH,
            system_type='cooling',
            temperature_issue='Room at 85°F, target 68°F'
        )
        request3.assign_to(tech3.id)
        request3.start_work()
        db.session.add(request3)
        print(f"   Created HVAC request: {request3.title}")

        # Electrical emergency
        request4 = factory.create_electrical_request(
            title='Parking lot lights not working',
            description='All parking lot lights went out, safety concern',
            submitter_id=admin.id,
            asset_id=asset4.id,
            is_emergency=True,
            circuit_number='PL-1',
            breaker_location='Panel B'
        )
        request4.assign_to(tech1.id)
        db.session.add(request4)
        print(f"   Created emergency electrical request: {request4.title}")

        # HVAC critical
        request5 = factory.create_hvac_request(
            title='Server room cooling unit failure',
            description='Secondary cooling unit completely failed',
            submitter_id=admin.id,
            asset_id=asset5.id,
            priority=RequestPriority.URGENT,
            system_type='cooling',
            temperature_issue='Unit not running',
            refrigerant_leak=True
        )
        request5.assign_to(tech3.id)
        request5.start_work()
        db.session.add(request5)
        print(f"   Created critical HVAC request: {request5.title}")

        # Commit all requests
        db.session.commit()

        print("\n" + "="*60)
        print("Database seeded successfully!")
        print("="*60)
        print("\nSample Login Credentials:")
        print("-" * 60)
        print("Admin:")
        print("  Email: admin@smartmaintenance.com")
        print("  Password: admin123")
        print("\nTechnicians:")
        print("  Email: john.tech@smartmaintenance.com")
        print("  Email: jane.plumber@smartmaintenance.com")
        print("  Email: mike.hvac@smartmaintenance.com")
        print("  Password: tech123")
        print("\nClients:")
        print("  Email: sarah.client@smartmaintenance.com")
        print("  Email: bob.client@smartmaintenance.com")
        print("  Password: client123")
        print("-" * 60)
        print(f"\nCreated:")
        print(f"  • {user_repo.count()} users")
        print(f"  • {asset_repo.count()} assets")
        print(f"  • 5 maintenance requests")
        print("="*60)

if __name__ == '__main__':
    seed_database()
