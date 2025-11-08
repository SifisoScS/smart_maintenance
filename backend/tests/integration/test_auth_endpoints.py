"""
Integration tests for authentication endpoints.

Tests:
- User registration
- User login
- Token refresh
- User logout
- Get current user
"""

import pytest
from flask import json


@pytest.mark.integration
class TestUserRegistration:
    """Test user registration endpoint."""

    def test_register_user_success(self, client, db_session):
        """Test successful user registration."""
        response = client.post('/api/v1/auth/register', json={
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'client'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert 'message' in data
        assert data['data']['email'] == 'newuser@example.com'
        assert data['data']['first_name'] == 'New'
        assert data['data']['last_name'] == 'User'
        assert data['data']['role'] == 'client'
        assert 'password' not in data['data']  # Password should not be returned

    def test_register_duplicate_email(self, client, db_session, sample_user):
        """Test registration fails with duplicate email."""
        response = client.post('/api/v1/auth/register', json={
            'email': sample_user.email,  # Existing email
            'password': 'SecurePass123!',
            'first_name': 'Another',
            'last_name': 'User',
            'role': 'client'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_register_invalid_email_format(self, client, db_session):
        """Test registration fails with invalid email format."""
        response = client.post('/api/v1/auth/register', json={
            'email': 'invalid-email',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'client'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'

    def test_register_weak_password(self, client, db_session):
        """Test registration fails with weak password."""
        response = client.post('/api/v1/auth/register', json={
            'email': 'test@example.com',
            'password': 'weak',  # Too short
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'client'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'

    def test_register_missing_required_fields(self, client, db_session):
        """Test registration fails with missing required fields."""
        response = client.post('/api/v1/auth/register', json={
            'email': 'test@example.com',
            'password': 'SecurePass123!'
            # Missing first_name, last_name, role
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'

    def test_register_invalid_role(self, client, db_session):
        """Test registration fails with invalid role."""
        response = client.post('/api/v1/auth/register', json={
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'superadmin'  # Invalid role
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'


@pytest.mark.integration
class TestUserLogin:
    """Test user login endpoint."""

    def test_login_success(self, client, db_session, sample_user):
        """Test successful login."""
        response = client.post('/api/v1/auth/login', json={
            'email': sample_user.email,
            'password': 'password123'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['id'] == sample_user.id
        assert data['user']['email'] == sample_user.email

    def test_login_invalid_credentials(self, client, db_session, sample_user):
        """Test login fails with invalid credentials."""
        response = client.post('/api/v1/auth/login', json={
            'email': sample_user.email,
            'password': 'wrongpassword'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

    def test_login_nonexistent_user(self, client, db_session):
        """Test login fails with nonexistent user."""
        response = client.post('/api/v1/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

    def test_login_inactive_user(self, client, db_session, sample_user):
        """Test login fails with inactive user."""
        # Deactivate user
        sample_user.is_active = False
        db_session.session.commit()

        response = client.post('/api/v1/auth/login', json={
            'email': sample_user.email,
            'password': 'password123'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

    def test_login_missing_email(self, client, db_session):
        """Test login fails with missing email."""
        response = client.post('/api/v1/auth/login', json={
            'password': 'password123'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_login_missing_password(self, client, db_session):
        """Test login fails with missing password."""
        response = client.post('/api/v1/auth/login', json={
            'email': 'test@example.com'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


@pytest.mark.integration
class TestTokenRefresh:
    """Test token refresh endpoint."""

    def test_refresh_token_success(self, client, db_session, sample_user):
        """Test successful token refresh."""
        # First, login to get refresh token
        login_response = client.post('/api/v1/auth/login', json={
            'email': sample_user.email,
            'password': 'password123'
        })
        refresh_token = login_response.get_json()['refresh_token']

        # Use refresh token to get new access token
        response = client.post('/api/v1/auth/refresh',
                               headers={'Authorization': f'Bearer {refresh_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data

    def test_refresh_with_access_token_fails(self, client, db_session, client_token):
        """Test refresh fails when using access token instead of refresh token."""
        response = client.post('/api/v1/auth/refresh',
                               headers={'Authorization': f'Bearer {client_token}'})

        # Should fail because we're using access token, not refresh token
        assert response.status_code in [401, 422]

    def test_refresh_without_token(self, client, db_session):
        """Test refresh fails without token."""
        response = client.post('/api/v1/auth/refresh')

        assert response.status_code == 401


@pytest.mark.integration
class TestUserLogout:
    """Test user logout endpoint."""

    def test_logout_success(self, client, db_session, client_token):
        """Test successful logout."""
        response = client.post('/api/v1/auth/logout',
                               headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data

    def test_logout_without_token(self, client, db_session):
        """Test logout fails without token."""
        response = client.post('/api/v1/auth/logout')

        assert response.status_code == 401

    def test_use_token_after_logout(self, client, db_session, client_token):
        """Test token cannot be used after logout."""
        # Logout
        logout_response = client.post('/api/v1/auth/logout',
                                      headers={'Authorization': f'Bearer {client_token}'})
        assert logout_response.status_code == 200

        # Try to use the same token
        response = client.get('/api/v1/auth/me',
                              headers={'Authorization': f'Bearer {client_token}'})

        # Should fail because token is blacklisted
        assert response.status_code == 401


@pytest.mark.integration
class TestGetCurrentUser:
    """Test get current user endpoint."""

    def test_get_current_user_success(self, client, db_session, sample_user, client_token):
        """Test successfully get current user."""
        response = client.get('/api/v1/auth/me',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['id'] == sample_user.id
        assert data['data']['email'] == sample_user.email
        assert data['data']['role'] == sample_user.role.value

    def test_get_current_user_as_admin(self, client, db_session, sample_admin, admin_token):
        """Test get current user as admin."""
        response = client.get('/api/v1/auth/me',
                              headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['id'] == sample_admin.id
        assert data['data']['role'] == 'admin'

    def test_get_current_user_as_technician(self, client, db_session, sample_technician, technician_token):
        """Test get current user as technician."""
        response = client.get('/api/v1/auth/me',
                              headers={'Authorization': f'Bearer {technician_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['id'] == sample_technician.id
        assert data['data']['role'] == 'technician'

    def test_get_current_user_without_token(self, client, db_session):
        """Test get current user fails without token."""
        response = client.get('/api/v1/auth/me')

        assert response.status_code == 401

    def test_get_current_user_with_invalid_token(self, client, db_session):
        """Test get current user fails with invalid token."""
        response = client.get('/api/v1/auth/me',
                              headers={'Authorization': 'Bearer invalid_token'})

        assert response.status_code == 422  # Unprocessable entity (invalid JWT)
