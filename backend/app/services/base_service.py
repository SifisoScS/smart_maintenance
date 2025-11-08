"""
Base Service Layer Pattern Implementation

Purpose: Encapsulate business logic separate from data access (repositories)
and presentation (controllers).

Benefits:
- Separation of Concerns: Business logic in one place
- Testability: Easy to test with mocked repositories
- Reusability: Business logic can be used from multiple controllers
- Transaction Management: Handle complex multi-repository operations

OOP Principles:
- Single Responsibility: Service handles only business logic for its domain
- Dependency Inversion: Depends on repository abstractions
- Open/Closed: Can be extended without modification
"""

from typing import Optional, List, Any
from abc import ABC


class BaseService(ABC):
    """
    Abstract base service with common functionality.

    All domain services inherit from this class.

    OOP Principles:
    - Abstraction: Provides common service behavior
    - Inheritance: Subclasses extend with domain-specific logic
    - Encapsulation: Common service operations in one place

    Design Pattern: Service Layer Pattern
    """

    def __init__(self):
        """
        Initialize base service.

        Subclasses should inject their required repositories in __init__.
        """
        pass

    def _validate_required(self, value: Any, field_name: str) -> None:
        """
        Validate that a required field has a value.

        Args:
            value: Value to check
            field_name: Name of field for error message

        Raises:
            ValueError: If value is None or empty

        Usage:
            self._validate_required(user_id, 'user_id')
        """
        if value is None:
            raise ValueError(f"{field_name} is required")

        if isinstance(value, str) and not value.strip():
            raise ValueError(f"{field_name} cannot be empty")

    def _validate_positive(self, value: int, field_name: str) -> None:
        """
        Validate that a numeric value is positive.

        Args:
            value: Numeric value to check
            field_name: Name of field for error message

        Raises:
            ValueError: If value is not positive
        """
        if value is None or value <= 0:
            raise ValueError(f"{field_name} must be a positive number")

    def _validate_in_list(self, value: Any, valid_values: List[Any], field_name: str) -> None:
        """
        Validate that value is in list of valid values.

        Args:
            value: Value to check
            valid_values: List of valid values
            field_name: Name of field for error message

        Raises:
            ValueError: If value not in valid_values
        """
        if value not in valid_values:
            raise ValueError(f"{field_name} must be one of: {', '.join(str(v) for v in valid_values)}")

    def _build_error_response(self, message: str, details: Optional[dict] = None) -> dict:
        """
        Build standardized error response.

        Args:
            message: Error message
            details: Additional error details (optional)

        Returns:
            dict: Standardized error response
        """
        response = {
            'success': False,
            'error': message
        }

        if details:
            response['details'] = details

        return response

    def _build_success_response(self, data: Any, message: Optional[str] = None) -> dict:
        """
        Build standardized success response.

        Args:
            data: Response data
            message: Success message (optional)

        Returns:
            dict: Standardized success response
        """
        response = {
            'success': True,
            'data': data
        }

        if message:
            response['message'] = message

        return response

    def _log_action(self, action: str, details: Optional[dict] = None) -> None:
        """
        Log service action.

        Args:
            action: Action description
            details: Additional details (optional)

        Note: In production, use proper logging framework
        """
        log_message = f"[{self.__class__.__name__}] {action}"

        if details:
            log_message += f" | Details: {details}"

        print(log_message)

    def _handle_exception(self, exception: Exception, context: str) -> dict:
        """
        Handle exception and return error response.

        Args:
            exception: Exception that occurred
            context: Context where exception occurred

        Returns:
            dict: Error response with exception details
        """
        error_message = f"Error in {context}: {str(exception)}"
        self._log_action(f"Exception: {error_message}")

        return self._build_error_response(
            message=error_message,
            details={
                'exception_type': exception.__class__.__name__,
                'context': context
            }
        )
