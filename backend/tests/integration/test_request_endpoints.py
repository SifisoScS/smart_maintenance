"""
Integration tests for request management endpoints.

Tests:
- Create request (electrical, plumbing, HVAC)
- List requests
- Get request
- Assign request
- Start work
- Complete request
- List unassigned requests
"""

import pytest


@pytest.mark.integration
class TestCreateRequest:
    """Test create maintenance request endpoint."""

    def test_create_electrical_request_success(self, client, db_session, client_token, sample_asset):
        """Test successful electrical request creation."""
        response = client.post('/api/v1/requests',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={
                                   'request_type': 'electrical',
                                   'asset_id': sample_asset.id,
                                   'title': 'Power Issue',
                                   'description': 'Server experiencing power failures',
                                   'priority': 'high',
                                   'voltage': '220V',
                                   'circuit_number': 'C15',
                                   'breaker_location': 'Panel A',
                                   'is_emergency': False
                               })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['title'] == 'Power Issue'
        assert data['data']['request_type'] == 'electrical'
        assert data['data']['status'] == 'submitted'

    def test_create_plumbing_request_success(self, client, db_session, client_token, sample_asset):
        """Test successful plumbing request creation."""
        response = client.post('/api/v1/requests',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={
                                   'request_type': 'plumbing',
                                   'asset_id': sample_asset.id,
                                   'title': 'Pipe Leak',
                                   'description': 'Water leak in restroom',
                                   'priority': 'urgent',
                                   'pipe_type': 'PVC',
                                   'water_pressure': 'High',
                                   'leak_severity': 'major',
                                   'water_shutoff_required': True
                               })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['request_type'] == 'plumbing'

    def test_create_hvac_request_success(self, client, db_session, client_token, sample_asset):
        """Test successful HVAC request creation."""
        response = client.post('/api/v1/requests',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={
                                   'request_type': 'hvac',
                                   'asset_id': sample_asset.id,
                                   'title': 'AC Not Cooling',
                                   'description': 'Air conditioner not cooling properly',
                                   'priority': 'medium',
                                   'system_type': 'Central AC',
                                   'temperature_issue': 'Too warm - 28°C',
                                   'refrigerant_leak': False
                               })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['request_type'] == 'hvac'

    def test_create_request_missing_required_fields(self, client, db_session, client_token):
        """Test request creation fails with missing required fields."""
        response = client.post('/api/v1/requests',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={
                                   'title': 'Incomplete Request'
                                   # Missing request_type, asset_id, description
                               })

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'

    def test_create_request_invalid_type(self, client, db_session, client_token, sample_asset):
        """Test request creation fails with invalid request type."""
        response = client.post('/api/v1/requests',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={
                                   'request_type': 'invalid_type',
                                   'asset_id': sample_asset.id,
                                   'title': 'Test Request',
                                   'description': 'Test description'
                               })

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_create_request_invalid_asset(self, client, db_session, client_token):
        """Test request creation fails with nonexistent asset."""
        response = client.post('/api/v1/requests',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={
                                   'request_type': 'electrical',
                                   'asset_id': 99999,
                                   'title': 'Test Request',
                                   'description': 'Test description'
                               })

        assert response.status_code == 400

    def test_create_request_invalid_priority(self, client, db_session, client_token, sample_asset):
        """Test request creation fails with invalid priority."""
        response = client.post('/api/v1/requests',
                               headers={'Authorization': f'Bearer {client_token}'},
                               json={
                                   'request_type': 'electrical',
                                   'asset_id': sample_asset.id,
                                   'title': 'Test Request',
                                   'description': 'Test description',
                                   'priority': 'invalid_priority'
                               })

        assert response.status_code == 400


@pytest.mark.integration
class TestListRequests:
    """Test list requests endpoint."""

    def test_list_requests_success(self, client, db_session, client_token, sample_user, sample_asset):
        """Test successful request listing."""
        # Create a request first
        client.post('/api/v1/requests',
                    headers={'Authorization': f'Bearer {client_token}'},
                    json={
                        'request_type': 'electrical',
                        'asset_id': sample_asset.id,
                        'title': 'Test Request',
                        'description': 'Test description',
                        'priority': 'medium',
                        'voltage': '110V',
                        'circuit_number': 'C1',
                        'breaker_location': 'Panel B'
                    })

        response = client.get('/api/v1/requests',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'total' in data
        assert len(data['data']) > 0

    def test_list_requests_includes_all_types(self, client, db_session, client_token, sample_asset):
        """Test listing includes all request types."""
        # Create requests of different types
        for req_type in ['electrical', 'plumbing', 'hvac']:
            client.post('/api/v1/requests',
                        headers={'Authorization': f'Bearer {client_token}'},
                        json={
                            'request_type': req_type,
                            'asset_id': sample_asset.id,
                            'title': f'{req_type.title()} Request',
                            'description': 'Test description',
                            'priority': 'medium'
                        })

        response = client.get('/api/v1/requests',
                              headers={'Authorization': f'Bearer {client_token}'})

        data = response.get_json()
        request_types = [req['request_type'] for req in data['data']]

        assert 'electrical' in request_types
        assert 'plumbing' in request_types
        assert 'hvac' in request_types


@pytest.mark.integration
class TestGetRequest:
    """Test get request endpoint."""

    def test_get_request_success(self, client, db_session, client_token, sample_asset):
        """Test successfully get request by ID."""
        # Create request
        create_response = client.post('/api/v1/requests',
                                      headers={'Authorization': f'Bearer {client_token}'},
                                      json={
                                          'request_type': 'electrical',
                                          'asset_id': sample_asset.id,
                                          'title': 'Get Test Request',
                                          'description': 'Test description',
                                          'priority': 'high',
                                          'voltage': '220V',
                                          'circuit_number': 'C10',
                                          'breaker_location': 'Panel C'
                                      })
        request_id = create_response.get_json()['data']['id']

        # Get the request
        response = client.get(f'/api/v1/requests/{request_id}',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['id'] == request_id
        assert data['data']['title'] == 'Get Test Request'

    def test_get_nonexistent_request(self, client, db_session, client_token):
        """Test get nonexistent request returns 404."""
        response = client.get('/api/v1/requests/99999',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data


@pytest.mark.integration
class TestAssignRequest:
    """Test assign request endpoint."""

    def test_assign_request_success(self, client, db_session, admin_token, client_token,
                                    sample_user, sample_technician, sample_asset):
        """Test successful request assignment."""
        # Create request
        create_response = client.post('/api/v1/requests',
                                      headers={'Authorization': f'Bearer {client_token}'},
                                      json={
                                          'request_type': 'electrical',
                                          'asset_id': sample_asset.id,
                                          'title': 'Assign Test Request',
                                          'description': 'Test description',
                                          'priority': 'high',
                                          'voltage': '220V',
                                          'circuit_number': 'C5',
                                          'breaker_location': 'Panel D'
                                      })
        request_id = create_response.get_json()['data']['id']

        # Assign to technician
        response = client.post(f'/api/v1/requests/{request_id}/assign',
                               headers={'Authorization': f'Bearer {admin_token}'},
                               json={'technician_id': sample_technician.id})

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['status'] == 'assigned'
        assert data['data']['assigned_to'] == sample_technician.id

    def test_assign_request_invalid_technician(self, client, db_session, admin_token,
                                               client_token, sample_asset):
        """Test assignment fails with invalid technician."""
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

        # Try to assign to non-existent technician
        response = client.post(f'/api/v1/requests/{request_id}/assign',
                               headers={'Authorization': f'Bearer {admin_token}'},
                               json={'technician_id': 99999})

        assert response.status_code == 400

    def test_assign_nonexistent_request(self, client, db_session, admin_token, sample_technician):
        """Test assigning nonexistent request fails."""
        response = client.post('/api/v1/requests/99999/assign',
                               headers={'Authorization': f'Bearer {admin_token}'},
                               json={'technician_id': sample_technician.id})

        assert response.status_code == 400


@pytest.mark.integration
class TestStartWork:
    """Test start work endpoint."""

    def test_start_work_success(self, client, db_session, admin_token, technician_token,
                                client_token, sample_technician, sample_asset):
        """Test technician can start work on assigned request."""
        # Create and assign request
        create_response = client.post('/api/v1/requests',
                                      headers={'Authorization': f'Bearer {client_token}'},
                                      json={
                                          'request_type': 'electrical',
                                          'asset_id': sample_asset.id,
                                          'title': 'Start Work Test',
                                          'description': 'Test description',
                                          'priority': 'high',
                                          'voltage': '220V',
                                          'circuit_number': 'C7',
                                          'breaker_location': 'Panel E'
                                      })
        request_id = create_response.get_json()['data']['id']

        client.post(f'/api/v1/requests/{request_id}/assign',
                   headers={'Authorization': f'Bearer {admin_token}'},
                   json={'technician_id': sample_technician.id})

        # Start work
        response = client.post(f'/api/v1/requests/{request_id}/start',
                               headers={'Authorization': f'Bearer {technician_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['status'] == 'in_progress'

    def test_start_work_unassigned_request(self, client, db_session, technician_token,
                                          client_token, sample_asset):
        """Test cannot start work on unassigned request."""
        # Create request (don't assign)
        create_response = client.post('/api/v1/requests',
                                      headers={'Authorization': f'Bearer {client_token}'},
                                      json={
                                          'request_type': 'electrical',
                                          'asset_id': sample_asset.id,
                                          'title': 'Unassigned Request',
                                          'description': 'Test description',
                                          'priority': 'medium',
                                          'voltage': '110V',
                                          'circuit_number': 'C2',
                                          'breaker_location': 'Panel A'
                                      })
        request_id = create_response.get_json()['data']['id']

        # Try to start work
        response = client.post(f'/api/v1/requests/{request_id}/start',
                               headers={'Authorization': f'Bearer {technician_token}'})

        assert response.status_code == 400


@pytest.mark.integration
class TestCompleteRequest:
    """Test complete request endpoint."""

    def test_complete_request_success(self, client, db_session, admin_token, technician_token,
                                      client_token, sample_technician, sample_asset):
        """Test technician can complete assigned request."""
        # Create, assign, and start request
        create_response = client.post('/api/v1/requests',
                                      headers={'Authorization': f'Bearer {client_token}'},
                                      json={
                                          'request_type': 'electrical',
                                          'asset_id': sample_asset.id,
                                          'title': 'Complete Test Request',
                                          'description': 'Test description',
                                          'priority': 'high',
                                          'voltage': '220V',
                                          'circuit_number': 'C8',
                                          'breaker_location': 'Panel F'
                                      })
        request_id = create_response.get_json()['data']['id']

        client.post(f'/api/v1/requests/{request_id}/assign',
                   headers={'Authorization': f'Bearer {admin_token}'},
                   json={'technician_id': sample_technician.id})

        client.post(f'/api/v1/requests/{request_id}/start',
                   headers={'Authorization': f'Bearer {technician_token}'})

        # Complete work
        response = client.post(f'/api/v1/requests/{request_id}/complete',
                               headers={'Authorization': f'Bearer {technician_token}'},
                               json={
                                   'completion_notes': 'Replaced circuit breaker and tested system',
                                   'actual_hours': 2.5
                               })

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['status'] == 'completed'

    def test_complete_request_missing_notes(self, client, db_session, admin_token, technician_token,
                                           client_token, sample_technician, sample_asset):
        """Test completion fails without notes."""
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
                                          'circuit_number': 'C3',
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
class TestListUnassignedRequests:
    """Test list unassigned requests endpoint."""

    def test_list_unassigned_requests(self, client, db_session, admin_token, client_token,
                                      sample_asset):
        """Test admin can list unassigned requests."""
        # Create unassigned request
        client.post('/api/v1/requests',
                    headers={'Authorization': f'Bearer {client_token}'},
                    json={
                        'request_type': 'electrical',
                        'asset_id': sample_asset.id,
                        'title': 'Unassigned Request',
                        'description': 'Test description',
                        'priority': 'high',
                        'voltage': '220V',
                        'circuit_number': 'C9',
                        'breaker_location': 'Panel G'
                    })

        response = client.get('/api/v1/requests/unassigned',
                              headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert len(data['data']) > 0

    def test_list_unassigned_excludes_assigned(self, client, db_session, admin_token,
                                               client_token, sample_technician, sample_asset):
        """Test unassigned list excludes assigned requests."""
        # Create and assign a request
        create_response = client.post('/api/v1/requests',
                                      headers={'Authorization': f'Bearer {client_token}'},
                                      json={
                                          'request_type': 'electrical',
                                          'asset_id': sample_asset.id,
                                          'title': 'Assigned Request',
                                          'description': 'Test description',
                                          'priority': 'medium',
                                          'voltage': '110V',
                                          'circuit_number': 'C4',
                                          'breaker_location': 'Panel B'
                                      })
        request_id = create_response.get_json()['data']['id']

        client.post(f'/api/v1/requests/{request_id}/assign',
                   headers={'Authorization': f'Bearer {admin_token}'},
                   json={'technician_id': sample_technician.id})

        # List unassigned
        response = client.get('/api/v1/requests/unassigned',
                              headers={'Authorization': f'Bearer {admin_token}'})

        data = response.get_json()
        request_ids = [req['id'] for req in data['data']]
        assert request_id not in request_ids
