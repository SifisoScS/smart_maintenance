"""
Seed Feature Flags

Populates the database with initial feature flags.

Run with: python seed_feature_flags.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
from app.models.feature_flag import FeatureFlag, FeatureCategory, Features
from app.repositories.feature_flag_repository import FeatureFlagRepository

def seed_feature_flags():
    """Seed initial feature flags into the database."""

    app = create_app('development')

    with app.app_context():
        repository = FeatureFlagRepository()

        # Define initial feature flags
        feature_flags = [
            # Analytics features
            {
                'feature_key': Features.ADVANCED_REPORTING,
                'name': 'Advanced Reporting',
                'description': 'Advanced analytics dashboard with custom metrics and data visualization',
                'category': FeatureCategory.ANALYTICS,
                'enabled': True,  # Enable by default
                'rollout_percentage': 100
            },
            {
                'feature_key': Features.PREDICTIVE_ANALYTICS,
                'name': 'Predictive Analytics',
                'description': 'ML-based predictions for maintenance needs and equipment failures',
                'category': FeatureCategory.ANALYTICS,
                'enabled': False,  # Experimental feature
                'rollout_percentage': 0
            },
            {
                'feature_key': Features.CUSTOM_DASHBOARDS,
                'name': 'Custom Dashboards',
                'description': 'Create and customize personal dashboards',
                'category': FeatureCategory.ANALYTICS,
                'enabled': False,
                'rollout_percentage': 50  # 50% rollout
            },
            {
                'feature_key': Features.DATA_EXPORT,
                'name': 'Data Export',
                'description': 'Export reports and data to CSV, Excel, and PDF formats',
                'category': FeatureCategory.ANALYTICS,
                'enabled': True,
                'rollout_percentage': 100
            },

            # Notification features
            {
                'feature_key': Features.EMAIL_NOTIFICATIONS,
                'name': 'Email Notifications',
                'description': 'Send email notifications for maintenance updates',
                'category': FeatureCategory.NOTIFICATIONS,
                'enabled': True,
                'rollout_percentage': 100
            },
            {
                'feature_key': Features.SMS_NOTIFICATIONS,
                'name': 'SMS Notifications',
                'description': 'Send SMS alerts for urgent maintenance requests',
                'category': FeatureCategory.NOTIFICATIONS,
                'enabled': False,
                'rollout_percentage': 0
            },
            {
                'feature_key': Features.PUSH_NOTIFICATIONS,
                'name': 'Push Notifications',
                'description': 'Real-time push notifications to mobile and web',
                'category': FeatureCategory.NOTIFICATIONS,
                'enabled': False,
                'rollout_percentage': 0
            },
            {
                'feature_key': Features.IN_APP_NOTIFICATIONS,
                'name': 'In-App Notifications',
                'description': 'Notification center within the application',
                'category': FeatureCategory.NOTIFICATIONS,
                'enabled': True,
                'rollout_percentage': 100
            },

            # Integration features
            {
                'feature_key': Features.API_ACCESS,
                'name': 'API Access',
                'description': 'REST API access for third-party integrations',
                'category': FeatureCategory.INTEGRATIONS,
                'enabled': True,
                'rollout_percentage': 100
            },
            {
                'feature_key': Features.WEBHOOK_INTEGRATIONS,
                'name': 'Webhook Integrations',
                'description': 'Configure webhooks for external system notifications',
                'category': FeatureCategory.INTEGRATIONS,
                'enabled': False,
                'rollout_percentage': 0
            },
            {
                'feature_key': Features.THIRD_PARTY_SYNC,
                'name': 'Third-Party Sync',
                'description': 'Sync data with external CMMS and ERP systems',
                'category': FeatureCategory.INTEGRATIONS,
                'enabled': False,
                'rollout_percentage': 0
            },

            # Mobile features
            {
                'feature_key': Features.MOBILE_APP_ACCESS,
                'name': 'Mobile App Access',
                'description': 'Access system via mobile applications',
                'category': FeatureCategory.MOBILE,
                'enabled': True,
                'rollout_percentage': 100
            },
            {
                'feature_key': Features.OFFLINE_MODE,
                'name': 'Offline Mode',
                'description': 'Work offline and sync when connection is restored',
                'category': FeatureCategory.MOBILE,
                'enabled': False,
                'rollout_percentage': 0
            },
            {
                'feature_key': Features.BARCODE_SCANNING,
                'name': 'Barcode Scanning',
                'description': 'Scan asset barcodes and QR codes for quick lookup',
                'category': FeatureCategory.MOBILE,
                'enabled': True,
                'rollout_percentage': 100
            },

            # Automation features
            {
                'feature_key': Features.CUSTOM_WORKFLOWS,
                'name': 'Custom Workflows',
                'description': 'Create custom approval and routing workflows',
                'category': FeatureCategory.AUTOMATION,
                'enabled': False,
                'rollout_percentage': 0
            },
            {
                'feature_key': Features.AUTO_ASSIGNMENT,
                'name': 'Auto Assignment',
                'description': 'Automatically assign requests to available technicians',
                'category': FeatureCategory.AUTOMATION,
                'enabled': True,
                'rollout_percentage': 100
            },
            {
                'feature_key': Features.SCHEDULED_MAINTENANCE,
                'name': 'Scheduled Maintenance',
                'description': 'Create recurring maintenance schedules',
                'category': FeatureCategory.AUTOMATION,
                'enabled': True,
                'rollout_percentage': 100
            },

            # Asset features
            {
                'feature_key': Features.ASSET_QR_CODES,
                'name': 'Asset QR Codes',
                'description': 'Generate QR codes for asset identification',
                'category': FeatureCategory.UI,
                'enabled': True,
                'rollout_percentage': 100
            },
            {
                'feature_key': Features.ASSET_TRACKING,
                'name': 'Asset Tracking',
                'description': 'Real-time asset location and movement tracking',
                'category': FeatureCategory.UI,
                'enabled': False,
                'rollout_percentage': 0
            },
            {
                'feature_key': Features.ASSET_LIFECYCLE,
                'name': 'Asset Lifecycle Management',
                'description': 'Track asset lifecycle from procurement to retirement',
                'category': FeatureCategory.UI,
                'enabled': True,
                'rollout_percentage': 100
            },

            # Security features
            {
                'feature_key': Features.TWO_FACTOR_AUTH,
                'name': 'Two-Factor Authentication',
                'description': 'Enhanced security with 2FA',
                'category': FeatureCategory.SECURITY,
                'enabled': False,
                'rollout_percentage': 0
            },
            {
                'feature_key': Features.AUDIT_LOGGING,
                'name': 'Audit Logging',
                'description': 'Comprehensive audit logs for all system actions',
                'category': FeatureCategory.SECURITY,
                'enabled': True,
                'rollout_percentage': 100
            },
            {
                'feature_key': Features.IP_WHITELISTING,
                'name': 'IP Whitelisting',
                'description': 'Restrict access to whitelisted IP addresses',
                'category': FeatureCategory.SECURITY,
                'enabled': False,
                'rollout_percentage': 0
            },

            # UI features
            {
                'feature_key': Features.DARK_MODE,
                'name': 'Dark Mode',
                'description': 'Dark theme for reduced eye strain',
                'category': FeatureCategory.UI,
                'enabled': True,
                'rollout_percentage': 100
            },
            {
                'feature_key': Features.COMPACT_VIEW,
                'name': 'Compact View',
                'description': 'Condensed view for displaying more data',
                'category': FeatureCategory.UI,
                'enabled': True,
                'rollout_percentage': 100
            },
            {
                'feature_key': Features.DRAG_DROP_UI,
                'name': 'Drag and Drop UI',
                'description': 'Drag and drop interface for workflow customization',
                'category': FeatureCategory.UI,
                'enabled': False,
                'rollout_percentage': 0
            },
        ]

        # Create or update feature flags
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for flag_data in feature_flags:
            existing = repository.get_by_key(flag_data['feature_key'])

            if existing:
                print(f"[SKIP] Feature flag '{flag_data['feature_key']}' already exists")
                skipped_count += 1
            else:
                flag = FeatureFlag(**flag_data)
                repository.create(flag)
                status = "ENABLED" if flag.enabled else "DISABLED"
                print(f"[CREATE] {flag.feature_key} - {flag.name} ({status})")
                created_count += 1

        print(f"\n=== Summary ===")
        print(f"Created: {created_count}")
        print(f"Skipped (already exists): {skipped_count}")
        print(f"Total feature flags in DB: {len(repository.get_all())}")

        # Show category breakdown
        print(f"\n=== By Category ===")
        all_flags = repository.get_all()
        by_category = {}
        for flag in all_flags:
            category = flag.category.value
            by_category[category] = by_category.get(category, 0) + 1

        for category, count in sorted(by_category.items()):
            enabled_count = len([f for f in all_flags if f.category.value == category and f.enabled])
            print(f"  {category}: {count} total ({enabled_count} enabled)")

        print(f"\n[SUCCESS] Feature flags seeded successfully!")


if __name__ == '__main__':
    seed_feature_flags()
