"""
Seed comprehensive assets for diverse industries and departments.

Creates assets for:
- IT Department
- Facilities Department
- Service Stations
- Manufacturing/Factories
- Building Infrastructure
- Office Equipment
"""

from app import create_app
from app.database import db
from app.models import Asset, AssetCategory, AssetStatus, AssetCondition
from app.repositories import AssetRepository
from datetime import datetime, timedelta
import random

def seed_comprehensive_assets():
    """Seed the database with comprehensive assets across industries"""
    app = create_app('development')

    with app.app_context():
        print("Seeding comprehensive assets for diverse industries...")

        asset_repo = AssetRepository()

        # Asset definitions organized by industry/department
        assets_data = [
            # ===== IT DEPARTMENT ASSETS =====
            {
                'name': 'Dell PowerEdge R740 Server',
                'description': 'Primary application server for business operations',
                'asset_tag': 'IT-SRV-001',
                'category': AssetCategory.IT_EQUIPMENT,
                'subcategory': 'Server',
                'building': 'Main Building',
                'floor': 'Basement',
                'room': 'Server Room A',
                'location_details': 'Rack 3, Unit 12-15',
                'manufacturer': 'Dell',
                'model': 'PowerEdge R740',
                'serial_number': 'SRV2024001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },
            {
                'name': 'HP ProLiant DL380 Backup Server',
                'description': 'Secondary backup and disaster recovery server',
                'asset_tag': 'IT-SRV-002',
                'category': AssetCategory.IT_EQUIPMENT,
                'subcategory': 'Server',
                'building': 'Main Building',
                'floor': 'Basement',
                'room': 'Server Room A',
                'location_details': 'Rack 4, Unit 8-11',
                'manufacturer': 'HP',
                'model': 'ProLiant DL380 Gen10',
                'serial_number': 'SRV2024002',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.EXCELLENT
            },
            {
                'name': 'Cisco Catalyst 2960-X Network Switch',
                'description': 'Core network switch for building connectivity',
                'asset_tag': 'IT-NET-001',
                'category': AssetCategory.IT_EQUIPMENT,
                'subcategory': 'Network Equipment',
                'building': 'Main Building',
                'floor': 'Basement',
                'room': 'Server Room A',
                'location_details': 'Rack 1, Unit 20',
                'manufacturer': 'Cisco',
                'model': 'Catalyst 2960-X',
                'serial_number': 'NET2024001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },
            {
                'name': 'Ubiquiti UniFi Dream Machine Pro',
                'description': 'Enterprise router and security gateway',
                'asset_tag': 'IT-NET-002',
                'category': AssetCategory.IT_EQUIPMENT,
                'subcategory': 'Network Equipment',
                'building': 'Main Building',
                'floor': 'Basement',
                'room': 'Server Room A',
                'location_details': 'Rack 1, Unit 18',
                'manufacturer': 'Ubiquiti',
                'model': 'Dream Machine Pro',
                'serial_number': 'NET2024002',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.EXCELLENT
            },
            {
                'name': 'APC Smart-UPS 3000VA',
                'description': 'Uninterruptible power supply for server room',
                'asset_tag': 'IT-PWR-001',
                'category': AssetCategory.IT_EQUIPMENT,
                'subcategory': 'Power Management',
                'building': 'Main Building',
                'floor': 'Basement',
                'room': 'Server Room A',
                'location_details': 'Floor mounted near Rack 3',
                'manufacturer': 'APC',
                'model': 'Smart-UPS 3000VA',
                'serial_number': 'UPS2024001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },
            {
                'name': 'Synology DS1821+ NAS Storage',
                'description': 'Network attached storage for file sharing and backups',
                'asset_tag': 'IT-STO-001',
                'category': AssetCategory.IT_EQUIPMENT,
                'subcategory': 'Storage',
                'building': 'Main Building',
                'floor': 'Basement',
                'room': 'Server Room A',
                'location_details': 'Rack 5, Unit 15-18',
                'manufacturer': 'Synology',
                'model': 'DiskStation DS1821+',
                'serial_number': 'NAS2024001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.EXCELLENT
            },

            # ===== HVAC & BUILDING SYSTEMS =====
            {
                'name': 'Carrier 30XA Air-Cooled Chiller',
                'description': 'Central chiller for building cooling system',
                'asset_tag': 'HVAC-CHL-001',
                'category': AssetCategory.HVAC,
                'subcategory': 'Chiller',
                'building': 'Main Building',
                'floor': 'Roof',
                'location_details': 'Mechanical penthouse - North side',
                'manufacturer': 'Carrier',
                'model': '30XA-150',
                'serial_number': 'CHL2023001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },
            {
                'name': 'Trane Rooftop HVAC Unit - Zone 1',
                'description': 'Rooftop package unit serving first floor offices',
                'asset_tag': 'HVAC-RTU-001',
                'category': AssetCategory.HVAC,
                'subcategory': 'Rooftop Unit',
                'building': 'Main Building',
                'floor': 'Roof',
                'location_details': 'South section, Unit 1',
                'manufacturer': 'Trane',
                'model': 'Precedent 15 Ton',
                'serial_number': 'RTU2023001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.FAIR
            },
            {
                'name': 'Trane Rooftop HVAC Unit - Zone 2',
                'description': 'Rooftop package unit serving second floor offices',
                'asset_tag': 'HVAC-RTU-002',
                'category': AssetCategory.HVAC,
                'subcategory': 'Rooftop Unit',
                'building': 'Main Building',
                'floor': 'Roof',
                'location_details': 'South section, Unit 2',
                'manufacturer': 'Trane',
                'model': 'Precedent 15 Ton',
                'serial_number': 'RTU2023002',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },
            {
                'name': 'Johnson Controls AHU - Main Lobby',
                'description': 'Air handling unit for main entrance and lobby area',
                'asset_tag': 'HVAC-AHU-001',
                'category': AssetCategory.HVAC,
                'subcategory': 'Air Handler',
                'building': 'Main Building',
                'floor': '2',
                'room': 'Mechanical Room',
                'manufacturer': 'Johnson Controls',
                'model': 'AHU-450',
                'serial_number': 'AHU2023001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.EXCELLENT
            },
            {
                'name': 'Honeywell Building Management System',
                'description': 'Central BMS controlling all HVAC equipment',
                'asset_tag': 'HVAC-BMS-001',
                'category': AssetCategory.IT_EQUIPMENT,
                'subcategory': 'Building Automation',
                'building': 'Main Building',
                'floor': '2',
                'room': 'Control Room',
                'manufacturer': 'Honeywell',
                'model': 'Enterprise Buildings Integrator',
                'serial_number': 'BMS2023001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },

            # ===== ELECTRICAL SYSTEMS =====
            {
                'name': 'Main Electrical Switchgear 480V',
                'description': 'Primary electrical distribution panel',
                'asset_tag': 'ELEC-SW-001',
                'category': AssetCategory.ELECTRICAL,
                'subcategory': 'Distribution',
                'building': 'Main Building',
                'floor': 'Basement',
                'room': 'Electrical Room A',
                'manufacturer': 'Square D',
                'model': 'I-Line Switchboard',
                'serial_number': 'SW2022001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },
            {
                'name': 'Emergency Generator - Diesel 500kW',
                'description': 'Backup power generator for critical systems',
                'asset_tag': 'ELEC-GEN-001',
                'category': AssetCategory.ELECTRICAL,
                'subcategory': 'Generator',
                'building': 'Main Building',
                'floor': 'Ground',
                'location_details': 'Exterior generator pad - East side',
                'manufacturer': 'Caterpillar',
                'model': 'C15 500kW',
                'serial_number': 'GEN2022001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },
            {
                'name': 'LED Lighting Panel - Floor 1',
                'description': 'Lighting control panel for first floor',
                'asset_tag': 'ELEC-LGT-001',
                'category': AssetCategory.ELECTRICAL,
                'subcategory': 'Lighting',
                'building': 'Main Building',
                'floor': '1',
                'room': 'Electrical Closet 1A',
                'manufacturer': 'Lutron',
                'model': 'Quantum System',
                'serial_number': 'LGT2023001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.EXCELLENT
            },
            {
                'name': 'Fire Alarm Control Panel',
                'description': 'Main fire alarm and detection system',
                'asset_tag': 'ELEC-FIRE-001',
                'category': AssetCategory.ELECTRICAL,
                'subcategory': 'Life Safety',
                'building': 'Main Building',
                'floor': '1',
                'room': 'Security Office',
                'manufacturer': 'Notifier',
                'model': 'NFS2-640',
                'serial_number': 'FIRE2022001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.EXCELLENT
            },

            # ===== PLUMBING SYSTEMS =====
            {
                'name': 'Domestic Water Booster Pump System',
                'description': 'Main water pressure booster for building',
                'asset_tag': 'PLMB-PMP-001',
                'category': AssetCategory.PLUMBING,
                'subcategory': 'Pump',
                'building': 'Main Building',
                'floor': 'Basement',
                'room': 'Mechanical Room B',
                'manufacturer': 'Grundfos',
                'model': 'Hydro MPC-S',
                'serial_number': 'PMP2023001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },
            {
                'name': 'AO Smith Water Heater - 100 Gallon',
                'description': 'Gas water heater for restroom facilities',
                'asset_tag': 'PLMB-WH-001',
                'category': AssetCategory.PLUMBING,
                'subcategory': 'Water Heater',
                'building': 'Main Building',
                'floor': 'Basement',
                'room': 'Mechanical Room B',
                'manufacturer': 'AO Smith',
                'model': 'BTH-100',
                'serial_number': 'WH2023001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.FAIR
            },
            {
                'name': 'Sewage Ejector Pump',
                'description': 'Basement wastewater pump system',
                'asset_tag': 'PLMB-SEW-001',
                'category': AssetCategory.PLUMBING,
                'subcategory': 'Sewage System',
                'building': 'Main Building',
                'floor': 'Basement',
                'room': 'Pump Room',
                'manufacturer': 'Liberty Pumps',
                'model': 'PRG101A',
                'serial_number': 'SEW2023001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },
            {
                'name': 'Backflow Prevention Device',
                'description': 'RPZ backflow preventer for main water line',
                'asset_tag': 'PLMB-BFP-001',
                'category': AssetCategory.PLUMBING,
                'subcategory': 'Water Safety',
                'building': 'Main Building',
                'floor': 'Basement',
                'room': 'Water Entry Room',
                'manufacturer': 'Watts',
                'model': '909 RPZ',
                'serial_number': 'BFP2023001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },

            # ===== MANUFACTURING/FACTORY EQUIPMENT =====
            {
                'name': 'CNC Milling Machine - Haas VF-4',
                'description': '3-axis vertical machining center',
                'asset_tag': 'MFG-CNC-001',
                'category': AssetCategory.OTHER,
                'subcategory': 'Manufacturing Equipment',
                'building': 'Factory Building',
                'floor': '1',
                'location_details': 'Production Floor - Station 12',
                'manufacturer': 'Haas Automation',
                'model': 'VF-4',
                'serial_number': 'CNC2023001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },
            {
                'name': 'Industrial Air Compressor - 100HP',
                'description': 'Rotary screw air compressor for plant operations',
                'asset_tag': 'MFG-COMP-001',
                'category': AssetCategory.OTHER,
                'subcategory': 'Compressed Air',
                'building': 'Factory Building',
                'floor': '1',
                'room': 'Compressor Room',
                'manufacturer': 'Atlas Copco',
                'model': 'GA 75 VSD',
                'serial_number': 'COMP2023001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.EXCELLENT
            },
            {
                'name': 'Overhead Crane - 10 Ton',
                'description': 'Bridge crane for heavy material handling',
                'asset_tag': 'MFG-CRANE-001',
                'category': AssetCategory.OTHER,
                'subcategory': 'Material Handling',
                'building': 'Factory Building',
                'floor': '1',
                'location_details': 'Bay 3 - Span 60ft',
                'manufacturer': 'Konecranes',
                'model': 'CXT 10 Ton',
                'serial_number': 'CRANE2023001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },
            {
                'name': 'Forklift - Electric 5000lb Capacity',
                'description': 'Battery-powered forklift for warehouse operations',
                'asset_tag': 'MFG-FORK-001',
                'category': AssetCategory.OTHER,
                'subcategory': 'Material Handling',
                'building': 'Warehouse',
                'floor': '1',
                'manufacturer': 'Toyota',
                'model': '8FBCU25',
                'serial_number': 'FORK2023001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.FAIR
            },
            {
                'name': 'Industrial Conveyor Belt System',
                'description': 'Automated parts conveyor system',
                'asset_tag': 'MFG-CONV-001',
                'category': AssetCategory.OTHER,
                'subcategory': 'Material Handling',
                'building': 'Factory Building',
                'floor': '1',
                'location_details': 'Production Line 1 - 50ft length',
                'manufacturer': 'Dorner',
                'model': '2200 Series',
                'serial_number': 'CONV2023001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },

            # ===== SERVICE STATION EQUIPMENT =====
            {
                'name': 'Gas Pump Dispenser - Pump 1',
                'description': 'Multi-product fuel dispenser',
                'asset_tag': 'SVC-PUMP-001',
                'category': AssetCategory.OTHER,
                'subcategory': 'Fuel Equipment',
                'building': 'Service Station',
                'location_details': 'Island 1 - Position A',
                'manufacturer': 'Gilbarco Veeder-Root',
                'model': 'Encore 700 S',
                'serial_number': 'PUMP2024001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },
            {
                'name': 'Gas Pump Dispenser - Pump 2',
                'description': 'Multi-product fuel dispenser',
                'asset_tag': 'SVC-PUMP-002',
                'category': AssetCategory.OTHER,
                'subcategory': 'Fuel Equipment',
                'building': 'Service Station',
                'location_details': 'Island 1 - Position B',
                'manufacturer': 'Gilbarco Veeder-Root',
                'model': 'Encore 700 S',
                'serial_number': 'PUMP2024002',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },
            {
                'name': 'Underground Fuel Tank - Regular Unleaded',
                'description': '10,000 gallon double-wall fiberglass tank',
                'asset_tag': 'SVC-TANK-001',
                'category': AssetCategory.OTHER,
                'subcategory': 'Fuel Storage',
                'building': 'Service Station',
                'location_details': 'Underground - North side',
                'manufacturer': 'Containment Solutions',
                'model': 'Titan UL Steel',
                'serial_number': 'TANK2023001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },
            {
                'name': 'Car Wash System - Automatic',
                'description': 'Touchless automatic car wash system',
                'asset_tag': 'SVC-WASH-001',
                'category': AssetCategory.OTHER,
                'subcategory': 'Vehicle Service',
                'building': 'Service Station',
                'location_details': 'Car Wash Bay',
                'manufacturer': 'PDQ',
                'model': 'LaserWash 360 Plus',
                'serial_number': 'WASH2024001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.EXCELLENT
            },
            {
                'name': 'Automotive Lift - 2 Post 10,000lb',
                'description': 'Vehicle lift for maintenance bay',
                'asset_tag': 'SVC-LIFT-001',
                'category': AssetCategory.OTHER,
                'subcategory': 'Vehicle Service',
                'building': 'Service Station',
                'room': 'Service Bay 1',
                'manufacturer': 'BendPak',
                'model': 'XPR-10A',
                'serial_number': 'LIFT2024001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },
            {
                'name': 'Air Compressor - 60 Gallon',
                'description': 'Shop air compressor for tire service and tools',
                'asset_tag': 'SVC-AIR-001',
                'category': AssetCategory.OTHER,
                'subcategory': 'Shop Equipment',
                'building': 'Service Station',
                'room': 'Equipment Room',
                'manufacturer': 'Ingersoll Rand',
                'model': '2340N5-V',
                'serial_number': 'AIR2024001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.FAIR
            },

            # ===== BUILDING & FACILITIES =====
            {
                'name': 'Passenger Elevator - Main Lobby',
                'description': '8-passenger hydraulic elevator',
                'asset_tag': 'BLDG-ELEV-001',
                'category': AssetCategory.BUILDING,
                'subcategory': 'Elevator',
                'building': 'Main Building',
                'location_details': 'Main Lobby - Car 1',
                'manufacturer': 'Otis',
                'model': 'Gen2',
                'serial_number': 'ELEV2022001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.EXCELLENT
            },
            {
                'name': 'Security Camera System - NVR',
                'description': 'Network video recorder for 32 cameras',
                'asset_tag': 'BLDG-SEC-001',
                'category': AssetCategory.IT_EQUIPMENT,
                'subcategory': 'Security',
                'building': 'Main Building',
                'floor': '1',
                'room': 'Security Office',
                'manufacturer': 'Hikvision',
                'model': 'DS-7732NI-K4',
                'serial_number': 'SEC2023001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },
            {
                'name': 'Access Control System',
                'description': 'Badge reader access control for all entry points',
                'asset_tag': 'BLDG-ACC-001',
                'category': AssetCategory.ELECTRICAL,
                'subcategory': 'Access Control',
                'building': 'Main Building',
                'floor': '1',
                'room': 'Security Office',
                'manufacturer': 'HID Global',
                'model': 'VertX V2000',
                'serial_number': 'ACC2023001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },
            {
                'name': 'Commercial Kitchen Refrigerator',
                'description': 'Walk-in cooler for cafeteria',
                'asset_tag': 'BLDG-KITCHEN-001',
                'category': AssetCategory.OTHER,
                'subcategory': 'Kitchen Equipment',
                'building': 'Main Building',
                'floor': '1',
                'room': 'Cafeteria Kitchen',
                'manufacturer': 'Kolpak',
                'model': 'Walk-In 8x10',
                'serial_number': 'KITCH2023001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },

            # ===== OFFICE FURNITURE & EQUIPMENT =====
            {
                'name': 'Conference Room AV System',
                'description': 'Video conferencing and presentation system',
                'asset_tag': 'OFC-AV-001',
                'category': AssetCategory.IT_EQUIPMENT,
                'subcategory': 'Audio Visual',
                'building': 'Main Building',
                'floor': '2',
                'room': 'Conference Room A',
                'manufacturer': 'Crestron',
                'model': 'Mercury CCS-UC-1',
                'serial_number': 'AV2024001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.EXCELLENT
            },
            {
                'name': 'Commercial Copy Machine',
                'description': 'Multifunction printer/copier/scanner',
                'asset_tag': 'OFC-COPY-001',
                'category': AssetCategory.IT_EQUIPMENT,
                'subcategory': 'Office Equipment',
                'building': 'Main Building',
                'floor': '2',
                'room': 'Copy Room',
                'manufacturer': 'Xerox',
                'model': 'VersaLink C7000',
                'serial_number': 'COPY2024001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.GOOD
            },
            {
                'name': 'Office Desk - Height Adjustable',
                'description': 'Electric standing desk workstation',
                'asset_tag': 'FRN-DESK-001',
                'category': AssetCategory.FURNITURE,
                'subcategory': 'Desk',
                'building': 'Main Building',
                'floor': '2',
                'room': 'Office 201',
                'manufacturer': 'Steelcase',
                'model': 'Ology Height-Adjustable',
                'serial_number': 'DESK2024001',
                'status': AssetStatus.ACTIVE,
                'condition': AssetCondition.EXCELLENT
            },
        ]

        # Track creation
        created_count = 0
        skipped_count = 0

        print("\nCreating assets...")
        for asset_data in assets_data:
            try:
                # Check if asset already exists
                existing = asset_repo.get_by_asset_tag(asset_data['asset_tag'])
                if existing:
                    print(f"   Skipped: {asset_data['asset_tag']} (already exists)")
                    skipped_count += 1
                    continue

                # Set random purchase date (1-5 years ago)
                years_ago = random.randint(1, 5)
                purchase_date = datetime.now().date() - timedelta(days=years_ago*365 + random.randint(0, 365))
                asset_data['purchase_date'] = purchase_date

                # Set warranty expiry (1-3 years from purchase)
                warranty_years = random.randint(1, 3)
                asset_data['warranty_expiry'] = purchase_date + timedelta(days=warranty_years*365)

                # Create asset
                asset = asset_repo.create_asset(**asset_data)
                print(f"   Created: {asset.asset_tag} - {asset.name}")
                created_count += 1

            except Exception as e:
                print(f"   Failed to create {asset_data['asset_tag']}: {str(e)}")
                continue

        print(f"\n[SUCCESS] Created {created_count} assets")
        if skipped_count > 0:
            print(f"[INFO] Skipped {skipped_count} existing assets")

        # Print final statistics
        all_assets = asset_repo.get_all()
        print(f"\n=== Final Asset Statistics ===")
        print(f"Total Assets: {len(all_assets)}")
        print(f"\nBy Category:")
        for category in AssetCategory:
            count = len([a for a in all_assets if a.category == category])
            if count > 0:
                print(f"  {category.value}: {count}")

        print(f"\nBy Status:")
        for status in AssetStatus:
            count = len([a for a in all_assets if a.status == status])
            if count > 0:
                print(f"  {status.value}: {count}")

        print("\n[SUCCESS] Comprehensive asset seeding complete!")

if __name__ == '__main__':
    seed_comprehensive_assets()
