"""
Unit Tests for NotificationService

Tests:
- Strategy pattern integration
- Runtime strategy switching
- User notification validation
- Bulk notifications
- Role-based notifications
- Notification history tracking
"""

import pytest
from unittest.mock import Mock, MagicMock
from app.services.notification_service import NotificationService
from app.patterns.strategy import (
    EmailNotificationStrategy,
    SMSNotificationStrategy,
    InAppNotificationStrategy
)
from app.models import User, UserRole


class TestNotificationServiceInitialization:
    """Test service initialization and strategy setup."""

    def test_init_with_default_strategy(self):
        """Test initialization with default strategy."""
        user_repo = Mock()
        strategy = Mock()

        service = NotificationService(user_repo, strategy)

        assert service.user_repo == user_repo
        assert service.context.strategy == strategy

    def test_init_without_strategy(self):
        """Test initialization without default strategy."""
        user_repo = Mock()

        service = NotificationService(user_repo)

        assert service.user_repo == user_repo
        assert service.context.strategy is None

    def test_set_strategy_runtime(self):
        """Test runtime strategy switching."""
        user_repo = Mock()
        initial_strategy = Mock()
        new_strategy = Mock()

        service = NotificationService(user_repo, initial_strategy)
        service.set_strategy(new_strategy)

        assert service.context.strategy == new_strategy


class TestNotifyUser:
    """Test single user notification functionality."""

    def test_notify_user_success_with_email_strategy(self):
        """Test successful notification with email strategy."""
        # Setup
        user_repo = Mock()
        user = Mock()
        user.id = 1
        user.email = 'test@example.com'
        user.full_name = 'Test User'
        user.is_active = True
        user_repo.get_by_id.return_value = user

        strategy = Mock(spec=EmailNotificationStrategy)
        strategy.get_strategy_name.return_value = 'email'
        strategy.send.return_value = True

        service = NotificationService(user_repo, strategy)

        # Execute
        result = service.notify_user(
            user_id=1,
            subject='Test Subject',
            message='Test Message'
        )

        # Assert
        assert result['success'] is True
        assert result['data']['sent'] is True
        assert result['data']['strategy'] == 'email'
        assert 'Test User' in result['message']
        user_repo.get_by_id.assert_called_once_with(1)
        strategy.send.assert_called_once()

    def test_notify_user_no_strategy_configured(self):
        """Test notification fails when no strategy configured."""
        user_repo = Mock()
        service = NotificationService(user_repo)

        result = service.notify_user(
            user_id=1,
            subject='Test',
            message='Test'
        )

        assert result['success'] is False
        assert 'No notification strategy configured' in result['error']

    def test_notify_user_not_found(self):
        """Test notification fails when user not found."""
        user_repo = Mock()
        user_repo.get_by_id.return_value = None
        strategy = Mock()

        service = NotificationService(user_repo, strategy)

        result = service.notify_user(
            user_id=999,
            subject='Test',
            message='Test'
        )

        assert result['success'] is False
        assert 'not found' in result['error']

    def test_notify_user_inactive(self):
        """Test notification fails for inactive user."""
        user_repo = Mock()
        user = Mock()
        user.id = 1
        user.is_active = False
        user_repo.get_by_id.return_value = user
        strategy = Mock()

        service = NotificationService(user_repo, strategy)

        result = service.notify_user(
            user_id=1,
            subject='Test',
            message='Test'
        )

        assert result['success'] is False
        assert 'not active' in result['error']

    def test_notify_user_missing_recipient_info(self):
        """Test notification fails when user missing recipient info (e.g., phone for SMS)."""
        user_repo = Mock()
        user = Mock()
        user.id = 1
        user.is_active = True
        user.phone = None  # No phone number
        user_repo.get_by_id.return_value = user

        strategy = Mock(spec=SMSNotificationStrategy)
        strategy.get_strategy_name.return_value = 'sms'

        service = NotificationService(user_repo, strategy)

        result = service.notify_user(
            user_id=1,
            subject='Test',
            message='Test'
        )

        assert result['success'] is False
        assert 'No sms configured' in result['error']

    def test_notify_user_validation_errors(self):
        """Test validation of required fields."""
        user_repo = Mock()
        strategy = Mock()
        service = NotificationService(user_repo, strategy)

        # Missing user_id
        result = service.notify_user(user_id=None, subject='Test', message='Test')
        assert result['success'] is False
        assert 'user_id is required' in result['error']

        # Missing subject (empty string)
        result = service.notify_user(user_id=1, subject='', message='Test')
        assert result['success'] is False
        assert 'subject cannot be empty' in result['error']

        # Missing message (empty string)
        result = service.notify_user(user_id=1, subject='Test', message='')
        assert result['success'] is False
        assert 'message cannot be empty' in result['error']

    def test_notify_user_strategy_send_fails(self):
        """Test notification fails when strategy send returns False."""
        user_repo = Mock()
        user = Mock()
        user.id = 1
        user.email = 'test@example.com'
        user.is_active = True
        user_repo.get_by_id.return_value = user

        strategy = Mock()
        strategy.get_strategy_name.return_value = 'email'
        strategy.send.return_value = False  # Send fails

        service = NotificationService(user_repo, strategy)

        result = service.notify_user(
            user_id=1,
            subject='Test',
            message='Test'
        )

        assert result['success'] is False
        assert 'Failed to send notification' in result['error']

    def test_notify_user_records_history(self):
        """Test notification is recorded in history."""
        user_repo = Mock()
        user = Mock()
        user.id = 1
        user.email = 'test@example.com'
        user.full_name = 'Test User'
        user.is_active = True
        user_repo.get_by_id.return_value = user

        strategy = Mock()
        strategy.get_strategy_name.return_value = 'email'
        strategy.send.return_value = True

        service = NotificationService(user_repo, strategy)

        service.notify_user(
            user_id=1,
            subject='Test Subject',
            message='Test Message'
        )

        history = service.get_notification_history()

        assert len(history) == 1
        assert history[0]['user_id'] == 1
        assert history[0]['subject'] == 'Test Subject'
        assert history[0]['message'] == 'Test Message'
        assert history[0]['strategy'] == 'email'
        assert history[0]['status'] == 'sent'


class TestNotifyMultipleUsers:
    """Test bulk notification functionality."""

    def test_notify_multiple_users_all_success(self):
        """Test bulk notification when all succeed."""
        user_repo = Mock()
        strategy = Mock()
        strategy.get_strategy_name.return_value = 'email'
        strategy.send.return_value = True

        service = NotificationService(user_repo, strategy)

        # Mock users
        for i in [1, 2, 3]:
            user = Mock()
            user.id = i
            user.email = f'user{i}@example.com'
            user.full_name = f'User {i}'
            user.is_active = True
            user_repo.get_by_id.side_effect = lambda uid: user if user.id == uid else None

        # Return appropriate user for each call
        users = []
        for i in [1, 2, 3]:
            user = Mock()
            user.id = i
            user.email = f'user{i}@example.com'
            user.full_name = f'User {i}'
            user.is_active = True
            users.append(user)

        user_repo.get_by_id.side_effect = lambda uid: users[uid - 1]

        result = service.notify_multiple_users(
            user_ids=[1, 2, 3],
            subject='Bulk Test',
            message='Bulk Message'
        )

        assert result['success'] is True
        assert result['data']['total'] == 3
        assert result['data']['successful'] == 3
        assert result['data']['failed'] == 0
        assert len(result['data']['errors']) == 0

    def test_notify_multiple_users_partial_success(self):
        """Test bulk notification with partial failures."""
        user_repo = Mock()
        strategy = Mock()
        strategy.get_strategy_name.return_value = 'email'
        strategy.send.return_value = True

        service = NotificationService(user_repo, strategy)

        # Mock users: user 1 and 3 exist, user 2 doesn't
        user1 = Mock()
        user1.id = 1
        user1.email = 'user1@example.com'
        user1.full_name = 'User 1'
        user1.is_active = True

        user3 = Mock()
        user3.id = 3
        user3.email = 'user3@example.com'
        user3.full_name = 'User 3'
        user3.is_active = True

        def get_user_side_effect(uid):
            if uid == 1:
                return user1
            elif uid == 3:
                return user3
            else:
                return None

        user_repo.get_by_id.side_effect = get_user_side_effect

        result = service.notify_multiple_users(
            user_ids=[1, 2, 3],
            subject='Bulk Test',
            message='Bulk Message'
        )

        assert result['success'] is True
        assert result['data']['total'] == 3
        assert result['data']['successful'] == 2
        assert result['data']['failed'] == 1
        assert len(result['data']['errors']) == 1
        assert result['data']['errors'][0]['user_id'] == 2

    def test_notify_multiple_users_validation_error(self):
        """Test validation of user_ids parameter."""
        user_repo = Mock()
        strategy = Mock()
        service = NotificationService(user_repo, strategy)

        # Not a list
        result = service.notify_multiple_users(
            user_ids=123,
            subject='Test',
            message='Test'
        )

        assert result['success'] is False
        assert 'must be a list' in result['error']


class TestNotifyByRole:
    """Test role-based notification functionality."""

    def test_notify_by_role_success(self):
        """Test notification to all users with specific role."""
        user_repo = Mock()
        strategy = Mock()
        strategy.get_strategy_name.return_value = 'email'
        strategy.send.return_value = True

        service = NotificationService(user_repo, strategy)

        # Mock technicians
        tech1 = Mock()
        tech1.id = 1
        tech1.email = 'tech1@example.com'
        tech1.full_name = 'Tech 1'
        tech1.is_active = True

        tech2 = Mock()
        tech2.id = 2
        tech2.email = 'tech2@example.com'
        tech2.full_name = 'Tech 2'
        tech2.is_active = True

        user_repo.get_by_role.return_value = [tech1, tech2]
        user_repo.get_by_id.side_effect = lambda uid: tech1 if uid == 1 else tech2

        result = service.notify_by_role(
            role='technician',
            subject='Team Meeting',
            message='Meeting tomorrow'
        )

        assert result['success'] is True
        assert result['data']['total'] == 2
        assert result['data']['successful'] == 2
        user_repo.get_by_role.assert_called_once()

    def test_notify_by_role_filters_inactive_users(self):
        """Test role notification skips inactive users."""
        user_repo = Mock()
        strategy = Mock()
        strategy.get_strategy_name.return_value = 'email'
        strategy.send.return_value = True

        service = NotificationService(user_repo, strategy)

        # Mock users: one active, one inactive
        active_user = Mock()
        active_user.id = 1
        active_user.email = 'active@example.com'
        active_user.full_name = 'Active User'
        active_user.is_active = True

        inactive_user = Mock()
        inactive_user.id = 2
        inactive_user.is_active = False

        user_repo.get_by_role.return_value = [active_user, inactive_user]
        user_repo.get_by_id.return_value = active_user

        result = service.notify_by_role(
            role='technician',
            subject='Test',
            message='Test'
        )

        # Should only notify active user
        assert result['success'] is True
        assert result['data']['total'] == 1
        assert result['data']['successful'] == 1

    def test_notify_by_role_invalid_role(self):
        """Test notification fails with invalid role."""
        user_repo = Mock()
        strategy = Mock()
        service = NotificationService(user_repo, strategy)

        result = service.notify_by_role(
            role='invalid_role',
            subject='Test',
            message='Test'
        )

        assert result['success'] is False
        assert 'Invalid role' in result['error']

    def test_notify_by_role_no_users_found(self):
        """Test notification when no users with role exist."""
        user_repo = Mock()
        user_repo.get_by_role.return_value = []
        strategy = Mock()

        service = NotificationService(user_repo, strategy)

        result = service.notify_by_role(
            role='admin',
            subject='Test',
            message='Test'
        )

        assert result['success'] is True
        assert result['data']['total'] == 0
        assert 'No active admin users found' in result['message']


class TestNotificationHistory:
    """Test notification history tracking."""

    def test_get_notification_history_all(self):
        """Test retrieving all notification history."""
        user_repo = Mock()
        strategy = Mock()
        strategy.get_strategy_name.return_value = 'email'
        strategy.send.return_value = True

        service = NotificationService(user_repo, strategy)

        # Send notifications
        for i in range(1, 4):
            user = Mock()
            user.id = i
            user.email = f'user{i}@example.com'
            user.full_name = f'User {i}'
            user.is_active = True
            user_repo.get_by_id.return_value = user

            service.notify_user(
                user_id=i,
                subject=f'Subject {i}',
                message=f'Message {i}'
            )

        history = service.get_notification_history()

        assert len(history) == 3
        assert history[0]['user_id'] == 1
        assert history[1]['user_id'] == 2
        assert history[2]['user_id'] == 3

    def test_get_notification_history_filtered_by_user(self):
        """Test retrieving history filtered by user ID."""
        user_repo = Mock()
        strategy = Mock()
        strategy.get_strategy_name.return_value = 'email'
        strategy.send.return_value = True

        service = NotificationService(user_repo, strategy)

        # Send notifications to different users
        for i in [1, 2, 1, 3, 1]:
            user = Mock()
            user.id = i
            user.email = f'user{i}@example.com'
            user.full_name = f'User {i}'
            user.is_active = True
            user_repo.get_by_id.return_value = user

            service.notify_user(
                user_id=i,
                subject=f'Subject',
                message=f'Message'
            )

        history = service.get_notification_history(user_id=1)

        assert len(history) == 3
        assert all(n['user_id'] == 1 for n in history)

    def test_get_notification_history_with_limit(self):
        """Test history limit parameter."""
        user_repo = Mock()
        strategy = Mock()
        strategy.get_strategy_name.return_value = 'email'
        strategy.send.return_value = True

        service = NotificationService(user_repo, strategy)

        # Send 10 notifications
        user = Mock()
        user.id = 1
        user.email = 'user@example.com'
        user.full_name = 'User'
        user.is_active = True
        user_repo.get_by_id.return_value = user

        for i in range(10):
            service.notify_user(
                user_id=1,
                subject=f'Subject {i}',
                message=f'Message {i}'
            )

        history = service.get_notification_history(limit=5)

        assert len(history) == 5
        # Should return last 5
        assert history[0]['subject'] == 'Subject 5'
        assert history[4]['subject'] == 'Subject 9'


class TestGetRecipientForStrategy:
    """Test strategy-specific recipient resolution."""

    def test_get_recipient_for_email_strategy(self):
        """Test recipient for email strategy returns email."""
        user_repo = Mock()
        strategy = Mock(spec=EmailNotificationStrategy)
        strategy.get_strategy_name.return_value = 'email'

        service = NotificationService(user_repo, strategy)

        user = Mock()
        user.email = 'test@example.com'
        user.phone = '+1-555-0101'
        user.id = 1

        recipient = service._get_recipient_for_strategy(user)

        assert recipient == 'test@example.com'

    def test_get_recipient_for_sms_strategy(self):
        """Test recipient for SMS strategy returns phone."""
        user_repo = Mock()
        strategy = Mock(spec=SMSNotificationStrategy)
        strategy.get_strategy_name.return_value = 'sms'

        service = NotificationService(user_repo, strategy)

        user = Mock()
        user.email = 'test@example.com'
        user.phone = '+1-555-0101'
        user.id = 1

        recipient = service._get_recipient_for_strategy(user)

        assert recipient == '+1-555-0101'

    def test_get_recipient_for_sms_strategy_no_phone(self):
        """Test recipient for SMS strategy returns None when no phone."""
        user_repo = Mock()
        strategy = Mock(spec=SMSNotificationStrategy)
        strategy.get_strategy_name.return_value = 'sms'

        service = NotificationService(user_repo, strategy)

        user = Mock()
        user.email = 'test@example.com'
        user.phone = None
        user.id = 1

        recipient = service._get_recipient_for_strategy(user)

        assert recipient is None

    def test_get_recipient_for_inapp_strategy(self):
        """Test recipient for in-app strategy returns user ID."""
        user_repo = Mock()
        strategy = Mock(spec=InAppNotificationStrategy)
        strategy.get_strategy_name.return_value = 'in_app'

        service = NotificationService(user_repo, strategy)

        user = Mock()
        user.email = 'test@example.com'
        user.id = 42

        recipient = service._get_recipient_for_strategy(user)

        assert recipient == '42'


class TestStrategyPatternIntegration:
    """Test Strategy Pattern integration and benefits."""

    def test_runtime_strategy_switching(self):
        """Test switching strategies at runtime."""
        user_repo = Mock()
        email_strategy = Mock(spec=EmailNotificationStrategy)
        email_strategy.get_strategy_name.return_value = 'email'
        email_strategy.send.return_value = True

        sms_strategy = Mock(spec=SMSNotificationStrategy)
        sms_strategy.get_strategy_name.return_value = 'sms'
        sms_strategy.send.return_value = True

        service = NotificationService(user_repo, email_strategy)

        # Send with email strategy
        user = Mock()
        user.id = 1
        user.email = 'test@example.com'
        user.phone = '+1-555-0101'
        user.full_name = 'Test User'
        user.is_active = True
        user_repo.get_by_id.return_value = user

        result1 = service.notify_user(1, 'Test', 'Test')
        assert result1['data']['strategy'] == 'email'

        # Switch to SMS strategy at runtime
        service.set_strategy(sms_strategy)

        result2 = service.notify_user(1, 'Test', 'Test')
        assert result2['data']['strategy'] == 'sms'

    def test_strategy_independence(self):
        """Test different strategies are independent."""
        user_repo = Mock()

        # Each strategy should have independent configuration
        email_strategy = Mock()
        email_strategy.get_strategy_name.return_value = 'email'
        email_strategy.send.return_value = True

        sms_strategy = Mock()
        sms_strategy.get_strategy_name.return_value = 'sms'
        sms_strategy.send.return_value = True

        service = NotificationService(user_repo, email_strategy)

        user = Mock()
        user.id = 1
        user.email = 'test@example.com'
        user.phone = '+1-555-0101'
        user.full_name = 'Test User'
        user.is_active = True
        user_repo.get_by_id.return_value = user

        # Use email strategy
        service.notify_user(1, 'Test', 'Test')
        email_strategy.send.assert_called_once()
        sms_strategy.send.assert_not_called()

        # Switch to SMS
        service.set_strategy(sms_strategy)
        service.notify_user(1, 'Test', 'Test')

        # Both strategies called independently
        assert email_strategy.send.call_count == 1
        assert sms_strategy.send.call_count == 1
