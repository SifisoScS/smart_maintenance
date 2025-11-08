"""
Demo: Strategy Pattern + Service Layer Integration

Demonstrates how patterns work together:
- Strategy Pattern: Pluggable notification methods
- Service Layer: Business logic orchestration
- Dependency Injection: Runtime strategy switching
"""

from app import create_app
from app.repositories import UserRepository
from app.services.notification_service import NotificationService
from app.patterns.strategy import (
    EmailNotificationStrategy,
    SMSNotificationStrategy,
    InAppNotificationStrategy
)


def demo_strategy_pattern():
    """Demonstrate Strategy Pattern with NotificationService"""

    app = create_app('development')

    with app.app_context():
        print("="*70)
        print("STRATEGY PATTERN + SERVICE LAYER DEMONSTRATION")
        print("="*70)

        # Initialize repositories
        user_repo = UserRepository()

        # Get sample users
        admin = user_repo.get_by_email('admin@smartmaintenance.com')
        tech = user_repo.get_by_email('john.tech@smartmaintenance.com')
        client = user_repo.get_by_email('sarah.client@smartmaintenance.com')

        if not all([admin, tech, client]):
            print("\n[ERROR] Sample users not found. Run 'python seed_data.py' first.")
            return

        print(f"\n[*] Sample Users Loaded:")
        print(f"   - Admin: {admin.email}")
        print(f"   - Technician: {tech.email}")
        print(f"   - Client: {client.email}")

        # Demo 1: Email Notification Strategy
        print("\n" + "="*70)
        print("DEMO 1: Email Notification Strategy")
        print("="*70)

        email_strategy = EmailNotificationStrategy(
            smtp_host='smtp.gmail.com',
            smtp_port=587,
            username='noreply@smartmaintenance.com',
            password='dummy-password'
        )

        notification_service = NotificationService(user_repo, email_strategy)

        result = notification_service.notify_user(
            user_id=tech.id,
            subject='New Maintenance Request Assigned',
            message='You have been assigned to fix the parking lot lights. Priority: URGENT'
        )

        print(f"\n[EMAIL] Email Strategy Result:")
        print(f"   Success: {result['success']}")
        print(f"   Message: {result.get('message', result.get('error'))}")

        # Demo 2: Runtime Strategy Switching (SMS)
        print("\n" + "="*70)
        print("DEMO 2: Runtime Strategy Switching - SMS")
        print("="*70)

        sms_strategy = SMSNotificationStrategy(
            api_key='dummy-api-key',
            api_url='https://api.smsgateway.com/send',
            sender_number='+1-555-0100'
        )

        # Switch strategy at runtime (Strategy Pattern benefit!)
        notification_service.set_strategy(sms_strategy)

        result = notification_service.notify_user(
            user_id=tech.id,
            subject='Urgent',
            message='Emergency: Server room temperature critical! Respond ASAP.'
        )

        print(f"\n[SMS] SMS Strategy Result:")
        print(f"   Success: {result['success']}")
        if result['success']:
            print(f"   Strategy Used: {result['data']['strategy']}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
            print(f"   Note: Phone validation requires format like +1-555-0101")

        # Demo 3: In-App Notification Strategy
        print("\n" + "="*70)
        print("DEMO 3: In-App Notification Strategy")
        print("="*70)

        from app.database import db
        inapp_strategy = InAppNotificationStrategy(db.session)

        notification_service.set_strategy(inapp_strategy)

        result = notification_service.notify_user(
            user_id=client.id,
            subject='Request Status Updated',
            message='Your maintenance request #3 is now in progress.',
            priority='high',
            link='/requests/3'
        )

        print(f"\n[IN-APP] In-App Strategy Result:")
        print(f"   Success: {result['success']}")
        print(f"   Strategy Used: {result['data']['strategy']}")

        # Demo 4: Bulk Notifications to Multiple Users
        print("\n" + "="*70)
        print("DEMO 4: Bulk Notifications (Multiple Users)")
        print("="*70)

        # Switch back to email for bulk
        notification_service.set_strategy(email_strategy)

        result = notification_service.notify_multiple_users(
            user_ids=[admin.id, tech.id, client.id],
            subject='System Maintenance Notice',
            message='Scheduled maintenance on Sunday at 2 AM. System will be unavailable for 1 hour.'
        )

        print(f"\n[BULK] Bulk Notification Results:")
        print(f"   Total Users: {result['data']['total']}")
        print(f"   Successful: {result['data']['successful']}")
        print(f"   Failed: {result['data']['failed']}")

        # Demo 5: Role-Based Notifications
        print("\n" + "="*70)
        print("DEMO 5: Role-Based Notifications (All Technicians)")
        print("="*70)

        result = notification_service.notify_by_role(
            role='technician',
            subject='Monthly Team Meeting',
            message='All technicians: Monthly meeting on Friday at 10 AM in Conference Room A.'
        )

        print(f"\n[ROLE] Role-Based Notification Results:")
        print(f"   Total Technicians: {result['data']['total']}")
        print(f"   Successful: {result['data']['successful']}")
        print(f"   Message: {result['message']}")

        # Demo 6: Notification History
        print("\n" + "="*70)
        print("DEMO 6: Notification History")
        print("="*70)

        history = notification_service.get_notification_history(limit=10)

        print(f"\n[HISTORY] Recent Notifications (last {len(history)}):")
        for i, notif in enumerate(history[-5:], 1):  # Show last 5
            print(f"\n   {i}. User ID: {notif['user_id']}")
            print(f"      Subject: {notif['subject']}")
            print(f"      Strategy: {notif['strategy']}")
            print(f"      Time: {notif['timestamp']}")

        # Demo 7: Pattern Benefits Summary
        print("\n" + "="*70)
        print("PATTERN BENEFITS DEMONSTRATED")
        print("="*70)

        print("""
[+] STRATEGY PATTERN BENEFITS:
   - Runtime strategy switching (Email -> SMS -> In-App)
   - No if/else chains for notification types
   - Easy to add new strategies (Push, Slack, etc.)
   - Each strategy encapsulates its own logic

[+] SERVICE LAYER BENEFITS:
   - Business logic separate from controllers
   - Reusable across multiple entry points
   - Easy to test (mock repositories)
   - Transaction management in one place

[+] DEPENDENCY INJECTION BENEFITS:
   - Loose coupling (service doesn't create dependencies)
   - Easy to swap implementations
   - Testable with mocks

[+] OOP PRINCIPLES APPLIED:
   - Single Responsibility: Each strategy handles one method
   - Open/Closed: Add strategies without modifying service
   - Liskov Substitution: All strategies interchangeable
   - Dependency Inversion: Depends on abstractions
        """)

        print("="*70)
        print("DEMONSTRATION COMPLETE!")
        print("="*70)
        print("\nNext: Run unit tests to verify everything works:")
        print("  pytest tests/unit/ -v")
        print("\nOr continue to Phase 2 services...")


if __name__ == '__main__':
    demo_strategy_pattern()
