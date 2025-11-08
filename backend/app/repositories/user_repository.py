"""
User Repository with user-specific data access methods.

Extends BaseRepository with authentication and role-specific queries.
"""

from typing import List, Optional
from app.repositories.base_repository import BaseRepository
from app.models.user import User, UserRole


class UserRepository(BaseRepository[User]):
    """
    Repository for User model.

    OOP Principles:
    - Inheritance: Extends BaseRepository functionality
    - Single Responsibility: Handles only user data access
    - Open/Closed: Extends base without modifying it
    """

    def __init__(self):
        """Initialize with User model class"""
        super().__init__(User)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: User's email address

        Returns:
            User instance or None if not found
        """
        return self.get_one_by_filter(email=email.lower())

    def get_by_role(self, role: UserRole) -> List[User]:
        """
        Get all users with specific role.

        Args:
            role: UserRole enum value

        Returns:
            List of users with the specified role
        """
        return self.get_by_filter(role=role)

    def get_active_users(self) -> List[User]:
        """
        Get all active users.

        Returns:
            List of active users
        """
        return self.get_by_filter(is_active=True)

    def get_active_technicians(self) -> List[User]:
        """
        Get all active technicians.

        Returns:
            List of active technician users

        Use case: For assigning maintenance requests
        """
        return [user for user in self.get_by_role(UserRole.TECHNICIAN) if user.is_active]

    def get_admins(self) -> List[User]:
        """
        Get all admin users.

        Returns:
            List of admin users
        """
        return self.get_by_role(UserRole.ADMIN)

    def email_exists(self, email: str) -> bool:
        """
        Check if email is already registered.

        Args:
            email: Email address to check

        Returns:
            True if email exists, False otherwise
        """
        return self.get_by_email(email) is not None

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.

        Args:
            email: User's email address
            password: Plain text password

        Returns:
            User instance if authentication successful, None otherwise

        Note: This is used by authentication service
        """
        user = self.get_by_email(email)

        if user and user.is_active and user.check_password(password):
            return user

        return None

    def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate user (soft delete).

        Args:
            user_id: User ID to deactivate

        Returns:
            True if successful, False if user not found
        """
        user = self.get_by_id(user_id)

        if user:
            user.is_active = False
            self.update(user)
            return True

        return False

    def reactivate_user(self, user_id: int) -> bool:
        """
        Reactivate deactivated user.

        Args:
            user_id: User ID to reactivate

        Returns:
            True if successful, False if user not found
        """
        user = self.get_by_id(user_id)

        if user:
            user.is_active = True
            self.update(user)
            return True

        return False

    def create_user(self, email: str, password: str, first_name: str,
                    last_name: str, role: UserRole, **kwargs) -> User:
        """
        Create new user with password hashing.

        Args:
            email: User's email
            password: Plain text password (will be hashed)
            first_name: User's first name
            last_name: User's last name
            role: UserRole enum value
            **kwargs: Additional user fields (phone, department, etc.)

        Returns:
            Created user instance

        Raises:
            ValueError: If email already exists or validation fails
        """
        # Check if email already exists
        if self.email_exists(email):
            raise ValueError(f"Email {email} is already registered")

        # Create user instance without committing
        user = User(
            email=email.lower(),
            first_name=first_name,
            last_name=last_name,
            role=role,
            **kwargs
        )

        # Set password (will be hashed)
        user.set_password(password)

        # Validate
        user.validate()

        # Save to database using base repository create logic
        from app.database import db
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

        return user

    def update_password(self, user_id: int, new_password: str) -> bool:
        """
        Update user's password.

        Args:
            user_id: User ID
            new_password: New plain text password (will be hashed)

        Returns:
            True if successful, False if user not found

        Raises:
            ValueError: If password validation fails
        """
        user = self.get_by_id(user_id)

        if user:
            user.set_password(new_password)
            self.update(user)
            return True

        return False

    def get_technician_workload(self, technician_id: int) -> int:
        """
        Get count of open requests assigned to technician.

        Args:
            technician_id: Technician user ID

        Returns:
            Number of open requests assigned to this technician

        Note: Requires RequestRepository for full implementation.
        This is a placeholder that will be enhanced in Phase 2.
        """
        # This will be fully implemented when we have service layer
        # For now, return 0 as placeholder
        return 0
