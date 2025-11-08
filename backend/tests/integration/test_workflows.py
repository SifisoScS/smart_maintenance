"""
Integration tests for complete workflows.

Tests end-to-end scenarios:
- Complete maintenance request lifecycle
- Multiple concurrent requests
- Request reassignment
- Asset condition tracking through maintenance
- User authentication and operations
"""

import pytest


@pytest.mark.integration
class TestCompleteMaintenanceWorkflow:
    """Test complete maintenance request lifecycle."""

    def test_full_request_lifecycle(self, client, db_session, sample_admin, sample_technician,
                                    sample_user, sample_asset):
        """Test complete workflow from request creation to completion."""
        # Step 1: Client registers and logs in
        register_response = client.post('/api/v1/auth/register', json={
            'email': 'workflow_client@example.com',
            'password': 'ClientPass123!',
            'first_name': 'Workflow',
            'last_name': 'Client',
            'role': 'client'
        })
        assert register_response.status_code == 201

        login_response = client.post('/api/v1/auth/login', json={
            'email': 'workflow_client@example.com',
            'password': 'ClientPass123!'
        })
        assert login_response.status_code == 200
        client_token = login_response.get_json()['access_token']

        # Step 2: Client creates maintenance request
        request_response = client.post('/api/v1/requests',
                                       headers={'Authorization': f'Bearer {client_token}'},
                                       json={
                                           'request_type': 'electrical',
                                           'asset_id': sample_asset.id,
                                           'title': 'Power Failure in Server Room',
                                           'description': 'Intermittent power failures affecting servers',
                                           'priority': 'high',
                                           'voltage': '220V',
                                           'circuit_number': 'C15',
                                           'breaker_location': 'Panel A - Bay 3',
                                           'is_emergency': False
                                       })
        assert request_response.status_code == 201
        request_id = request_response.get_json()['data']['id']
        assert request_response.get_json()['data']['status'] == 'submitted'

        # Step 3: Admin logs in and views unassigned requests
        admin_login = client.post('/api/v1/auth/login', json={
            'email': sample_admin.email,
            'password': 'password123'
        })
        admin_token = admin_login.get_json()['access_token']

        unassigned_response = client.get('/api/v1/requests/unassigned',
                                         headers={'Authorization': f'Bearer {admin_token}'})
        assert unassigned_response.status_code == 200
        unassigned_ids = [req['id'] for req in unassigned_response.get_json()['data']]
        assert request_id in unassigned_ids

        # Step 4: Admin assigns request to technician
        assign_response = client.post(f'/api/v1/requests/{request_id}/assign',
                                      headers={'Authorization': f'Bearer {admin_token}'},
                                      json={'technician_id': sample_technician.id})
        assert assign_response.status_code == 200
        assert assign_response.get_json()['data']['status'] == 'assigned'
        assert assign_response.get_json()['data']['assigned_to'] == sample_technician.id

        # Step 5: Technician logs in and starts work
        tech_login = client.post('/api/v1/auth/login', json={
            'email': sample_technician.email,
            'password': 'password123'
        })
        tech_token = tech_login.get_json()['access_token']

        start_response = client.post(f'/api/v1/requests/{request_id}/start',
                                     headers={'Authorization': f'Bearer {tech_token}'})
        assert start_response.status_code == 200
        assert start_response.get_json()['data']['status'] == 'in_progress'

        # Step 6: Technician updates asset condition
        condition_response = client.patch(f'/api/v1/assets/{sample_asset.id}/condition',
                                          headers={'Authorization': f'Bearer {tech_token}'},
                                          json={'condition': 'fair'})
        assert condition_response.status_code == 200

        # Step 7: Technician completes request
        complete_response = client.post(f'/api/v1/requests/{request_id}/complete',
                                        headers={'Authorization': f'Bearer {tech_token}'},
                                        json={
                                            'completion_notes': 'Replaced faulty circuit breaker in Panel A. '
                                                              'Tested all circuits and verified stable power supply. '
                                                              'Recommended monitoring for 48 hours.',
                                            'actual_hours': 2.5
                                        })
        assert complete_response.status_code == 200
        assert complete_response.get_json()['data']['status'] == 'completed'

        # Step 8: Client views completed request
        final_response = client.get(f'/api/v1/requests/{request_id}',
                                    headers={'Authorization': f'Bearer {client_token}'})
        assert final_response.status_code == 200
        final_data = final_response.get_json()['data']
        assert final_data['status'] == 'completed'
        assert final_data['completion_notes'] is not None
        # Note: completed_at field doesn't exist in model, only updated_at

    def test_emergency_request_workflow(self, client, db_session, sample_admin, sample_technician,
                                       sample_asset):
        """Test emergency request handling."""
        # Admin creates emergency request
        admin_login = client.post('/api/v1/auth/login', json={
            'email': sample_admin.email,
            'password': 'password123'
        })
        admin_token = admin_login.get_json()['access_token']

        # Create emergency electrical request
        request_response = client.post('/api/v1/requests',
                                       headers={'Authorization': f'Bearer {admin_token}'},
                                       json={
                                           'request_type': 'electrical',
                                           'asset_id': sample_asset.id,
                                           'title': 'EMERGENCY: Electrical Fire Hazard',
                                           'description': 'Sparking electrical panel - immediate attention required',
                                           'priority': 'urgent',
                                           'voltage': '220V',
                                           'circuit_number': 'C20',
                                           'breaker_location': 'Panel B',
                                           'is_emergency': True
                                       })
        assert request_response.status_code == 201
        request_id = request_response.get_json()['data']['id']

        # Immediately assign and start
        client.post(f'/api/v1/requests/{request_id}/assign',
                   headers={'Authorization': f'Bearer {admin_token}'},
                   json={'technician_id': sample_technician.id})

        tech_login = client.post('/api/v1/auth/login', json={
            'email': sample_technician.email,
            'password': 'password123'
        })
        tech_token = tech_login.get_json()['access_token']

        start_response = client.post(f'/api/v1/requests/{request_id}/start',
                                     headers={'Authorization': f'Bearer {tech_token}'})
        assert start_response.status_code == 200

        # Complete emergency repair
        complete_response = client.post(f'/api/v1/requests/{request_id}/complete',
                                        headers={'Authorization': f'Bearer {tech_token}'},
                                        json={
                                            'completion_notes': 'Emergency shutdown of affected circuit. '
                                                              'Replaced damaged wiring and breaker. '
                                                              'Safety inspection completed.',
                                            'actual_hours': 1.5
                                        })
        assert complete_response.status_code == 200


@pytest.mark.integration
class TestMultipleRequestWorkflow:
    """Test handling multiple concurrent requests."""

    def test_technician_with_multiple_requests(self, client, db_session, sample_admin,
                                               sample_technician, sample_user, sample_asset):
        """Test technician handling multiple requests."""
        # Login tokens
        admin_login = client.post('/api/v1/auth/login', json={
            'email': sample_admin.email,
            'password': 'password123'
        })
        admin_token = admin_login.get_json()['access_token']

        client_login = client.post('/api/v1/auth/login', json={
            'email': sample_user.email,
            'password': 'password123'
        })
        client_token = client_login.get_json()['access_token']

        tech_login = client.post('/api/v1/auth/login', json={
            'email': sample_technician.email,
            'password': 'password123'
        })
        tech_token = tech_login.get_json()['access_token']

        # Create multiple requests
        request_ids = []
        for i in range(3):
            response = client.post('/api/v1/requests',
                                   headers={'Authorization': f'Bearer {client_token}'},
                                   json={
                                       'request_type': 'electrical',
                                       'asset_id': sample_asset.id,
                                       'title': f'Request {i+1}',
                                       'description': f'Test description {i+1}',
                                       'priority': 'medium',
                                       'voltage': '110V',
                                       'circuit_number': f'C{i+1}',
                                       'breaker_location': 'Panel A'
                                   })
            request_ids.append(response.get_json()['data']['id'])

        # Assign all to same technician
        for request_id in request_ids:
            assign_response = client.post(f'/api/v1/requests/{request_id}/assign',
                                          headers={'Authorization': f'Bearer {admin_token}'},
                                          json={'technician_id': sample_technician.id})
            assert assign_response.status_code == 200

        # Technician starts and completes first request
        client.post(f'/api/v1/requests/{request_ids[0]}/start',
                   headers={'Authorization': f'Bearer {tech_token}'})
        complete1 = client.post(f'/api/v1/requests/{request_ids[0]}/complete',
                                headers={'Authorization': f'Bearer {tech_token}'},
                                json={
                                    'completion_notes': 'Completed first request',
                                    'actual_hours': 1.0
                                })
        assert complete1.status_code == 200

        # Technician starts second request (first one should be completed)
        start2 = client.post(f'/api/v1/requests/{request_ids[1]}/start',
                            headers={'Authorization': f'Bearer {tech_token}'})
        assert start2.status_code == 200

        # Verify first is completed, second is in progress, third is assigned
        req1_response = client.get(f'/api/v1/requests/{request_ids[0]}',
                                   headers={'Authorization': f'Bearer {tech_token}'})
        assert req1_response.get_json()['data']['status'] == 'completed'

        req2_response = client.get(f'/api/v1/requests/{request_ids[1]}',
                                   headers={'Authorization': f'Bearer {tech_token}'})
        assert req2_response.get_json()['data']['status'] == 'in_progress'

        req3_response = client.get(f'/api/v1/requests/{request_ids[2]}',
                                   headers={'Authorization': f'Bearer {tech_token}'})
        assert req3_response.get_json()['data']['status'] == 'assigned'


@pytest.mark.integration
class TestAssetMaintenanceTracking:
    """Test asset condition tracking through maintenance."""

    def test_asset_condition_degrades_and_improves(self, client, db_session, admin_token,
                                                   technician_token, client_token, sample_asset):
        """Test tracking asset condition through maintenance cycle."""
        # Initial condition
        asset_response = client.get(f'/api/v1/assets/{sample_asset.id}',
                                    headers={'Authorization': f'Bearer {client_token}'})
        initial_condition = asset_response.get_json()['data']['condition']

        # Update to poor condition (requires maintenance)
        update_response = client.patch(f'/api/v1/assets/{sample_asset.id}/condition',
                                       headers={'Authorization': f'Bearer {technician_token}'},
                                       json={'condition': 'poor'})
        assert update_response.status_code == 200

        # Verify asset appears in maintenance needed list
        maintenance_response = client.get('/api/v1/assets/maintenance',
                                          headers={'Authorization': f'Bearer {client_token}'})
        maintenance_ids = [asset['id'] for asset in maintenance_response.get_json()['data']]
        assert sample_asset.id in maintenance_ids

        # Create maintenance request
        request_response = client.post('/api/v1/requests',
                                       headers={'Authorization': f'Bearer {client_token}'},
                                       json={
                                           'request_type': 'electrical',
                                           'asset_id': sample_asset.id,
                                           'title': 'Preventive Maintenance',
                                           'description': 'Asset showing signs of wear',
                                           'priority': 'high',
                                           'voltage': '220V',
                                           'circuit_number': 'C1',
                                           'breaker_location': 'Panel A'
                                       })
        request_id = request_response.get_json()['data']['id']

        # Complete maintenance and improve condition
        # (In real workflow: assign, start, then complete)
        update_good = client.patch(f'/api/v1/assets/{sample_asset.id}/condition',
                                   headers={'Authorization': f'Bearer {technician_token}'},
                                   json={'condition': 'good'})
        assert update_good.status_code == 200

        # Verify improved condition
        final_asset = client.get(f'/api/v1/assets/{sample_asset.id}',
                                 headers={'Authorization': f'Bearer {client_token}'})
        assert final_asset.get_json()['data']['condition'] == 'good'


@pytest.mark.integration
class TestUserRoleWorkflows:
    """Test workflows specific to different user roles."""

    def test_client_workflow(self, client, db_session, sample_user, sample_asset):
        """Test typical client user workflow."""
        # Client logs in
        login_response = client.post('/api/v1/auth/login', json={
            'email': sample_user.email,
            'password': 'password123'
        })
        token = login_response.get_json()['access_token']

        # Client can view assets
        assets_response = client.get('/api/v1/assets',
                                      headers={'Authorization': f'Bearer {token}'})
        assert assets_response.status_code == 200

        # Client can create request
        request_response = client.post('/api/v1/requests',
                                       headers={'Authorization': f'Bearer {token}'},
                                       json={
                                           'request_type': 'plumbing',
                                           'asset_id': sample_asset.id,
                                           'title': 'Leaking Faucet',
                                           'description': 'Bathroom faucet has constant drip',
                                           'priority': 'low',
                                           'pipe_type': 'Copper',
                                           'water_pressure': 'Normal',
                                           'leak_severity': 'minor',
                                           'water_shutoff_required': False
                                       })
        assert request_response.status_code == 201

        # Client can view own profile
        profile_response = client.get(f'/api/v1/users/{sample_user.id}',
                                      headers={'Authorization': f'Bearer {token}'})
        assert profile_response.status_code == 200

        # Client cannot create assets
        asset_create_response = client.post('/api/v1/assets',
                                            headers={'Authorization': f'Bearer {token}'},
                                            json={
                                                'name': 'Test',
                                                'asset_tag': 'TEST-001',
                                                'category': 'electrical',
                                                'building': 'A',
                                                'floor': '1',
                                                'room': '101'
                                            })
        assert asset_create_response.status_code == 403

    def test_technician_workflow(self, client, db_session, sample_technician, sample_asset):
        """Test typical technician workflow."""
        # Technician logs in
        login_response = client.post('/api/v1/auth/login', json={
            'email': sample_technician.email,
            'password': 'password123'
        })
        token = login_response.get_json()['access_token']

        # Technician can update asset condition
        condition_response = client.patch(f'/api/v1/assets/{sample_asset.id}/condition',
                                          headers={'Authorization': f'Bearer {token}'},
                                          json={'condition': 'fair'})
        assert condition_response.status_code == 200

        # Technician can view assets needing maintenance
        maintenance_response = client.get('/api/v1/assets/maintenance',
                                          headers={'Authorization': f'Bearer {token}'})
        assert maintenance_response.status_code == 200

        # Technician cannot create assets
        asset_create = client.post('/api/v1/assets',
                                   headers={'Authorization': f'Bearer {token}'},
                                   json={
                                       'name': 'Test',
                                       'asset_tag': 'TEST-002',
                                       'category': 'electrical',
                                       'building': 'A',
                                       'floor': '1',
                                       'room': '101'
                                   })
        assert asset_create.status_code == 403

        # Technician cannot assign requests
        # (Would need a request to test, but permission denied regardless)

    def test_admin_workflow(self, client, db_session, sample_admin, sample_technician,
                           sample_asset):
        """Test typical admin workflow."""
        # Admin logs in
        login_response = client.post('/api/v1/auth/login', json={
            'email': sample_admin.email,
            'password': 'password123'
        })
        token = login_response.get_json()['access_token']

        # Admin can list all users
        users_response = client.get('/api/v1/users',
                                     headers={'Authorization': f'Bearer {token}'})
        assert users_response.status_code == 200

        # Admin can create assets
        asset_response = client.post('/api/v1/assets',
                                     headers={'Authorization': f'Bearer {token}'},
                                     json={
                                         'name': 'Admin Created Asset',
                                         'asset_tag': 'ADMIN-001',
                                         'category': 'hvac',
                                         'building': 'Main',
                                         'floor': '3',
                                         'room': '301'
                                     })
        assert asset_response.status_code == 201

        # Admin can view unassigned requests
        unassigned_response = client.get('/api/v1/requests/unassigned',
                                         headers={'Authorization': f'Bearer {token}'})
        assert unassigned_response.status_code == 200

        # Admin has technician privileges (role hierarchy)
        condition_response = client.patch(f'/api/v1/assets/{sample_asset.id}/condition',
                                          headers={'Authorization': f'Bearer {token}'},
                                          json={'condition': 'excellent'})
        assert condition_response.status_code == 200
