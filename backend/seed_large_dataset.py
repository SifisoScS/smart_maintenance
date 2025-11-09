"""
Seed database with 100+ maintenance requests for UI testing.

This script creates a large dataset to test dashboard and list page performance.
"""

from app import create_app
from app.database import db
from app.models import User, Asset, UserRole
from app.repositories import UserRepository, AssetRepository, RequestRepository
from app.patterns.factory import MaintenanceRequestFactory
from app.models.request import RequestPriority, RequestType, RequestStatus
from datetime import datetime, timedelta
import random

def seed_large_dataset():
    """Seed the database with 100+ maintenance requests"""
    app = create_app('development')

    with app.app_context():
        print("Seeding database with 100+ maintenance requests...")

        # Initialize repositories
        user_repo = UserRepository()
        asset_repo = AssetRepository()
        request_repo = RequestRepository()
        factory = MaintenanceRequestFactory()

        # Get all users and assets
        print("\n1. Fetching existing users and assets...")
        users = user_repo.get_all()
        assets = asset_repo.get_all()

        clients = [u for u in users if u.role == UserRole.CLIENT]
        technicians = [u for u in users if u.role == UserRole.TECHNICIAN]

        print(f"   Found {len(clients)} clients")
        print(f"   Found {len(technicians)} technicians")
        print(f"   Found {len(assets)} assets")

        if not clients or not assets:
            print("ERROR: Need at least 1 client and 1 asset. Run seed_data.py first!")
            return

        # Request types with their details
        request_types = [
            {
                'type': RequestType.ELECTRICAL,
                'titles': [
                    'Flickering lights in office',
                    'Power outlet not working',
                    'Circuit breaker keeps tripping',
                    'Emergency lighting needs repair',
                    'Electrical panel inspection',
                    'Replace faulty light switches',
                    'Install new power outlets',
                    'Repair damaged wiring'
                ],
                'extra_data': lambda: {
                    'circuit_number': f'C{random.randint(1, 50)}',
                    'breaker_location': random.choice(['Panel A', 'Panel B', 'Panel C']),
                    'voltage': random.choice(['120V', '240V', '480V'])
                }
            },
            {
                'type': RequestType.PLUMBING,
                'titles': [
                    'Leaking pipe under sink',
                    'Toilet not flushing properly',
                    'Water pressure too low',
                    'Clogged drain in restroom',
                    'Water heater maintenance',
                    'Faucet replacement needed',
                    'Sink installation request',
                    'Pipe burst emergency'
                ],
                'extra_data': lambda: {
                    'pipe_type': random.choice(['PVC', 'Copper', 'PEX', 'Cast Iron']),
                    'water_pressure': random.choice(['low', 'normal', 'high']),
                    'leak_severity': random.choice(['minor', 'moderate', 'severe'])
                }
            },
            {
                'type': RequestType.HVAC,
                'titles': [
                    'Air conditioning not cooling',
                    'Heating system malfunction',
                    'Strange noise from HVAC unit',
                    'Thermostat not responding',
                    'Air filter replacement needed',
                    'HVAC annual maintenance',
                    'Poor air circulation',
                    'Temperature control issues'
                ],
                'extra_data': lambda: {
                    'system_type': random.choice(['heating', 'cooling', 'ventilation']),
                    'temperature_issue': random.choice(['Too hot', 'Too cold', 'Inconsistent', 'No airflow'])
                }
            }
        ]

        # Status distribution (realistic mix)
        statuses = [
            (RequestStatus.SUBMITTED, 0.25),      # 25% submitted
            (RequestStatus.ASSIGNED, 0.15),       # 15% assigned
            (RequestStatus.IN_PROGRESS, 0.30),    # 30% in progress
            (RequestStatus.COMPLETED, 0.30)       # 30% completed
        ]

        # Priority distribution
        priorities = [
            (RequestPriority.LOW, 0.30),
            (RequestPriority.MEDIUM, 0.40),
            (RequestPriority.HIGH, 0.20),
            (RequestPriority.URGENT, 0.10)
        ]

        print("\n2. Creating 120 maintenance requests...")

        created_count = 0
        failed_count = 0

        for i in range(120):
            try:
                # Randomly select request type
                req_type = random.choice(request_types)
                request_type = req_type['type']
                title = random.choice(req_type['titles'])

                # Random client
                client = random.choice(clients)

                # Random asset
                asset = random.choice(assets)

                # Random priority (weighted)
                priority = random.choices(
                    [p[0] for p in priorities],
                    weights=[p[1] for p in priorities]
                )[0]

                # Random status (weighted)
                status = random.choices(
                    [s[0] for s in statuses],
                    weights=[s[1] for s in statuses]
                )[0]

                # Random dates (within last 90 days)
                days_ago = random.randint(0, 90)
                created_at = datetime.utcnow() - timedelta(days=days_ago)

                # Create description
                descriptions = [
                    f"This issue was reported on {created_at.strftime('%B %d, %Y')}.",
                    f"Located in {asset.location_details or asset.room or 'main building'}.",
                    "Please address this as soon as possible.",
                    "User has reported this issue multiple times." if random.random() > 0.7 else "",
                    "This may require specialized equipment." if random.random() > 0.8 else ""
                ]
                description = " ".join([d for d in descriptions if d])

                # Create request via factory
                request_data = {
                    'title': f"{title} #{i+1}",
                    'description': description,
                    'request_type': request_type,
                    'priority': priority,
                    'submitter_id': client.id,
                    'asset_id': asset.id,
                    **req_type['extra_data']()
                }

                request = factory.create_request(**request_data)

                # Update status if not submitted
                if status != RequestStatus.SUBMITTED:
                    request.status = status

                    # Assign to technician if not submitted
                    if status in [RequestStatus.ASSIGNED, RequestStatus.IN_PROGRESS, RequestStatus.COMPLETED]:
                        technician = random.choice(technicians)
                        request.assigned_technician_id = technician.id

                    # Add completion time if completed
                    if status == RequestStatus.COMPLETED:
                        completion_days = random.randint(1, 7)
                        request.completed_at = created_at + timedelta(days=completion_days)

                # Set created_at timestamp
                request.created_at = created_at

                db.session.add(request)
                created_count += 1

                if (i + 1) % 20 == 0:
                    db.session.commit()
                    print(f"   Created {i + 1} requests...")

            except Exception as e:
                failed_count += 1
                print(f"   Failed to create request {i + 1}: {str(e)}")
                continue

        # Final commit
        db.session.commit()

        print(f"\n[SUCCESS] Successfully created {created_count} maintenance requests")
        if failed_count > 0:
            print(f"[FAILED] Failed to create {failed_count} requests")

        # Print statistics
        total_requests = request_repo.get_all()
        print(f"\n3. Database Statistics:")
        print(f"   Total requests: {len(total_requests)}")
        print(f"   Submitted: {len([r for r in total_requests if r.status == RequestStatus.SUBMITTED])}")
        print(f"   Assigned: {len([r for r in total_requests if r.status == RequestStatus.ASSIGNED])}")
        print(f"   In Progress: {len([r for r in total_requests if r.status == RequestStatus.IN_PROGRESS])}")
        print(f"   Completed: {len([r for r in total_requests if r.status == RequestStatus.COMPLETED])}")

        print("\n[SUCCESS] Large dataset seeding complete!")

if __name__ == '__main__':
    seed_large_dataset()
