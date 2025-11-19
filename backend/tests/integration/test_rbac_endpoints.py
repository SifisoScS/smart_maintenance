"""
Integration tests for RBAC API endpoints.

Tests permission and role controllers with full HTTP request/response cycle.
"""

import pytest
import json


class TestPermissionEndpoints:
    """Integration tests for permission endpoints."""

    def test_get_all_permissions(self, client, db_session, admin_permissions_token, sample_permissions):
        """Test GET /api/v1/permissions."""
        response = client.get(
            '/api/v1/permissions',
            headers={'Authorization': f'Bearer {admin_permissions_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert len(data['data']) >= 14  # Updated count

    def test_get_permissions_unauthorized(self, client, db_session, sample_permissions):
        """Test that permissions endpoint requires authentication."""
        response = client.get('/api/v1/permissions')

        assert response.status_code == 401

    def test_get_permissions_forbidden_for_non_admin(self, client, db_session, client_token, sample_permissions):
        """Test that non-admin users cannot access permissions."""
        response = client.get(
            '/api/v1/permissions',
            headers={'Authorization': f'Bearer {client_token}'}
        )

        assert response.status_code == 403

    def test_get_permission_by_id(self, client, db_session, admin_permissions_token, sample_permissions):
        """Test GET /api/v1/permissions/<id>."""
        permission_id = sample_permissions[0].id

        response = client.get(
            f'/api/v1/permissions/{permission_id}',
            headers={'Authorization': f'Bearer {admin_permissions_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['id'] == permission_id

    def test_get_permission_by_id_not_found(self, client, db_session, admin_permissions_token):
        """Test GET /api/v1/permissions/<id> with invalid ID."""
        response = client.get(
            '/api/v1/permissions/99999',
            headers={'Authorization': f'Bearer {admin_permissions_token}'}
        )

        assert response.status_code == 404

    def test_get_permissions_grouped(self, client, db_session, admin_permissions_token, sample_permissions):
        """Test GET /api/v1/permissions/grouped."""
        response = client.get(
            '/api/v1/permissions/grouped',
            headers={'Authorization': f'Bearer {admin_permissions_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'requests' in data['data']
        assert 'assets' in data['data']

    def test_create_permission(self, client, db_session, admin_permissions_token):
        """Test POST /api/v1/permissions."""
        response = client.post(
            '/api/v1/permissions',
            headers={'Authorization': f'Bearer {admin_permissions_token}'},
            json={
                'name': 'test_new_permission',
                'description': 'A new test permission',
                'resource': 'test_resource',
                'action': 'test_action'
            }
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['name'] == 'test_new_permission'

    def test_create_permission_missing_fields(self, client, db_session, admin_permissions_token):
        """Test POST /api/v1/permissions with missing required fields."""
        response = client.post(
            '/api/v1/permissions',
            headers={'Authorization': f'Bearer {admin_permissions_token}'},
            json={
                'name': 'incomplete_permission'
                # Missing resource and action
            }
        )

        assert response.status_code == 400

    def test_check_user_permission(self, client, db_session, admin_permissions_token, user_with_roles):
        """Test POST /api/v1/permissions/check."""
        response = client.post(
            '/api/v1/permissions/check',
            headers={'Authorization': f'Bearer {admin_permissions_token}'},
            json={
                'user_id': user_with_roles.id,
                'permission_name': 'view_requests'
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['has_permission'] is True


class TestRoleEndpoints:
    """Integration tests for role endpoints."""

    def test_get_all_roles(self, client, db_session, admin_permissions_token, sample_role):
        """Test GET /api/v1/roles."""
        response = client.get(
            '/api/v1/roles',
            headers={'Authorization': f'Bearer {admin_permissions_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) >= 1

    def test_get_roles_unauthorized(self, client, db_session):
        """Test that roles endpoint requires authentication."""
        response = client.get('/api/v1/roles')

        assert response.status_code == 401

    def test_get_role_by_id(self, client, db_session, admin_permissions_token, sample_role):
        """Test GET /api/v1/roles/<id>."""
        response = client.get(
            f'/api/v1/roles/{sample_role.id}',
            headers={'Authorization': f'Bearer {admin_permissions_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['id'] == sample_role.id
        assert data['data']['name'] == sample_role.name

    def test_get_role_by_id_not_found(self, client, db_session, admin_permissions_token):
        """Test GET /api/v1/roles/<id> with invalid ID."""
        response = client.get(
            '/api/v1/roles/99999',
            headers={'Authorization': f'Bearer {admin_permissions_token}'}
        )

        assert response.status_code == 404

    def test_create_role(self, client, db_session, admin_permissions_token):
        """Test POST /api/v1/roles."""
        response = client.post(
            '/api/v1/roles',
            headers={'Authorization': f'Bearer {admin_permissions_token}'},
            json={
                'name': 'Test Integration Role',
                'description': 'Created via integration test'
            }
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['name'] == 'Test Integration Role'
        assert data['data']['is_system'] is False

    def test_create_role_with_permissions(self, client, db_session, admin_permissions_token, sample_permissions):
        """Test POST /api/v1/roles with initial permissions."""
        response = client.post(
            '/api/v1/roles',
            headers={'Authorization': f'Bearer {admin_permissions_token}'},
            json={
                'name': 'Role With Permissions',
                'description': 'Test',
                'permission_ids': [sample_permissions[0].id, sample_permissions[1].id]
            }
        )

        assert response.status_code == 201
        data = response.get_json()
        assert len(data['data']['permissions']) == 2

    def test_create_role_duplicate_name(self, client, db_session, admin_permissions_token, sample_role):
        """Test POST /api/v1/roles with duplicate name."""
        response = client.post(
            '/api/v1/roles',
            headers={'Authorization': f'Bearer {admin_permissions_token}'},
            json={
                'name': sample_role.name,
                'description': 'Duplicate'
            }
        )

        assert response.status_code == 400

    def test_update_role(self, client, db_session, admin_permissions_token, sample_role):
        """Test PUT /api/v1/roles/<id>."""
        response = client.put(
            f'/api/v1/roles/{sample_role.id}',
            headers={'Authorization': f'Bearer {admin_permissions_token}'},
            json={
                'name': 'Updated Role Name',
                'description': 'Updated description'
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['name'] == 'Updated Role Name'

    def test_delete_role(self, client, db_session, admin_permissions_token):
        """Test DELETE /api/v1/roles/<id>."""
        # Create a role to delete
        create_response = client.post(
            '/api/v1/roles',
            headers={'Authorization': f'Bearer {admin_permissions_token}'},
            json={'name': 'Role To Delete', 'description': 'Will be deleted'}
        )
        role_id = create_response.get_json()['data']['id']

        # Delete it
        response = client.delete(
            f'/api/v1/roles/{role_id}',
            headers={'Authorization': f'Bearer {admin_permissions_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

        # Verify deletion
        get_response = client.get(
            f'/api/v1/roles/{role_id}',
            headers={'Authorization': f'Bearer {admin_permissions_token}'}
        )
        assert get_response.status_code == 404

    def test_delete_system_role_forbidden(self, client, db_session, admin_permissions_token, sample_system_role):
        """Test that system roles cannot be deleted."""
        response = client.delete(
            f'/api/v1/roles/{sample_system_role.id}',
            headers={'Authorization': f'Bearer {admin_permissions_token}'}
        )

        assert response.status_code == 400

    def test_add_permission_to_role(self, client, db_session, admin_permissions_token, sample_role, sample_permissions):
        """Test POST /api/v1/roles/<id>/permissions."""
        # Add a new permission to role
        response = client.post(
            f'/api/v1/roles/{sample_role.id}/permissions',
            headers={'Authorization': f'Bearer {admin_permissions_token}'},
            json={'permission_id': sample_permissions[3].id}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        # Sample role starts with 3 perms, now should have 4
        assert len(data['data']['permissions']) == 4

    def test_remove_permission_from_role(self, client, db_session, admin_permissions_token, sample_role, sample_permissions):
        """Test DELETE /api/v1/roles/<id>/permissions/<permission_id>."""
        # Remove first permission
        response = client.delete(
            f'/api/v1/roles/{sample_role.id}/permissions/{sample_permissions[0].id}',
            headers={'Authorization': f'Bearer {admin_permissions_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_assign_role_to_user(self, client, db_session, admin_permissions_token, sample_user, sample_role):
        """Test POST /api/v1/users/<id>/roles."""
        response = client.post(
            f'/api/v1/users/{sample_user.id}/roles',
            headers={'Authorization': f'Bearer {admin_permissions_token}'},
            json={'role_id': sample_role.id}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_remove_role_from_user(self, client, db_session, admin_permissions_token, user_with_roles, sample_role):
        """Test DELETE /api/v1/users/<id>/roles/<role_id>."""
        response = client.delete(
            f'/api/v1/users/{user_with_roles.id}/roles/{sample_role.id}',
            headers={'Authorization': f'Bearer {admin_permissions_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_get_user_roles(self, client, db_session, admin_permissions_token, user_with_roles):
        """Test GET /api/v1/users/<id>/roles."""
        response = client.get(
            f'/api/v1/users/{user_with_roles.id}/roles',
            headers={'Authorization': f'Bearer {admin_permissions_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 2  # user_with_roles has 2 roles

    def test_get_role_users(self, client, db_session, admin_permissions_token, sample_role, user_with_roles):
        """Test GET /api/v1/roles/<id>/users."""
        response = client.get(
            f'/api/v1/roles/{sample_role.id}/users',
            headers={'Authorization': f'Bearer {admin_permissions_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) >= 1

    def test_get_user_permissions(self, client, db_session, admin_permissions_token, user_with_roles):
        """Test GET /api/v1/users/<id>/permissions."""
        response = client.get(
            f'/api/v1/users/{user_with_roles.id}/permissions',
            headers={'Authorization': f'Bearer {admin_permissions_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 9  # All unique permissions from both roles
