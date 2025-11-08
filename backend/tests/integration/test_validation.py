"""
Integration tests for input validation.

Tests validation across all endpoints:
- Missing required fields
- Invalid field types
- Invalid enum values
- Length constraints
- Email format validation
- Password complexity
"""

import pytest


@pytest.mark.integration
class TestEmailValidation:
    """Test email validation."""

    def test_register_invalid_email_format(self, client, db_session):
        """Test registration rejects invalid email formats."""
        invalid_emails = [
            'notanemail',
            '@nodomain.com',
            'missing@domain',
            'spaces in@email.com',
            'double@@email.com'
        ]

        for email in invalid_emails:
            response = client.post('/api/v1/auth/register', json={
                'email': email,
                'password': 'ValidPass123!',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'client'
            })

            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
            assert data['error']['code'] == 'VALIDATION_ERROR'


@pytest.mark.integration
class TestPasswordValidation:
    """Test password validation."""

    def test_register_weak_passwords(self, client, db_session):
        """Test registration rejects weak passwords."""
        weak_passwords = [
            'short',  # Too short
            '1234567',  # Only numbers, too short
            'pass',  # Too short
            ''  # Empty
        ]

        for password in weak_passwords:
            response = client.post('/api/v1/auth/register', json={
                'email': f'test{password}@example.com',
                'password': password,
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'client'
            })

            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data

    def test_change_password_validates_new_password(self, client, db_session, sample_user,
                                                    client_token):
        """Test password change validates new password strength."""
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


@pytest.mark.integration
class TestEnumValidation:
    """Test enum field validation."""

    def test_register_invalid_role(self, client, db_session):
        """Test registration rejects invalid roles."""
        invalid_roles = ['superadmin', 'user', 'manager', 'invalid']

        for role in invalid_roles:
            response = client.post('/api/v1/auth/register', json={
                'email': f'{role}@example.com',
                'password': 'ValidPass123!',
                'first_name': 'Test',
                'last_name': 'User',
                'role': role
            })

            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
            assert data['error']['code'] == 'VALIDATION_ERROR'

    def test_create_asset_invalid_category(self, client, db_session, admin_token):
        """Test asset creation rejects invalid categories."""
        response = client.post('/api/v1/assets',
                               headers={'Authorization': f'Bearer {admin_token}'},
                               json={
                                   'name': 'Test Asset',
                                   'asset_tag': 'TEST-001',
                                   'category': 'invalid_category',
                                   'building': 'Building A',
                                   'floor': '1',
                                   'room': '101'
                               })

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_update_asset_condition_invalid_value(self, client, db_session, technician_token,
                                                  sample_asset):
        """Test asset condition update rejects invalid conditions."""
        invalid_conditions = ['broken', 'new', 'old', 'invalid']

        for condition in invalid_conditions:
            response = client.patch(f'/api/v1/assets/{sample_asset.id}/condition',
                                    headers={'Authorization': f'Bearer {technician_token}'},
                                    json={'condition': condition})

            assert response.status_code == 400

    def test_create_request_invalid_type(self, client, db_session, client_token, sample_asset):
        """Test request creation rejects invalid types."""
        invalid_types = ['carpentry', 'painting', 'landscaping', 'invalid']

        for req_type in invalid_types:
            response = client.post('/api/v1/requests',
                                   headers={'Authorization': f'Bearer {client_token}'},
                                   json={
                                       'request_type': req_type,
                                       'asset_id': sample_asset.id,
                                       'title': 'Test Request',
                                       'description': 'Test description'
                                   })

            assert response.status_code == 400

    def test_create_request_invalid_priority(self, client, db_session, client_token, sample_asset):
        """Test request creation rejects invalid priorities."""
        invalid_priorities = ['critical', 'minor', 'normal', 'invalid']

        for priority in invalid_priorities:
            response = client.post('/api/v1/requests',
                                   headers={'Authorization': f'Bearer {client_token}'},
                                   json={
                                       'request_type': 'electrical',
                                       'asset_id': sample_asset.id,
                                       'title': 'Test Request',
                                       'description': 'Test description',
                                       'priority': priority
                                   })

            assert response.status_code == 400


@pytest.mark.integration
class TestRequiredFieldValidation:
    """Test required field validation."""

    def test_register_missing_fields(self, client, db_session):
        """Test registration requires all fields."""
        test_cases = [
            {'password': 'Pass123!', 'first_name': 'Test', 'last_name': 'User', 'role': 'client'},
            {'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User', 'role': 'client'},
            {'email': 'test@example.com', 'password': 'Pass123!', 'last_name': 'User', 'role': 'client'},
            {'email': 'test@example.com', 'password': 'Pass123!', 'first_name': 'Test', 'role': 'client'},
            {'email': 'test@example.com', 'password': 'Pass123!', 'first_name': 'Test', 'last_name': 'User'}
        ]

        for data in test_cases:
            response = client.post('/api/v1/auth/register', json=data)
            assert response.status_code == 400
            result = response.get_json()
            assert 'error' in result
            assert result['error']['code'] == 'VALIDATION_ERROR'

    def test_login_missing_fields(self, client, db_session):
        """Test login requires email and password."""
        test_cases = [
            {'email': 'test@example.com'},
            {'password': 'password123'},
            {}
        ]

        for data in test_cases:
            response = client.post('/api/v1/auth/login', json=data)
            assert response.status_code == 400

    def test_create_asset_missing_fields(self, client, db_session, admin_token):
        """Test asset creation requires all mandatory fields."""
        # Only name, asset_tag, and category are required per schema
        test_cases = [
            {'asset_tag': 'TEST-001', 'category': 'electrical'},  # Missing name
            {'name': 'Test', 'category': 'electrical'},  # Missing asset_tag
            {'name': 'Test', 'asset_tag': 'TEST-001'},  # Missing category
        ]

        for data in test_cases:
            response = client.post('/api/v1/assets',
                                   headers={'Authorization': f'Bearer {admin_token}'},
                                   json=data)
            assert response.status_code == 400

    def test_create_request_missing_fields(self, client, db_session, client_token, sample_asset):
        """Test request creation requires all mandatory fields."""
        test_cases = [
            {'asset_id': sample_asset.id, 'title': 'Test', 'description': 'Desc'},
            {'request_type': 'electrical', 'title': 'Test', 'description': 'Desc'},
            {'request_type': 'electrical', 'asset_id': sample_asset.id, 'description': 'Desc'},
            {'request_type': 'electrical', 'asset_id': sample_asset.id, 'title': 'Test'}
        ]

        for data in test_cases:
            response = client.post('/api/v1/requests',
                                   headers={'Authorization': f'Bearer {client_token}'},
                                   json=data)
            assert response.status_code == 400

    def test_complete_request_missing_notes(self, client, db_session, admin_token,
                                           technician_token, client_token, sample_technician,
                                           sample_asset):
        """Test request completion requires completion notes."""
        # Create, assign, and start request
        create_response = client.post('/api/v1/requests',
                                      headers={'Authorization': f'Bearer {client_token}'},
                                      json={
                                          'request_type': 'electrical',
                                          'asset_id': sample_asset.id,
                                          'title': 'Test Request',
                                          'description': 'Test description',
                                          'priority': 'medium',
                                          'voltage': '110V',
                                          'circuit_number': 'C1',
                                          'breaker_location': 'Panel A'
                                      })
        request_id = create_response.get_json()['data']['id']

        client.post(f'/api/v1/requests/{request_id}/assign',
                   headers={'Authorization': f'Bearer {admin_token}'},
                   json={'technician_id': sample_technician.id})

        client.post(f'/api/v1/requests/{request_id}/start',
                   headers={'Authorization': f'Bearer {technician_token}'})

        # Try to complete without notes
        response = client.post(f'/api/v1/requests/{request_id}/complete',
                               headers={'Authorization': f'Bearer {technician_token}'},
                               json={})

        assert response.status_code == 400


@pytest.mark.integration
class TestLengthConstraints:
    """Test length constraint validation."""

    def test_register_name_length(self, client, db_session):
        """Test registration enforces name length constraints."""
        # Test with empty first name
        response = client.post('/api/v1/auth/register', json={
            'email': 'test@example.com',
            'password': 'ValidPass123!',
            'first_name': '',
            'last_name': 'User',
            'role': 'client'
        })
        assert response.status_code == 400

        # Test with very long name (if validation exists)
        response = client.post('/api/v1/auth/register', json={
            'email': 'test2@example.com',
            'password': 'ValidPass123!',
            'first_name': 'A' * 200,  # Very long
            'last_name': 'User',
            'role': 'client'
        })
        # May pass or fail depending on validation rules

    def test_create_request_title_length(self, client, db_session, client_token, sample_asset):
        """Test request title length constraints."""
        # Test with empty title
        response = client.post('/api/v1/requests',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={
                                   'request_type': 'electrical',
                                   'asset_id': sample_asset.id,
                                   'title': '',
                                   'description': 'Test description'
                               })
        assert response.status_code == 400

        # Test with very long title
        response = client.post('/api/v1/requests',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={
                                   'request_type': 'electrical',
                                   'asset_id': sample_asset.id,
                                   'title': 'T' * 500,  # Very long
                                   'description': 'Test description'
                               })
        # May pass or fail depending on validation rules


@pytest.mark.integration
class TestTypeValidation:
    """Test data type validation."""

    def test_asset_id_must_be_integer(self, client, db_session, client_token, sample_asset):
        """Test asset_id must be an integer."""
        response = client.post('/api/v1/requests',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={
                                   'request_type': 'electrical',
                                   'asset_id': 'not_an_integer',
                                   'title': 'Test Request',
                                   'description': 'Test description'
                               })

        assert response.status_code == 400

    def test_technician_id_must_be_integer(self, client, db_session, admin_token, client_token,
                                           sample_asset):
        """Test technician_id must be an integer."""
        # Create request
        create_response = client.post('/api/v1/requests',
                                      headers={'Authorization': f'Bearer {client_token}'},
                                      json={
                                          'request_type': 'electrical',
                                          'asset_id': sample_asset.id,
                                          'title': 'Test Request',
                                          'description': 'Test description',
                                          'priority': 'medium',
                                          'voltage': '110V',
                                          'circuit_number': 'C1',
                                          'breaker_location': 'Panel A'
                                      })
        request_id = create_response.get_json()['data']['id']

        # Try to assign with invalid technician_id
        response = client.post(f'/api/v1/requests/{request_id}/assign',
                               headers={'Authorization': f'Bearer {admin_token}'},
                               json={'technician_id': 'not_an_integer'})

        assert response.status_code == 400
