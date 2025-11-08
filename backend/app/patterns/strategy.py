"""
Strategy Pattern Implementation for Notifications

Purpose: Define a family of algorithms (notification methods), encapsulate each one,
and make them interchangeable. Strategy lets the algorithm vary independently
from clients that use it.

Benefits:
- Open/Closed Principle: Add new notification types without modifying existing code
- Runtime flexibility: Switch notification methods dynamically
- Testability: Easy to mock different strategies
- Single Responsibility: Each strategy focuses on one notification method

OOP Principles:
- Polymorphism: All strategies share common interface
- Encapsulation: Implementation details hidden within each strategy
- Abstraction: Client code depends on abstraction, not concrete implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class NotificationStrategy(ABC):
    """
    Abstract base class for notification strategies.

    All concrete notification strategies must implement the send method.

    Design Pattern: Strategy Pattern
    OOP Principle: Abstraction - defines contract without implementation
    """

    @abstractmethod
    def send(self, recipient: str, subject: str, message: str, **kwargs) -> bool:
        """
        Send notification to recipient.

        Args:
            recipient: Recipient identifier (email, phone, user_id)
            subject: Notification subject/title
            message: Notification message body
            **kwargs: Additional strategy-specific parameters

        Returns:
            bool: True if notification sent successfully, False otherwise

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """
        Get the name of this notification strategy.

        Returns:
            str: Strategy name (e.g., 'email', 'sms', 'in_app')
        """
        pass

    def validate_recipient(self, recipient: str) -> bool:
        """
        Validate recipient identifier format.

        Override in subclasses for specific validation.

        Args:
            recipient: Recipient identifier

        Returns:
            bool: True if valid, False otherwise
        """
        return bool(recipient and recipient.strip())


class EmailNotificationStrategy(NotificationStrategy):
    """
    Email notification strategy implementation.

    Sends notifications via email using SMTP.

    OOP Principle: Encapsulation - Email sending logic is internal
    """

    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
        """
        Initialize email notification strategy.

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send(self, recipient: str, subject: str, message: str, **kwargs) -> bool:
        """
        Send email notification.

        Args:
            recipient: Email address
            subject: Email subject
            message: Email body
            **kwargs: Additional parameters (cc, bcc, attachments, etc.)

        Returns:
            bool: True if sent successfully

        Note: This is a mock implementation. In production, use smtplib or
        a service like SendGrid, AWS SES, etc.
        """
        # Validate email format
        if not self._validate_email(recipient):
            print(f"[EmailStrategy] Invalid email address: {recipient}")
            return False

        # Mock email sending (in production, use actual SMTP)
        print(f"[EmailStrategy] Sending email to: {recipient}")
        print(f"  Subject: {subject}")
        print(f"  Message: {message[:100]}...")
        print(f"  SMTP: {self.smtp_host}:{self.smtp_port}")

        # In production:
        # import smtplib
        # from email.mime.text import MIMEText
        # try:
        #     msg = MIMEText(message)
        #     msg['Subject'] = subject
        #     msg['From'] = self.username
        #     msg['To'] = recipient
        #
        #     with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
        #         server.starttls()
        #         server.login(self.username, self.password)
        #         server.send_message(msg)
        #     return True
        # except Exception as e:
        #     print(f"Email failed: {e}")
        #     return False

        return True

    def get_strategy_name(self) -> str:
        """Get strategy name"""
        return "email"

    def _validate_email(self, email: str) -> bool:
        """
        Validate email format.

        Args:
            email: Email address to validate

        Returns:
            bool: True if valid email format
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


class SMSNotificationStrategy(NotificationStrategy):
    """
    SMS notification strategy implementation.

    Sends notifications via SMS using a gateway service.

    OOP Principle: Encapsulation - SMS sending logic is internal
    """

    def __init__(self, api_key: str, api_url: str, sender_number: str):
        """
        Initialize SMS notification strategy.

        Args:
            api_key: SMS gateway API key
            api_url: SMS gateway API URL
            sender_number: Sender phone number
        """
        self.api_key = api_key
        self.api_url = api_url
        self.sender_number = sender_number

    def send(self, recipient: str, subject: str, message: str, **kwargs) -> bool:
        """
        Send SMS notification.

        Args:
            recipient: Phone number
            subject: SMS subject (may be included in message)
            message: SMS body (160 chars recommended)
            **kwargs: Additional parameters

        Returns:
            bool: True if sent successfully

        Note: This is a mock implementation. In production, use Twilio,
        AWS SNS, or other SMS gateway.
        """
        # Validate phone format
        if not self._validate_phone(recipient):
            print(f"[SMSStrategy] Invalid phone number: {recipient}")
            return False

        # Truncate message if too long
        max_length = kwargs.get('max_length', 160)
        truncated_message = message[:max_length]

        # Mock SMS sending
        print(f"[SMSStrategy] Sending SMS to: {recipient}")
        print(f"  From: {self.sender_number}")
        print(f"  Message: {truncated_message}")
        print(f"  API: {self.api_url}")

        # In production:
        # import requests
        # try:
        #     response = requests.post(
        #         self.api_url,
        #         headers={'Authorization': f'Bearer {self.api_key}'},
        #         json={
        #             'to': recipient,
        #             'from': self.sender_number,
        #             'body': truncated_message
        #         }
        #     )
        #     return response.status_code == 200
        # except Exception as e:
        #     print(f"SMS failed: {e}")
        #     return False

        return True

    def get_strategy_name(self) -> str:
        """Get strategy name"""
        return "sms"

    def _validate_phone(self, phone: str) -> bool:
        """
        Validate phone number format.

        Args:
            phone: Phone number to validate

        Returns:
            bool: True if valid phone format
        """
        import re
        # Simple validation: digits, spaces, dashes, parentheses
        pattern = r'^[\d\s\-\(\)\+]+$'
        cleaned = phone.strip()
        return bool(re.match(pattern, cleaned) and len(cleaned) >= 10)


class InAppNotificationStrategy(NotificationStrategy):
    """
    In-app notification strategy implementation.

    Stores notifications in database for display within the application.

    OOP Principle: Encapsulation - Database storage logic is internal
    """

    def __init__(self, db_session):
        """
        Initialize in-app notification strategy.

        Args:
            db_session: Database session for storing notifications
        """
        self.db_session = db_session

    def send(self, recipient: str, subject: str, message: str, **kwargs) -> bool:
        """
        Create in-app notification.

        Args:
            recipient: User ID (string)
            subject: Notification title
            message: Notification body
            **kwargs: Additional parameters (priority, link, icon, etc.)

        Returns:
            bool: True if stored successfully

        Note: Stores notification in database for retrieval by user.
        """
        try:
            user_id = int(recipient)
        except ValueError:
            print(f"[InAppStrategy] Invalid user ID: {recipient}")
            return False

        # Mock in-app notification (in production, store in Notification table)
        print(f"[InAppStrategy] Creating in-app notification for user {user_id}")
        print(f"  Subject: {subject}")
        print(f"  Message: {message[:100]}...")
        print(f"  Priority: {kwargs.get('priority', 'normal')}")

        # In production:
        # from app.models import Notification
        # try:
        #     notification = Notification(
        #         user_id=user_id,
        #         subject=subject,
        #         message=message,
        #         priority=kwargs.get('priority', 'normal'),
        #         link=kwargs.get('link'),
        #         icon=kwargs.get('icon'),
        #         is_read=False,
        #         created_at=datetime.utcnow()
        #     )
        #     self.db_session.add(notification)
        #     self.db_session.commit()
        #     return True
        # except Exception as e:
        #     self.db_session.rollback()
        #     print(f"In-app notification failed: {e}")
        #     return False

        return True

    def get_strategy_name(self) -> str:
        """Get strategy name"""
        return "in_app"


class NotificationContext:
    """
    Context class for Strategy pattern.

    Maintains reference to a Strategy object and delegates notification
    sending to the strategy.

    Benefits:
    - Clients work with this context instead of concrete strategies
    - Strategy can be changed at runtime
    - New strategies can be added without changing client code

    OOP Principle: Composition over inheritance - has-a strategy, not is-a strategy
    """

    def __init__(self, strategy: Optional[NotificationStrategy] = None):
        """
        Initialize context with a strategy.

        Args:
            strategy: Initial notification strategy (can be changed later)
        """
        self._strategy = strategy

    @property
    def strategy(self) -> Optional[NotificationStrategy]:
        """Get current strategy"""
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: NotificationStrategy) -> None:
        """
        Set notification strategy.

        Args:
            strategy: New notification strategy to use

        Demonstrates: Runtime strategy switching (Strategy Pattern benefit)
        """
        self._strategy = strategy

    def send_notification(self, recipient: str, subject: str, message: str, **kwargs) -> bool:
        """
        Send notification using current strategy.

        Args:
            recipient: Recipient identifier
            subject: Notification subject
            message: Notification message
            **kwargs: Strategy-specific parameters

        Returns:
            bool: True if sent successfully

        Raises:
            ValueError: If no strategy is set

        Demonstrates: Delegation to strategy (Strategy Pattern core concept)
        """
        if self._strategy is None:
            raise ValueError("No notification strategy set")

        return self._strategy.send(recipient, subject, message, **kwargs)

    def get_current_strategy_name(self) -> str:
        """
        Get name of current strategy.

        Returns:
            str: Strategy name or 'none' if no strategy set
        """
        if self._strategy is None:
            return "none"
        return self._strategy.get_strategy_name()
