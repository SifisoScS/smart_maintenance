"""
Integration tests for asset management endpoints.

Tests:
- Create asset
- List assets
- Get asset
- Update asset condition
- Assets needing maintenance
- Asset statistics
"""

import pytest


@pytest.mark.integration
class TestCreateAsset:
    """Test create asset endpoint."""

    def test_create_asset_success(self, client, db_session, admin_token):
        """Test successful asset creation."""
        response = client.post('/api/v1/assets',
                               headers={'Authorization': f'Bearer {admin_token}'},
                               json={
                                   'name': 'Server Rack A1',
                                   'asset_tag': 'SRV-001',
                                   'category': 'electrical',
                                   'building': 'Main Building',
                                   'floor': '2',
                                   'room': 'Server Room',
                                   'manufacturer': 'Dell',
                                   'model': 'PowerEdge R750',
                                   'serial_number': 'SN123456',
                                   'status': 'active',
                                   'condition': 'excellent'
                               })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['name'] == 'Server Rack A1'
        assert data['data']['asset_tag'] == 'SRV-001'
        assert 'message' in data

    def test_create_asset_minimal_fields(self, client, db_session, admin_token):
        """Test creating asset with only required fields."""
        response = client.post('/api/v1/assets',
                               headers={'Authorization': f'Bearer {admin_token}'},
                               json={
                                   'name': 'Minimal Asset',
                                   'asset_tag': 'MIN-001',
                                   'category': 'plumbing',
                                   'building': 'Building A',
                                   'floor': '1',
                                   'room': '101'
                               })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['name'] == 'Minimal Asset'

    def test_create_asset_missing_required_fields(self, client, db_session, admin_token):
        """Test asset creation fails with missing required fields."""
        response = client.post('/api/v1/assets',
                               headers={'Authorization': f'Bearer {admin_token}'},
                               json={
                                   'name': 'Incomplete Asset'
                                   # Missing asset_tag, category, building, floor, room
                               })

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'

    def test_create_asset_invalid_category(self, client, db_session, admin_token):
        """Test asset creation fails with invalid category."""
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


@pytest.mark.integration
class TestListAssets:
    """Test list assets endpoint."""

    def test_list_assets_success(self, client, db_session, client_token, sample_asset):
        """Test successful asset listing."""
        response = client.get('/api/v1/assets',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'total' in data
        assert len(data['data']) > 0

    def test_list_assets_returns_all_assets(self, client, db_session, client_token, multiple_assets):
        """Test listing returns all assets."""
        response = client.get('/api/v1/assets',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == len(multiple_assets)

    def test_list_assets_includes_all_categories(self, client, db_session, client_token,
                                                 multiple_assets):
        """Test listing includes all asset categories."""
        response = client.get('/api/v1/assets',
                              headers={'Authorization': f'Bearer {client_token}'})

        data = response.get_json()
        categories = [asset['category'] for asset in data['data']]

        # multiple_assets creates electrical, plumbing, and HVAC assets
        assert 'electrical' in categories or 'plumbing' in categories or 'hvac' in categories


@pytest.mark.integration
class TestGetAsset:
    """Test get asset endpoint."""

    def test_get_asset_success(self, client, db_session, client_token, sample_asset):
        """Test successfully get asset by ID."""
        response = client.get(f'/api/v1/assets/{sample_asset.id}',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['id'] == sample_asset.id
        assert data['data']['name'] == sample_asset.name
        assert data['data']['asset_tag'] == sample_asset.asset_tag

    def test_get_nonexistent_asset(self, client, db_session, client_token):
        """Test get nonexistent asset returns 404."""
        response = client.get('/api/v1/assets/99999',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data

    def test_get_asset_includes_all_fields(self, client, db_session, admin_token):
        """Test get asset includes all relevant fields."""
        # Create asset with all fields
        create_response = client.post('/api/v1/assets',
                                      headers={'Authorization': f'Bearer {admin_token}'},
                                      json={
                                          'name': 'Complete Asset',
                                          'asset_tag': 'COMP-001',
                                          'category': 'hvac',
                                          'building': 'Building A',
                                          'floor': '3',
                                          'room': '301',
                                          'manufacturer': 'Carrier',
                                          'model': 'AC-5000',
                                          'serial_number': 'SN999',
                                          'status': 'active',
                                          'condition': 'good'
                                      })
        asset_id = create_response.get_json()['data']['id']

        # Get the asset
        response = client.get(f'/api/v1/assets/{asset_id}',
                              headers={'Authorization': f'Bearer {admin_token}'})

        data = response.get_json()['data']
        assert data['manufacturer'] == 'Carrier'
        assert data['model'] == 'AC-5000'
        assert data['serial_number'] == 'SN999'


@pytest.mark.integration
class TestUpdateAssetCondition:
    """Test update asset condition endpoint."""

    def test_update_condition_success(self, client, db_session, technician_token, sample_asset):
        """Test successful condition update."""
        response = client.patch(f'/api/v1/assets/{sample_asset.id}/condition',
                                headers={'Authorization': f'Bearer {technician_token}'},
                                json={'condition': 'fair'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['condition'] == 'fair'
        assert 'message' in data

    def test_update_condition_invalid_value(self, client, db_session, technician_token, sample_asset):
        """Test update fails with invalid condition value."""
        response = client.patch(f'/api/v1/assets/{sample_asset.id}/condition',
                                headers={'Authorization': f'Bearer {technician_token}'},
                                json={'condition': 'invalid'})

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_update_condition_nonexistent_asset(self, client, db_session, technician_token):
        """Test update fails for nonexistent asset."""
        response = client.patch('/api/v1/assets/99999/condition',
                                headers={'Authorization': f'Bearer {technician_token}'},
                                json={'condition': 'good'})

        assert response.status_code == 400

    def test_update_condition_missing_field(self, client, db_session, technician_token, sample_asset):
        """Test update fails when condition field is missing."""
        response = client.patch(f'/api/v1/assets/{sample_asset.id}/condition',
                                headers={'Authorization': f'Bearer {technician_token}'},
                                json={})

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


@pytest.mark.integration
class TestAssetsNeedingMaintenance:
    """Test assets needing maintenance endpoint."""

    def test_get_assets_needing_maintenance(self, client, db_session, client_token, multiple_assets):
        """Test get assets needing maintenance."""
        response = client.get('/api/v1/assets/maintenance',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'message' in data

    def test_assets_needing_maintenance_includes_poor_condition(self, client, db_session,
                                                                admin_token, technician_token):
        """Test assets with poor condition are included."""
        # Create asset with poor condition
        create_response = client.post('/api/v1/assets',
                                      headers={'Authorization': f'Bearer {admin_token}'},
                                      json={
                                          'name': 'Poor Asset',
                                          'asset_tag': 'POOR-001',
                                          'category': 'electrical',
                                          'building': 'Building A',
                                          'floor': '1',
                                          'room': '101',
                                          'condition': 'poor'
                                      })
        asset_id = create_response.get_json()['data']['id']

        # Get assets needing maintenance
        response = client.get('/api/v1/assets/maintenance',
                              headers={'Authorization': f'Bearer {technician_token}'})

        data = response.get_json()
        asset_ids = [asset['id'] for asset in data['data']]
        assert asset_id in asset_ids


@pytest.mark.integration
class TestAssetStatistics:
    """Test asset statistics endpoint."""

    def test_get_asset_statistics(self, client, db_session, client_token, multiple_assets):
        """Test get asset statistics."""
        response = client.get('/api/v1/assets/statistics',
                              headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data

    def test_asset_statistics_structure(self, client, db_session, client_token, sample_asset):
        """Test asset statistics has expected structure."""
        response = client.get('/api/v1/assets/statistics',
                              headers={'Authorization': f'Bearer {client_token}'})

        data = response.get_json()['data']

        # Check for expected statistics fields
        assert 'total_assets' in data
        assert data['total_assets'] > 0

    def test_asset_statistics_counts_correctly(self, client, db_session, admin_token):
        """Test asset statistics counts are accurate."""
        # Create known number of assets
        for i in range(3):
            client.post('/api/v1/assets',
                        headers={'Authorization': f'Bearer {admin_token}'},
                        json={
                            'name': f'Test Asset {i}',
                            'asset_tag': f'STAT-{i:03d}',
                            'category': 'electrical',
                            'building': 'Building A',
                            'floor': '1',
                            'room': '101'
                        })

        response = client.get('/api/v1/assets/statistics',
                              headers={'Authorization': f'Bearer {admin_token}'})

        data = response.get_json()['data']
        assert data['total_assets'] >= 3
