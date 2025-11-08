"""
User Service with Authentication and Authorization Logic

Demonstrates:
- Service Layer: User management business logic
- Authentication: Login, password management
- Authorization: Role-based access control
"""

from typing import Optional, Dict
from app.services.base_service import BaseService
from app.repositories import UserRepository
from app.models import User, UserRole


class UserService(BaseService):
    """
    Service for user management and authentication.

    Business Logic:
    - User registration with validation
    - Authentication (login)
    - Authorization (role checking)
    - Password management
    - User profile management

    OOP Principles:
    - Single Responsibility: Handles only user-related business logic
    - Dependency Injection: Repository injected
    """

    def __init__(self, user_repository: UserRepository):
        """
        Initialize user service.

        Args:
            user_repository: Repository for user data access
        """
        super().__init__()
        self.user_repo = user_repository

    def register_user(self, email: str, password: str, first_name: str,
                     last_name: str, role: str, **kwargs) -> dict:
        """
        Register a new user.

        Args:
            email: User email
            password: Plain text password
            first_name: First name
            last_name: Last name
            role: User role (admin, technician, client)
            **kwargs: Additional fields (phone, department)

        Returns:
            dict: Success/error response with user data

        Business Rules:
        - Email must be unique
        - Password must meet requirements
        - Role must be valid
        """
        try:
            # Validate inputs
            self._validate_required(email, 'email')
            self._validate_required(password, 'password')
            self._validate_required(first_name, 'first_name')
            self._validate_required(last_name, 'last_name')
            self._validate_required(role, 'role')

            # Convert role string to enum
            try:
                role_enum = UserRole(role.lower())
            except ValueError:
                return self._build_error_response(f"Invalid role: {role}")

            # Register user through repository
            user = self.user_repo.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role_enum,
                **kwargs
            )

            self._log_action(f"User registered: {user.email}", {'user_id': user.id, 'role': role})

            return self._build_success_response(
                data=user.to_dict(),
                message=f"User {user.full_name} registered successfully"
            )

        except ValueError as e:
            return self._build_error_response(str(e))
        except Exception as e:
            return self._handle_exception(e, "register_user")

    def authenticate(self, email: str, password: str) -> dict:
        """
        Authenticate user with email and password.

        Args:
            email: User email
            password: Plain text password

        Returns:
            dict: Success with user data or error

        Business Logic:
        - Verifies credentials
        - Checks if user is active
        - Returns user data on success
        """
        try:
            self._validate_required(email, 'email')
            self._validate_required(password, 'password')

            # Authenticate through repository
            user = self.user_repo.authenticate(email, password)

            if user:
                self._log_action(f"User authenticated: {user.email}", {'user_id': user.id})

                return self._build_success_response(
                    data=user.to_dict(),
                    message=f"Welcome back, {user.full_name}!"
                )
            else:
                self._log_action(f"Authentication failed for: {email}")
                return self._build_error_response("Invalid email or password")

        except Exception as e:
            return self._handle_exception(e, "authenticate")

    def change_password(self, user_id: int, old_password: str, new_password: str) -> dict:
        """
        Change user password.

        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            dict: Success/error response

        Business Rules:
        - Old password must be correct
        - New password must meet requirements
        - Cannot reuse old password
        """
        try:
            self._validate_required(user_id, 'user_id')
            self._validate_required(old_password, 'old_password')
            self._validate_required(new_password, 'new_password')

            # Get user
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return self._build_error_response("User not found")

            # Verify old password
            if not user.check_password(old_password):
                return self._build_error_response("Current password is incorrect")

            # Check new password is different
            if old_password == new_password:
                return self._build_error_response("New password must be different from current password")

            # Update password
            success = self.user_repo.update_password(user_id, new_password)

            if success:
                self._log_action(f"Password changed for user {user_id}")
                return self._build_success_response(
                    data={'user_id': user_id},
                    message="Password changed successfully"
                )
            else:
                return self._build_error_response("Failed to update password")

        except ValueError as e:
            return self._build_error_response(str(e))
        except Exception as e:
            return self._handle_exception(e, "change_password")

    def get_user_profile(self, user_id: int) -> dict:
        """
        Get user profile.

        Args:
            user_id: User ID

        Returns:
            dict: User profile data
        """
        try:
            user = self.user_repo.get_by_id(user_id)

            if not user:
                return self._build_error_response("User not found")

            return self._build_success_response(data=user.to_dict())

        except Exception as e:
            return self._handle_exception(e, "get_user_profile")

    def update_profile(self, user_id: int, **updates) -> dict:
        """
        Update user profile.

        Args:
            user_id: User ID
            **updates: Fields to update (first_name, last_name, phone, department)

        Returns:
            dict: Success/error response

        Business Rules:
        - Cannot update email or role through this method
        - Only specific fields allowed
        """
        try:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return self._build_error_response("User not found")

            # Filter allowed updates
            allowed_fields = ['first_name', 'last_name', 'phone', 'department']
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}

            if not filtered_updates:
                return self._build_error_response("No valid fields to update")

            # Update user
            updated_user = self.user_repo.update(user, **filtered_updates)

            self._log_action(f"Profile updated for user {user_id}", filtered_updates)

            return self._build_success_response(
                data=updated_user.to_dict(),
                message="Profile updated successfully"
            )

        except Exception as e:
            return self._handle_exception(e, "update_profile")

    def check_authorization(self, user_id: int, required_role: str) -> dict:
        """
        Check if user has required authorization.

        Args:
            user_id: User ID
            required_role: Required role (admin, technician, client)

        Returns:
            dict: Authorization result

        Business Logic: Role hierarchy check
        """
        try:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return self._build_error_response("User not found")

            try:
                required_role_enum = UserRole(required_role.lower())
            except ValueError:
                return self._build_error_response(f"Invalid role: {required_role}")

            authorized = user.has_permission(required_role_enum)

            return self._build_success_response(
                data={
                    'authorized': authorized,
                    'user_role': user.role.value,
                    'required_role': required_role
                }
            )

        except Exception as e:
            return self._handle_exception(e, "check_authorization")

    def get_available_technicians(self) -> dict:
        """
        Get list of active technicians.

        Returns:
            dict: List of technician users

        Use Case: For assigning maintenance requests
        """
        try:
            technicians = self.user_repo.get_active_technicians()

            return self._build_success_response(
                data=[tech.to_dict() for tech in technicians],
                message=f"Found {len(technicians)} available technicians"
            )

        except Exception as e:
            return self._handle_exception(e, "get_available_technicians")
