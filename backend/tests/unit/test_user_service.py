"""
Unit Tests for UserService

Tests:
- User registration with validation
- Authentication and authorization
- Password management
- Profile updates
- Role-based operations
"""

import pytest
from unittest.mock import Mock, MagicMock
from app.services.user_service import UserService
from app.models import UserRole


class TestRegisterUser:
    """Test user registration functionality."""

    def test_register_user_success(self):
        """Test successful user registration."""
        user_repo = Mock()
        service = UserService(user_repo)

        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = 'newuser@example.com'
        mock_user.full_name = 'John Doe'
        mock_user.to_dict.return_value = {
            'id': 1,
            'email': 'newuser@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'client'
        }

        user_repo.create_user.return_value = mock_user

        result = service.register_user(
            email='newuser@example.com',
            password='SecurePass123',
            first_name='John',
            last_name='Doe',
            role='client'
        )

        assert result['success'] is True
        assert result['data']['email'] == 'newuser@example.com'
        assert 'John Doe' in result['message']
        user_repo.create_user.assert_called_once()

    def test_register_user_with_additional_fields(self):
        """Test registration with optional fields."""
        user_repo = Mock()
        service = UserService(user_repo)

        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = 'tech@example.com'
        mock_user.full_name = 'Jane Tech'
        mock_user.to_dict.return_value = {'id': 1}

        user_repo.create_user.return_value = mock_user

        result = service.register_user(
            email='tech@example.com',
            password='SecurePass123',
            first_name='Jane',
            last_name='Tech',
            role='technician',
            phone='+1-555-0101',
            department='IT'
        )

        assert result['success'] is True
        call_kwargs = user_repo.create_user.call_args[1]
        assert call_kwargs['phone'] == '+1-555-0101'
        assert call_kwargs['department'] == 'IT'

    def test_register_user_validation_errors(self):
        """Test validation of required fields."""
        user_repo = Mock()
        service = UserService(user_repo)

        # Missing email (empty string)
        result = service.register_user(
            email='',
            password='pass',
            first_name='John',
            last_name='Doe',
            role='client'
        )
        assert result['success'] is False
        assert 'email cannot be empty' in result['error']

        # Missing password (empty string)
        result = service.register_user(
            email='test@example.com',
            password='',
            first_name='John',
            last_name='Doe',
            role='client'
        )
        assert result['success'] is False
        assert 'password cannot be empty' in result['error']

        # Missing first name (empty string)
        result = service.register_user(
            email='test@example.com',
            password='pass',
            first_name='',
            last_name='Doe',
            role='client'
        )
        assert result['success'] is False
        assert 'first_name cannot be empty' in result['error']

        # Missing last name (empty string)
        result = service.register_user(
            email='test@example.com',
            password='pass',
            first_name='John',
            last_name='',
            role='client'
        )
        assert result['success'] is False
        assert 'last_name cannot be empty' in result['error']

        # Missing role (empty string)
        result = service.register_user(
            email='test@example.com',
            password='pass',
            first_name='John',
            last_name='Doe',
            role=''
        )
        assert result['success'] is False
        assert 'role cannot be empty' in result['error']

    def test_register_user_invalid_role(self):
        """Test registration fails with invalid role."""
        user_repo = Mock()
        service = UserService(user_repo)

        result = service.register_user(
            email='test@example.com',
            password='SecurePass123',
            first_name='John',
            last_name='Doe',
            role='invalid_role'
        )

        assert result['success'] is False
        assert 'Invalid role' in result['error']

    def test_register_user_duplicate_email(self):
        """Test registration fails when email already exists."""
        user_repo = Mock()
        user_repo.create_user.side_effect = ValueError('Email already exists')

        service = UserService(user_repo)

        result = service.register_user(
            email='existing@example.com',
            password='SecurePass123',
            first_name='John',
            last_name='Doe',
            role='client'
        )

        assert result['success'] is False
        assert 'Email already exists' in result['error']

    def test_register_user_role_enum_conversion(self):
        """Test role string is properly converted to enum."""
        user_repo = Mock()
        service = UserService(user_repo)

        mock_user = Mock()
        mock_user.id = 1
        mock_user.full_name = 'Test User'
        mock_user.to_dict.return_value = {'id': 1}
        user_repo.create_user.return_value = mock_user

        # Test different role formats
        for role in ['admin', 'ADMIN', 'Admin']:
            result = service.register_user(
                email=f'test{role}@example.com',
                password='pass',
                first_name='Test',
                last_name='User',
                role=role
            )
            assert result['success'] is True
            call_kwargs = user_repo.create_user.call_args[1]
            assert call_kwargs['role'] == UserRole.ADMIN


class TestAuthenticate:
    """Test user authentication functionality."""

    def test_authenticate_success(self):
        """Test successful authentication."""
        user_repo = Mock()
        service = UserService(user_repo)

        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = 'user@example.com'
        mock_user.full_name = 'Test User'
        mock_user.to_dict.return_value = {
            'id': 1,
            'email': 'user@example.com',
            'full_name': 'Test User'
        }

        user_repo.authenticate.return_value = mock_user

        result = service.authenticate(
            email='user@example.com',
            password='correctpassword'
        )

        assert result['success'] is True
        assert result['data']['email'] == 'user@example.com'
        assert 'Welcome back, Test User!' in result['message']
        user_repo.authenticate.assert_called_once_with('user@example.com', 'correctpassword')

    def test_authenticate_invalid_credentials(self):
        """Test authentication fails with invalid credentials."""
        user_repo = Mock()
        user_repo.authenticate.return_value = None

        service = UserService(user_repo)

        result = service.authenticate(
            email='user@example.com',
            password='wrongpassword'
        )

        assert result['success'] is False
        assert 'Invalid email or password' in result['error']

    def test_authenticate_validation_errors(self):
        """Test authentication validation of required fields."""
        user_repo = Mock()
        service = UserService(user_repo)

        # Missing email (empty string)
        result = service.authenticate(email='', password='pass')
        assert result['success'] is False
        assert 'email cannot be empty' in result['error']

        # Missing password (empty string)
        result = service.authenticate(email='user@example.com', password='')
        assert result['success'] is False
        assert 'password cannot be empty' in result['error']

    def test_authenticate_inactive_user(self):
        """Test authentication fails for inactive user (handled by repository)."""
        user_repo = Mock()
        user_repo.authenticate.return_value = None  # Repository filters inactive users

        service = UserService(user_repo)

        result = service.authenticate(
            email='inactive@example.com',
            password='password'
        )

        assert result['success'] is False
        assert 'Invalid email or password' in result['error']


class TestChangePassword:
    """Test password change functionality."""

    def test_change_password_success(self):
        """Test successful password change."""
        user_repo = Mock()
        service = UserService(user_repo)

        mock_user = Mock()
        mock_user.id = 1
        mock_user.check_password = Mock(return_value=True)

        user_repo.get_by_id.return_value = mock_user
        user_repo.update_password.return_value = True

        result = service.change_password(
            user_id=1,
            old_password='oldpass',
            new_password='newpass123'
        )

        assert result['success'] is True
        assert 'Password changed successfully' in result['message']
        user_repo.update_password.assert_called_once_with(1, 'newpass123')

    def test_change_password_user_not_found(self):
        """Test password change fails when user doesn't exist."""
        user_repo = Mock()
        user_repo.get_by_id.return_value = None

        service = UserService(user_repo)

        result = service.change_password(
            user_id=999,
            old_password='oldpass',
            new_password='newpass'
        )

        assert result['success'] is False
        assert 'User not found' in result['error']

    def test_change_password_incorrect_old_password(self):
        """Test password change fails with incorrect old password."""
        user_repo = Mock()
        service = UserService(user_repo)

        mock_user = Mock()
        mock_user.id = 1
        mock_user.check_password = Mock(return_value=False)

        user_repo.get_by_id.return_value = mock_user

        result = service.change_password(
            user_id=1,
            old_password='wrongpass',
            new_password='newpass'
        )

        assert result['success'] is False
        assert 'Current password is incorrect' in result['error']

    def test_change_password_same_as_old(self):
        """Test password change fails when new password same as old."""
        user_repo = Mock()
        service = UserService(user_repo)

        mock_user = Mock()
        mock_user.id = 1
        mock_user.check_password = Mock(return_value=True)

        user_repo.get_by_id.return_value = mock_user

        result = service.change_password(
            user_id=1,
            old_password='samepass',
            new_password='samepass'
        )

        assert result['success'] is False
        assert 'New password must be different' in result['error']

    def test_change_password_validation_errors(self):
        """Test validation of required fields."""
        user_repo = Mock()
        service = UserService(user_repo)

        # Missing user_id
        result = service.change_password(
            user_id=None,
            old_password='old',
            new_password='new'
        )
        assert result['success'] is False
        assert 'user_id is required' in result['error']

        # Missing old password (empty string)
        result = service.change_password(
            user_id=1,
            old_password='',
            new_password='new'
        )
        assert result['success'] is False
        assert 'old_password cannot be empty' in result['error']

        # Missing new password (empty string)
        result = service.change_password(
            user_id=1,
            old_password='old',
            new_password=''
        )
        assert result['success'] is False
        assert 'new_password cannot be empty' in result['error']


class TestGetUserProfile:
    """Test user profile retrieval."""

    def test_get_user_profile_success(self):
        """Test successful profile retrieval."""
        user_repo = Mock()
        service = UserService(user_repo)

        mock_user = Mock()
        mock_user.id = 1
        mock_user.to_dict.return_value = {
            'id': 1,
            'email': 'user@example.com',
            'first_name': 'John',
            'last_name': 'Doe'
        }

        user_repo.get_by_id.return_value = mock_user

        result = service.get_user_profile(user_id=1)

        assert result['success'] is True
        assert result['data']['email'] == 'user@example.com'

    def test_get_user_profile_not_found(self):
        """Test profile retrieval fails when user doesn't exist."""
        user_repo = Mock()
        user_repo.get_by_id.return_value = None

        service = UserService(user_repo)

        result = service.get_user_profile(user_id=999)

        assert result['success'] is False
        assert 'User not found' in result['error']


class TestUpdateProfile:
    """Test user profile update functionality."""

    def test_update_profile_success(self):
        """Test successful profile update."""
        user_repo = Mock()
        service = UserService(user_repo)

        mock_user = Mock()
        mock_user.id = 1

        updated_user = Mock()
        updated_user.to_dict.return_value = {
            'id': 1,
            'first_name': 'Jane',
            'last_name': 'Smith',
            'phone': '+1-555-9999'
        }

        user_repo.get_by_id.return_value = mock_user
        user_repo.update.return_value = updated_user

        result = service.update_profile(
            user_id=1,
            first_name='Jane',
            last_name='Smith',
            phone='+1-555-9999'
        )

        assert result['success'] is True
        assert result['data']['first_name'] == 'Jane'
        assert 'Profile updated successfully' in result['message']

    def test_update_profile_filters_allowed_fields(self):
        """Test only allowed fields can be updated."""
        user_repo = Mock()
        service = UserService(user_repo)

        mock_user = Mock()
        mock_user.id = 1

        updated_user = Mock()
        updated_user.to_dict.return_value = {'id': 1}

        user_repo.get_by_id.return_value = mock_user
        user_repo.update.return_value = updated_user

        # Attempt to update allowed and disallowed fields
        result = service.update_profile(
            user_id=1,
            first_name='John',  # Allowed
            email='newemail@example.com',  # Not allowed
            role='admin',  # Not allowed
            password='newpass'  # Not allowed
        )

        assert result['success'] is True

        # Check that only allowed fields were passed to repository
        call_kwargs = user_repo.update.call_args[1]
        assert 'first_name' in call_kwargs
        assert 'email' not in call_kwargs
        assert 'role' not in call_kwargs
        assert 'password' not in call_kwargs

    def test_update_profile_no_valid_fields(self):
        """Test update fails when no valid fields provided."""
        user_repo = Mock()
        service = UserService(user_repo)

        mock_user = Mock()
        mock_user.id = 1
        user_repo.get_by_id.return_value = mock_user

        result = service.update_profile(
            user_id=1,
            email='newemail@example.com',  # Not allowed
            role='admin'  # Not allowed
        )

        assert result['success'] is False
        assert 'No valid fields to update' in result['error']

    def test_update_profile_user_not_found(self):
        """Test update fails when user doesn't exist."""
        user_repo = Mock()
        user_repo.get_by_id.return_value = None

        service = UserService(user_repo)

        result = service.update_profile(
            user_id=999,
            first_name='John'
        )

        assert result['success'] is False
        assert 'User not found' in result['error']


class TestCheckAuthorization:
    """Test authorization checking functionality."""

    def test_check_authorization_authorized(self):
        """Test authorization check when user has permission."""
        user_repo = Mock()
        service = UserService(user_repo)

        mock_user = Mock()
        mock_user.id = 1
        mock_user.role = UserRole.ADMIN
        mock_user.has_permission = Mock(return_value=True)

        user_repo.get_by_id.return_value = mock_user

        result = service.check_authorization(
            user_id=1,
            required_role='admin'
        )

        assert result['success'] is True
        assert result['data']['authorized'] is True
        assert result['data']['user_role'] == 'admin'
        assert result['data']['required_role'] == 'admin'

    def test_check_authorization_not_authorized(self):
        """Test authorization check when user lacks permission."""
        user_repo = Mock()
        service = UserService(user_repo)

        mock_user = Mock()
        mock_user.id = 1
        mock_user.role = UserRole.CLIENT
        mock_user.has_permission = Mock(return_value=False)

        user_repo.get_by_id.return_value = mock_user

        result = service.check_authorization(
            user_id=1,
            required_role='admin'
        )

        assert result['success'] is True
        assert result['data']['authorized'] is False

    def test_check_authorization_user_not_found(self):
        """Test authorization check fails when user doesn't exist."""
        user_repo = Mock()
        user_repo.get_by_id.return_value = None

        service = UserService(user_repo)

        result = service.check_authorization(
            user_id=999,
            required_role='admin'
        )

        assert result['success'] is False
        assert 'User not found' in result['error']

    def test_check_authorization_invalid_role(self):
        """Test authorization check fails with invalid role."""
        user_repo = Mock()
        service = UserService(user_repo)

        mock_user = Mock()
        mock_user.id = 1
        user_repo.get_by_id.return_value = mock_user

        result = service.check_authorization(
            user_id=1,
            required_role='invalid_role'
        )

        assert result['success'] is False
        assert 'Invalid role' in result['error']


class TestGetAvailableTechnicians:
    """Test technician listing functionality."""

    def test_get_available_technicians_success(self):
        """Test successful retrieval of available technicians."""
        user_repo = Mock()
        service = UserService(user_repo)

        tech1 = Mock()
        tech1.to_dict.return_value = {
            'id': 1,
            'full_name': 'Tech One',
            'role': 'technician'
        }

        tech2 = Mock()
        tech2.to_dict.return_value = {
            'id': 2,
            'full_name': 'Tech Two',
            'role': 'technician'
        }

        user_repo.get_active_technicians.return_value = [tech1, tech2]

        result = service.get_available_technicians()

        assert result['success'] is True
        assert len(result['data']) == 2
        assert 'Found 2 available technicians' in result['message']

    def test_get_available_technicians_empty(self):
        """Test when no technicians available."""
        user_repo = Mock()
        user_repo.get_active_technicians.return_value = []

        service = UserService(user_repo)

        result = service.get_available_technicians()

        assert result['success'] is True
        assert len(result['data']) == 0
        assert 'Found 0 available technicians' in result['message']


class TestBusinessLogic:
    """Test service-level business logic."""

    def test_authentication_returns_user_data_not_password(self):
        """Test authentication doesn't expose password in response."""
        user_repo = Mock()
        service = UserService(user_repo)

        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = 'user@example.com'
        mock_user.full_name = 'Test User'
        mock_user.to_dict.return_value = {
            'id': 1,
            'email': 'user@example.com',
            'full_name': 'Test User'
            # Note: password_hash should not be included
        }

        user_repo.authenticate.return_value = mock_user

        result = service.authenticate('user@example.com', 'password')

        assert result['success'] is True
        assert 'password' not in result['data']
        assert 'password_hash' not in result['data']

    def test_profile_update_allowed_fields_only(self):
        """Test business rule: only specific fields can be updated via profile update."""
        user_repo = Mock()
        service = UserService(user_repo)

        mock_user = Mock()
        mock_user.id = 1

        updated_user = Mock()
        updated_user.to_dict.return_value = {'id': 1}

        user_repo.get_by_id.return_value = mock_user
        user_repo.update.return_value = updated_user

        # Allowed fields
        allowed_fields = ['first_name', 'last_name', 'phone', 'department']

        for field in allowed_fields:
            service.update_profile(user_id=1, **{field: 'test_value'})
            call_kwargs = user_repo.update.call_args[1]
            assert field in call_kwargs

    def test_role_enum_conversion_case_insensitive(self):
        """Test role conversion handles different cases."""
        user_repo = Mock()
        service = UserService(user_repo)

        mock_user = Mock()
        mock_user.full_name = 'Test'
        mock_user.to_dict.return_value = {'id': 1}
        user_repo.create_user.return_value = mock_user

        # Test various cases
        for role_input in ['admin', 'ADMIN', 'Admin', 'aDmIn']:
            result = service.register_user(
                email=f'test{role_input}@example.com',
                password='pass',
                first_name='Test',
                last_name='User',
                role=role_input
            )
            assert result['success'] is True
            # Verify role was converted to enum
            call_kwargs = user_repo.create_user.call_args[1]
            assert isinstance(call_kwargs['role'], UserRole)
            assert call_kwargs['role'] == UserRole.ADMIN
