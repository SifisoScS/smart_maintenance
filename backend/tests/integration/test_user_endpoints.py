"""
Integration tests for user management endpoints.

Tests:
- List users
- Get user profile
- Update user profile
- Change password
- List technicians
"""

import pytest


@pytest.mark.integration
class TestListUsers:
    """Test list users endpoint."""

    def test_list_users_returns_all_users(self, client, db_session, admin_token, multiple_users):
        """Test listing users returns all users."""
        response = client.get('/api/v1/users',
                              headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'total' in data
        # admin_token creates sample_admin, so total is multiple_users + 1
        assert data['total'] == len(multiple_users) + 1
        assert len(data['data']) == len(multiple_users) + 1

    def test_list_users_includes_all_roles(self, client, db_session, admin_token, multiple_users):
        """Test listing users includes all roles."""
        response = client.get('/api/v1/users',
                              headers={'Authorization': f'Bearer {admin_token}'})

        data = response.get_json()
        roles = [user['role'] for user in data['data']]

        assert 'admin' in roles
        assert 'technician' in roles
        assert 'client' in roles

    def test_list_users_excludes_passwords(self, client, db_session, admin_token, sample_user):
        """Test listing users does not include passwords."""
        response = client.get('/api/v1/users',
                              headers={'Authorization': f'Bearer {admin_token}'})

        data = response.get_json()
        for user in data['data']:
            assert 'password' not in user
            assert 'password_hash' not in user


@pytest.mark.integration
class TestGetUserProfile:
    """Test get user profile endpoint."""

    def test_get_own_profile_success(self, client, db_session, sample_user, client_token):
        """Test user can get their own profile."""
        response = client.get(f'/api/v1/users/{sample_user.id}',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['id'] == sample_user.id
        assert data['data']['email'] == sample_user.email
        assert data['data']['first_name'] == sample_user.first_name
        assert data['data']['last_name'] == sample_user.last_name
        assert 'password' not in data['data']

    def test_get_nonexistent_user(self, client, db_session, admin_token):
        """Test getting nonexistent user returns 404."""
        response = client.get('/api/v1/users/99999',
                              headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data

    def test_get_profile_includes_role_info(self, client, db_session, sample_technician,
                                           technician_token):
        """Test profile includes role information."""
        response = client.get(f'/api/v1/users/{sample_technician.id}',
                              headers={'Authorization': f'Bearer {technician_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['role'] == 'technician'


@pytest.mark.integration
class TestUpdateUserProfile:
    """Test update user profile endpoint."""

    def test_update_own_profile_success(self, client, db_session, sample_user, client_token):
        """Test user can update their own profile."""
        response = client.put(f'/api/v1/users/{sample_user.id}',
                              headers={'Authorization': f'Bearer {client_token}'},
                              json={
                                  'first_name': 'Updated',
                                  'last_name': 'Name',
                                  'phone': '555-1234',
                                  'department': 'Engineering'
                              })

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['first_name'] == 'Updated'
        assert data['data']['last_name'] == 'Name'
        assert data['data']['phone'] == '555-1234'
        assert data['data']['department'] == 'Engineering'

    def test_update_partial_profile(self, client, db_session, sample_user, client_token):
        """Test partial profile update."""
        original_last_name = sample_user.last_name

        response = client.put(f'/api/v1/users/{sample_user.id}',
                              headers={'Authorization': f'Bearer {client_token}'},
                              json={'first_name': 'PartialUpdate'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['first_name'] == 'PartialUpdate'
        assert data['data']['last_name'] == original_last_name  # Should remain unchanged

    def test_update_profile_invalid_data(self, client, db_session, sample_user, client_token):
        """Test update with invalid data fails."""
        response = client.put(f'/api/v1/users/{sample_user.id}',
                              headers={'Authorization': f'Bearer {client_token}'},
                              json={'first_name': ''})  # Empty name

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_update_nonexistent_user(self, client, db_session, admin_token):
        """Test updating nonexistent user returns 404."""
        response = client.put('/api/v1/users/99999',
                              headers={'Authorization': f'Bearer {admin_token}'},
                              json={'first_name': 'Test'})

        assert response.status_code in [400, 404]

    def test_update_profile_cannot_change_email(self, client, db_session, sample_user, client_token):
        """Test users cannot change their email through profile update."""
        original_email = sample_user.email

        response = client.put(f'/api/v1/users/{sample_user.id}',
                              headers={'Authorization': f'Bearer {client_token}'},
                              json={'email': 'newemail@example.com'})

        # Email should not be updatable through this endpoint
        # Verify by getting the profile
        profile_response = client.get(f'/api/v1/users/{sample_user.id}',
                                      headers={'Authorization': f'Bearer {client_token}'})
        data = profile_response.get_json()
        assert data['data']['email'] == original_email


@pytest.mark.integration
class TestChangePassword:
    """Test change password endpoint."""

    def test_change_password_success(self, client, db_session, sample_user, client_token):
        """Test successful password change."""
        response = client.post(f'/api/v1/users/{sample_user.id}/password',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={
                                   'old_password': 'password123',
                                   'new_password': 'NewSecurePass456!'
                               })

        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data

        # Verify can login with new password
        login_response = client.post('/api/v1/auth/login', json={
            'email': sample_user.email,
            'password': 'NewSecurePass456!'
        })
        assert login_response.status_code == 200

    def test_change_password_wrong_old_password(self, client, db_session, sample_user, client_token):
        """Test password change fails with wrong old password."""
        response = client.post(f'/api/v1/users/{sample_user.id}/password',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={
                                   'old_password': 'wrongpassword',
                                   'new_password': 'NewSecurePass456!'
                               })

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_change_password_weak_new_password(self, client, db_session, sample_user, client_token):
        """Test password change fails with weak new password."""
        response = client.post(f'/api/v1/users/{sample_user.id}/password',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={
                                   'old_password': 'password123',
                                   'new_password': 'weak'
                               })

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'

    def test_change_password_missing_old_password(self, client, db_session, sample_user, client_token):
        """Test password change fails without old password."""
        response = client.post(f'/api/v1/users/{sample_user.id}/password',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={'new_password': 'NewSecurePass456!'})

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_change_password_missing_new_password(self, client, db_session, sample_user, client_token):
        """Test password change fails without new password."""
        response = client.post(f'/api/v1/users/{sample_user.id}/password',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={'old_password': 'password123'})

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


@pytest.mark.integration
class TestListTechnicians:
    """Test list technicians endpoint."""

    def test_list_technicians_returns_only_technicians(self, client, db_session, client_token,
                                                       multiple_users):
        """Test list technicians returns only technician role users."""
        response = client.get('/api/v1/users/technicians',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data

        # Verify all returned users are technicians
        for user in data['data']:
            assert user['role'] == 'technician'

        # Count technicians in fixture (3 technicians created in multiple_users)
        expected_count = sum(1 for u in multiple_users if u.role.value == 'technician')
        assert len(data['data']) == expected_count

    def test_list_technicians_excludes_inactive(self, client, db_session, client_token,
                                                sample_technician):
        """Test list technicians excludes inactive technicians."""
        # Deactivate technician
        sample_technician.is_active = False
        db_session.session.commit()

        response = client.get('/api/v1/users/technicians',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200
        data = response.get_json()

        # Sample technician should not be in the list
        technician_ids = [user['id'] for user in data['data']]
        assert sample_technician.id not in technician_ids

    def test_list_technicians_includes_relevant_info(self, client, db_session, client_token,
                                                     sample_technician):
        """Test list technicians includes relevant information."""
        # Reactivate if needed
        sample_technician.is_active = True
        db_session.session.commit()

        response = client.get('/api/v1/users/technicians',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200
        data = response.get_json()

        if len(data['data']) > 0:
            tech = data['data'][0]
            assert 'id' in tech
            assert 'email' in tech
            assert 'first_name' in tech
            assert 'last_name' in tech
            assert 'role' in tech
            assert 'password' not in tech
