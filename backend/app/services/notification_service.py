"""
Notification Service using Strategy Pattern

Demonstrates:
- Service Layer Pattern: Business logic for notifications
- Strategy Pattern: Pluggable notification methods
- Dependency Injection: Strategy injected at runtime
"""

from typing import Optional, List, Dict
from app.services.base_service import BaseService
from app.patterns.strategy import NotificationStrategy, NotificationContext
from app.repositories import UserRepository
from app.models import User


class NotificationService(BaseService):
    """
    Service for managing notifications.

    Demonstrates:
    - Service Layer: Encapsulates notification business logic
    - Strategy Pattern: Uses pluggable notification strategies
    - Dependency Injection: Repositories and strategies injected

    OOP Principles:
    - Single Responsibility: Manages only notification logic
    - Dependency Inversion: Depends on abstractions (NotificationStrategy)
    - Open/Closed: New strategies can be added without modification
    """

    def __init__(self, user_repository: UserRepository, default_strategy: Optional[NotificationStrategy] = None):
        """
        Initialize notification service.

        Args:
            user_repository: Repository for user data access
            default_strategy: Default notification strategy (optional)

        Demonstrates: Dependency Injection
        """
        super().__init__()
        self.user_repo = user_repository
        self.context = NotificationContext(default_strategy)
        self._notification_history: List[Dict] = []  # For tracking sent notifications

    def set_strategy(self, strategy: NotificationStrategy) -> None:
        """
        Set notification strategy at runtime.

        Args:
            strategy: Notification strategy to use

        Demonstrates: Strategy Pattern - runtime strategy switching
        """
        self.context.strategy = strategy
        self._log_action(f"Notification strategy changed to: {strategy.get_strategy_name()}")

    def notify_user(self, user_id: int, subject: str, message: str, **kwargs) -> dict:
        """
        Send notification to a user.

        Args:
            user_id: User ID to notify
            subject: Notification subject
            message: Notification message
            **kwargs: Strategy-specific parameters

        Returns:
            dict: Success/error response

        Business Logic:
        - Validates user exists and is active
        - Determines notification recipient based on strategy
        - Sends notification via current strategy
        - Records notification in history
        """
        try:
            # Validate inputs
            self._validate_required(user_id, 'user_id')
            self._validate_required(subject, 'subject')
            self._validate_required(message, 'message')

            # Check strategy is set
            if self.context.strategy is None:
                return self._build_error_response("No notification strategy configured")

            # Get user
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return self._build_error_response(f"User {user_id} not found")

            # Check user is active
            if not user.is_active:
                return self._build_error_response(f"User {user_id} is not active")

            # Determine recipient based on strategy
            recipient = self._get_recipient_for_strategy(user)
            if not recipient:
                return self._build_error_response(
                    f"No {self.context.get_current_strategy_name()} configured for user {user_id}"
                )

            # Send notification
            success = self.context.send_notification(recipient, subject, message, **kwargs)

            if success:
                # Record in history
                self._record_notification(user_id, subject, message, self.context.get_current_strategy_name())

                self._log_action(
                    "Notification sent",
                    {'user_id': user_id, 'strategy': self.context.get_current_strategy_name()}
                )

                return self._build_success_response(
                    data={'sent': True, 'strategy': self.context.get_current_strategy_name()},
                    message=f"Notification sent to {user.full_name}"
                )
            else:
                return self._build_error_response("Failed to send notification")

        except Exception as e:
            return self._handle_exception(e, "notify_user")

    def notify_multiple_users(self, user_ids: List[int], subject: str, message: str, **kwargs) -> dict:
        """
        Send notification to multiple users.

        Args:
            user_ids: List of user IDs
            subject: Notification subject
            message: Notification message
            **kwargs: Strategy-specific parameters

        Returns:
            dict: Response with success/failure counts
        """
        try:
            self._validate_required(user_ids, 'user_ids')

            if not isinstance(user_ids, list):
                return self._build_error_response("user_ids must be a list")

            results = {
                'total': len(user_ids),
                'successful': 0,
                'failed': 0,
                'errors': []
            }

            for user_id in user_ids:
                response = self.notify_user(user_id, subject, message, **kwargs)
                if response['success']:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'user_id': user_id,
                        'error': response.get('error', 'Unknown error')
                    })

            return self._build_success_response(
                data=results,
                message=f"Sent {results['successful']}/{results['total']} notifications"
            )

        except Exception as e:
            return self._handle_exception(e, "notify_multiple_users")

    def notify_by_role(self, role: str, subject: str, message: str, **kwargs) -> dict:
        """
        Send notification to all users with a specific role.

        Args:
            role: User role (admin, technician, client)
            subject: Notification subject
            message: Notification message
            **kwargs: Strategy-specific parameters

        Returns:
            dict: Response with notification results

        Business Logic: Bulk notification to role-based users
        """
        try:
            from app.models import UserRole

            # Convert string to enum
            try:
                role_enum = UserRole(role.lower())
            except ValueError:
                return self._build_error_response(f"Invalid role: {role}")

            # Get users with role
            users = self.user_repo.get_by_role(role_enum)
            active_users = [u for u in users if u.is_active]

            if not active_users:
                return self._build_success_response(
                    data={'total': 0, 'successful': 0, 'failed': 0},
                    message=f"No active {role} users found"
                )

            # Notify all users
            user_ids = [u.id for u in active_users]
            return self.notify_multiple_users(user_ids, subject, message, **kwargs)

        except Exception as e:
            return self._handle_exception(e, "notify_by_role")

    def get_notification_history(self, user_id: Optional[int] = None, limit: int = 50) -> List[Dict]:
        """
        Get notification history.

        Args:
            user_id: Filter by user ID (optional)
            limit: Maximum number of notifications to return

        Returns:
            List of notification records
        """
        history = self._notification_history

        if user_id is not None:
            history = [n for n in history if n['user_id'] == user_id]

        return history[-limit:]

    def _get_recipient_for_strategy(self, user: User) -> Optional[str]:
        """
        Get recipient identifier based on current strategy.

        Args:
            user: User object

        Returns:
            str: Recipient identifier (email, phone, or user_id)
        """
        strategy_name = self.context.get_current_strategy_name()

        if strategy_name == 'email':
            return user.email
        elif strategy_name == 'sms':
            return user.phone if user.phone else None
        elif strategy_name == 'in_app':
            return str(user.id)
        else:
            return None

    def _record_notification(self, user_id: int, subject: str, message: str, strategy: str) -> None:
        """
        Record notification in history.

        Args:
            user_id: User ID
            subject: Notification subject
            message: Notification message
            strategy: Strategy used

        Note: In production, store in database
        """
        from datetime import datetime

        self._notification_history.append({
            'user_id': user_id,
            'subject': subject,
            'message': message,
            'strategy': strategy,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'sent'
        })
