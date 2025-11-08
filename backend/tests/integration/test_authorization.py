"""
Integration tests for authorization (RBAC).

Tests role-based access control:
- Admin-only endpoints
- Technician-only endpoints
- Resource ownership
- Role hierarchy
"""

import pytest


@pytest.mark.integration
class TestAdminOnlyEndpoints:
    """Test endpoints that require admin role."""

    def test_list_users_as_admin_success(self, client, db_session, admin_token):
        """Test admin can list all users."""
        response = client.get('/api/v1/users',
                              headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert isinstance(data['data'], list)

    def test_list_users_as_technician_forbidden(self, client, db_session, technician_token):
        """Test technician cannot list users."""
        response = client.get('/api/v1/users',
                              headers={'Authorization': f'Bearer {technician_token}'})

        assert response.status_code == 403

    def test_list_users_as_client_forbidden(self, client, db_session, client_token):
        """Test client cannot list users."""
        response = client.get('/api/v1/users',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 403

    def test_list_users_unauthenticated(self, client, db_session):
        """Test unauthenticated user cannot list users."""
        response = client.get('/api/v1/users')

        assert response.status_code == 401

    def test_create_asset_as_admin_success(self, client, db_session, admin_token):
        """Test admin can create assets."""
        response = client.post('/api/v1/assets',
                               headers={'Authorization': f'Bearer {admin_token}'},
                               json={
                                   'name': 'New Asset',
                                   'asset_tag': 'ASSET-NEW-001',
                                   'category': 'electrical',
                                   'building': 'Main Building',
                                   'floor': '1',
                                   'room': '101'
                               })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['name'] == 'New Asset'

    def test_create_asset_as_technician_forbidden(self, client, db_session, technician_token):
        """Test technician cannot create assets."""
        response = client.post('/api/v1/assets',
                               headers={'Authorization': f'Bearer {technician_token}'},
                               json={
                                   'name': 'New Asset',
                                   'asset_tag': 'ASSET-NEW-002',
                                   'category': 'electrical',
                                   'building': 'Main Building',
                                   'floor': '1',
                                   'room': '101'
                               })

        assert response.status_code == 403

    def test_create_asset_as_client_forbidden(self, client, db_session, client_token):
        """Test client cannot create assets."""
        response = client.post('/api/v1/assets',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={
                                   'name': 'New Asset',
                                   'asset_tag': 'ASSET-NEW-003',
                                   'category': 'electrical',
                                   'building': 'Main Building',
                                   'floor': '1',
                                   'room': '101'
                               })

        assert response.status_code == 403

    def test_assign_request_as_admin_success(self, client, db_session, admin_token, sample_user,
                                             sample_technician, sample_asset):
        """Test admin can assign requests."""
        # Create request as client
        client_token_header = self._login_as_user(client, sample_user)

        create_response = client.post('/api/v1/requests',
                                      headers=client_token_header,
                                      json={
                                          'request_type': 'electrical',
                                          'asset_id': sample_asset.id,
                                          'title': 'Test Request',
                                          'description': 'Test description',
                                          'priority': 'high',
                                          'voltage': '220V',
                                          'circuit_number': 'C1',
                                          'breaker_location': 'Panel A'
                                      })
        request_id = create_response.get_json()['data']['id']

        # Assign as admin
        response = client.post(f'/api/v1/requests/{request_id}/assign',
                               headers={'Authorization': f'Bearer {admin_token}'},
                               json={'technician_id': sample_technician.id})

        assert response.status_code == 200

    def test_assign_request_as_technician_forbidden(self, client, db_session, technician_token,
                                                    sample_user, sample_asset):
        """Test technician cannot assign requests."""
        # Create request as client
        client_token_header = self._login_as_user(client, sample_user)

        create_response = client.post('/api/v1/requests',
                                      headers=client_token_header,
                                      json={
                                          'request_type': 'electrical',
                                          'asset_id': sample_asset.id,
                                          'title': 'Test Request',
                                          'description': 'Test description',
                                          'priority': 'high',
                                          'voltage': '220V',
                                          'circuit_number': 'C1',
                                          'breaker_location': 'Panel A'
                                      })
        request_id = create_response.get_json()['data']['id']

        # Try to assign as technician
        response = client.post(f'/api/v1/requests/{request_id}/assign',
                               headers={'Authorization': f'Bearer {technician_token}'},
                               json={'technician_id': 1})

        assert response.status_code == 403

    def test_list_unassigned_requests_as_admin_success(self, client, db_session, admin_token):
        """Test admin can list unassigned requests."""
        response = client.get('/api/v1/requests/unassigned',
                              headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data

    def test_list_unassigned_requests_as_client_forbidden(self, client, db_session, client_token):
        """Test client cannot list unassigned requests."""
        response = client.get('/api/v1/requests/unassigned',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 403

    @staticmethod
    def _login_as_user(client, user):
        """Helper to login as a user and return auth headers."""
        response = client.post('/api/v1/auth/login', json={
            'email': user.email,
            'password': 'password123'
        })
        token = response.get_json()['access_token']
        return {'Authorization': f'Bearer {token}'}


@pytest.mark.integration
class TestTechnicianEndpoints:
    """Test endpoints that require technician role."""

    def test_update_asset_condition_as_technician_success(self, client, db_session,
                                                          technician_token, sample_asset):
        """Test technician can update asset condition."""
        response = client.patch(f'/api/v1/assets/{sample_asset.id}/condition',
                                headers={'Authorization': f'Bearer {technician_token}'},
                                json={'condition': 'fair'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['condition'] == 'fair'

    def test_update_asset_condition_as_admin_success(self, client, db_session,
                                                     admin_token, sample_asset):
        """Test admin can update asset condition (role hierarchy)."""
        response = client.patch(f'/api/v1/assets/{sample_asset.id}/condition',
                                headers={'Authorization': f'Bearer {admin_token}'},
                                json={'condition': 'excellent'})

        assert response.status_code == 200

    def test_update_asset_condition_as_client_forbidden(self, client, db_session,
                                                        client_token, sample_asset):
        """Test client cannot update asset condition."""
        response = client.patch(f'/api/v1/assets/{sample_asset.id}/condition',
                                headers={'Authorization': f'Bearer {client_token}'},
                                json={'condition': 'poor'})

        assert response.status_code == 403

    def test_start_work_as_technician_success(self, client, db_session, admin_token,
                                              technician_token, sample_user,
                                              sample_technician, sample_asset):
        """Test technician can start work on assigned request."""
        # Create and assign request
        client_token_header = self._login_as_user(client, sample_user)

        create_response = client.post('/api/v1/requests',
                                      headers=client_token_header,
                                      json={
                                          'request_type': 'electrical',
                                          'asset_id': sample_asset.id,
                                          'title': 'Test Request',
                                          'description': 'Test description',
                                          'priority': 'high',
                                          'voltage': '220V',
                                          'circuit_number': 'C1',
                                          'breaker_location': 'Panel A'
                                      })
        request_id = create_response.get_json()['data']['id']

        # Assign to technician
        client.post(f'/api/v1/requests/{request_id}/assign',
                   headers={'Authorization': f'Bearer {admin_token}'},
                   json={'technician_id': sample_technician.id})

        # Start work as technician
        response = client.post(f'/api/v1/requests/{request_id}/start',
                               headers={'Authorization': f'Bearer {technician_token}'})

        assert response.status_code == 200

    def test_start_work_as_client_forbidden(self, client, db_session, client_token, sample_asset):
        """Test client cannot start work on request."""
        # Assuming a request exists
        response = client.post('/api/v1/requests/1/start',
                               headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code in [403, 404, 400]  # Forbidden or not found

    @staticmethod
    def _login_as_user(client, user):
        """Helper to login as a user and return auth headers."""
        response = client.post('/api/v1/auth/login', json={
            'email': user.email,
            'password': 'password123'
        })
        token = response.get_json()['access_token']
        return {'Authorization': f'Bearer {token}'}


@pytest.mark.integration
class TestResourceOwnership:
    """Test resource ownership validation."""

    def test_user_can_view_own_profile(self, client, db_session, sample_user, client_token):
        """Test user can view their own profile."""
        response = client.get(f'/api/v1/users/{sample_user.id}',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['id'] == sample_user.id

    def test_user_cannot_view_other_profile(self, client, db_session, sample_user,
                                           sample_technician, client_token):
        """Test user cannot view another user's profile."""
        response = client.get(f'/api/v1/users/{sample_technician.id}',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 403

    def test_admin_can_view_any_profile(self, client, db_session, sample_user, admin_token):
        """Test admin can view any user's profile."""
        response = client.get(f'/api/v1/users/{sample_user.id}',
                              headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200

    def test_user_can_update_own_profile(self, client, db_session, sample_user, client_token):
        """Test user can update their own profile."""
        response = client.put(f'/api/v1/users/{sample_user.id}',
                              headers={'Authorization': f'Bearer {client_token}'},
                              json={
                                  'first_name': 'Updated',
                                  'phone': '555-1234'
                              })

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['first_name'] == 'Updated'

    def test_user_cannot_update_other_profile(self, client, db_session, sample_technician,
                                              client_token):
        """Test user cannot update another user's profile."""
        response = client.put(f'/api/v1/users/{sample_technician.id}',
                              headers={'Authorization': f'Bearer {client_token}'},
                              json={'first_name': 'Hacked'})

        assert response.status_code == 403

    def test_admin_can_update_any_profile(self, client, db_session, sample_user, admin_token):
        """Test admin can update any user's profile."""
        response = client.put(f'/api/v1/users/{sample_user.id}',
                              headers={'Authorization': f'Bearer {admin_token}'},
                              json={'first_name': 'AdminUpdated'})

        assert response.status_code == 200

    def test_user_can_change_own_password(self, client, db_session, sample_user, client_token):
        """Test user can change their own password."""
        response = client.post(f'/api/v1/users/{sample_user.id}/password',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={
                                   'old_password': 'password123',
                                   'new_password': 'NewSecurePass456!'
                               })

        assert response.status_code == 200

    def test_user_cannot_change_other_password(self, client, db_session, sample_technician,
                                               client_token):
        """Test user cannot change another user's password."""
        response = client.post(f'/api/v1/users/{sample_technician.id}/password',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={
                                   'old_password': 'password123',
                                   'new_password': 'Hacked123!'
                               })

        assert response.status_code == 403

    def test_admin_cannot_change_other_password(self, client, db_session, sample_user, admin_token):
        """Test even admin cannot change another user's password (self-only operation)."""
        response = client.post(f'/api/v1/users/{sample_user.id}/password',
                               headers={'Authorization': f'Bearer {admin_token}'},
                               json={
                                   'old_password': 'password123',
                                   'new_password': 'NewPass123!'
                               })

        assert response.status_code == 403  # Even admin should not be able to change others' passwords


@pytest.mark.integration
class TestAuthenticatedEndpoints:
    """Test endpoints that require any authenticated user."""

    def test_list_assets_authenticated(self, client, db_session, client_token):
        """Test authenticated user can list assets."""
        response = client.get('/api/v1/assets',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200

    def test_list_assets_unauthenticated(self, client, db_session):
        """Test unauthenticated user cannot list assets."""
        response = client.get('/api/v1/assets')

        assert response.status_code == 401

    def test_create_request_authenticated(self, client, db_session, client_token, sample_asset):
        """Test authenticated user can create request."""
        response = client.post('/api/v1/requests',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={
                                   'request_type': 'electrical',
                                   'asset_id': sample_asset.id,
                                   'title': 'Test Request',
                                   'description': 'Test description',
                                   'priority': 'high',
                                   'voltage': '220V',
                                   'circuit_number': 'C1',
                                   'breaker_location': 'Panel A'
                               })

        assert response.status_code == 201

    def test_create_request_unauthenticated(self, client, db_session, sample_asset):
        """Test unauthenticated user cannot create request."""
        response = client.post('/api/v1/requests',
                               json={
                                   'request_type': 'electrical',
                                   'asset_id': sample_asset.id,
                                   'title': 'Test Request',
                                   'description': 'Test description'
                               })

        assert response.status_code == 401

    def test_list_technicians_authenticated(self, client, db_session, client_token):
        """Test authenticated user can list technicians."""
        response = client.get('/api/v1/users/technicians',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200

    def test_list_technicians_unauthenticated(self, client, db_session):
        """Test unauthenticated user cannot list technicians."""
        response = client.get('/api/v1/users/technicians')

        assert response.status_code == 401
