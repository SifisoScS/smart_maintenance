"""
Unit tests for PermissionService.

Tests permission creation, retrieval, updating, and checking logic.
"""

import pytest
from app.services.permission_service import PermissionService
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User, UserRole


class TestPermissionService:
    """Test suite for PermissionService."""

    def test_create_permission(self, db_session):
        """Test creating a new permission."""
        service = PermissionService()

        result = service.create_permission({
            'name': 'test_permission',
            'description': 'Test permission',
            'resource': 'test_resource',
            'action': 'test_action'
        })

        assert result['success'] is True
        assert 'data' in result
        assert result['data']['name'] == 'test_permission'
        assert result['data']['description'] == 'Test permission'
        assert result['data']['resource'] == 'test_resource'
        assert result['data']['action'] == 'test_action'

    def test_create_permission_duplicate_name(self, db_session, sample_permissions):
        """Test that creating a permission with duplicate name fails."""
        service = PermissionService()

        result = service.create_permission({
            'name': 'view_requests',
            'description': 'Duplicate',
            'resource': 'requests',
            'action': 'view'
        })

        assert result['success'] is False
        assert 'already exists' in result['error']

    def test_get_all_permissions(self, db_session, sample_permissions):
        """Test retrieving all permissions."""
        service = PermissionService()

        result = service.get_all_permissions()

        assert result['success'] is True
        assert 'data' in result
        assert result['total'] == 9  # sample_permissions creates 9
        assert len(result['data']) == 9

    def test_get_permission_by_id(self, db_session, sample_permissions):
        """Test retrieving permission by ID."""
        service = PermissionService()

        result = service.get_permission_by_id(sample_permissions[0].id)

        assert result['success'] is True
        assert 'data' in result
        assert result['data']['id'] == sample_permissions[0].id
        assert result['data']['name'] == sample_permissions[0].name

    def test_get_permission_by_id_not_found(self, db_session):
        """Test retrieving non-existent permission."""
        service = PermissionService()

        result = service.get_permission_by_id(99999)

        assert result['success'] is False
        assert 'not found' in result['error'].lower()

    def test_get_permission_by_name(self, db_session, sample_permissions):
        """Test retrieving permission by name."""
        service = PermissionService()

        result = service.get_permission_by_name('view_requests')

        assert result['success'] is True
        assert 'data' in result
        assert result['data']['name'] == 'view_requests'
        assert result['data']['resource'] == 'requests'
        assert result['data']['action'] == 'view'

    def test_get_permission_by_name_not_found(self, db_session):
        """Test retrieving non-existent permission by name."""
        service = PermissionService()

        result = service.get_permission_by_name('nonexistent_permission')

        assert result['success'] is False
        assert 'not found' in result['error'].lower()

    def test_update_permission(self, db_session, sample_permissions):
        """Test updating a permission."""
        service = PermissionService()
        permission = sample_permissions[0]

        result = service.update_permission(
            permission.id,
            {'description': 'Updated description'}
        )

        assert result['success'] is True
        assert 'data' in result
        assert result['data']['description'] == 'Updated description'
        assert result['data']['name'] == permission.name  # Unchanged

    def test_update_permission_not_found(self, db_session):
        """Test updating non-existent permission."""
        service = PermissionService()

        result = service.update_permission(99999, {'description': 'New description'})

        assert result['success'] is False
        assert 'not found' in result['error'].lower()

    def test_delete_permission(self, db_session, sample_permissions):
        """Test deleting a permission."""
        service = PermissionService()
        permission_id = sample_permissions[0].id

        result = service.delete_permission(permission_id)

        assert result['success'] is True

        # Verify deletion
        check = service.get_permission_by_id(permission_id)
        assert check['success'] is False

    def test_delete_permission_not_found(self, db_session):
        """Test deleting non-existent permission."""
        service = PermissionService()

        result = service.delete_permission(99999)

        assert result['success'] is False

    def test_get_permissions_grouped(self, db_session, sample_permissions):
        """Test getting permissions grouped by resource."""
        service = PermissionService()

        result = service.get_permissions_grouped()

        assert result['success'] is True
        assert 'data' in result

        grouped = result['data']
        assert 'requests' in grouped
        assert 'assets' in grouped
        assert 'users' in grouped
        assert 'roles' in grouped

        # Check that request permissions are grouped correctly
        request_perms = grouped['requests']
        assert len(request_perms) >= 4  # view, create, edit, delete
        assert all(p['resource'] == 'requests' for p in request_perms)

    def test_user_has_permission_via_role(self, db_session, user_with_roles, sample_permissions):
        """Test checking if user has permission through assigned role."""
        service = PermissionService()

        # user_with_roles has sample_role which includes first 3 permissions
        result = service.check_user_permission(user_with_roles.id, 'view_requests')

        assert result['success'] is True
        assert result['has_permission'] is True

    def test_user_has_permission_not_assigned(self, db_session, sample_user, sample_permissions):
        """Test user without permission."""
        service = PermissionService()

        # sample_user has no roles assigned
        result = service.check_user_permission(sample_user.id, 'view_requests')

        assert result['success'] is True
        assert result['has_permission'] is False

    def test_user_has_permission_invalid_user(self, db_session):
        """Test checking permission for non-existent user."""
        service = PermissionService()

        result = service.check_user_permission(99999, 'view_requests')

        assert result['success'] is False

    def test_get_user_permissions(self, db_session, user_with_roles, sample_role, sample_system_role):
        """Test getting all permissions for a user."""
        service = PermissionService()

        result = service.get_user_permissions(user_with_roles.id)

        # user_with_roles has both sample_role (3 perms) and sample_system_role (all 9 perms)
        # Should get unique set of all permissions
        assert result['success'] is True
        assert 'data' in result
        assert result['total'] == 9
        assert len(result['data']) == 9

    def test_get_user_permissions_no_roles(self, db_session, sample_user):
        """Test getting permissions for user with no roles."""
        service = PermissionService()

        result = service.get_user_permissions(sample_user.id)

        assert result['success'] is True
        assert result['total'] == 0

    def test_get_user_permissions_invalid_user(self, db_session):
        """Test getting permissions for non-existent user."""
        service = PermissionService()

        result = service.get_user_permissions(99999)

        assert result['success'] is False

    def test_create_permission_validates_required_fields(self, db_session):
        """Test that creating permission validates required fields."""
        service = PermissionService()

        result = service.create_permission({
            'name': '',  # Empty name should fail
            'description': 'Test',
            'resource': 'test',
            'action': 'test'
        })

        assert result['success'] is False
        assert 'required' in result['error'].lower()

    def test_create_permission_validates_resource_field(self, db_session):
        """Test that resource field is required."""
        service = PermissionService()

        result = service.create_permission({
            'name': 'test_perm',
            'description': 'Test',
            'action': 'test'
            # Missing resource
        })

        assert result['success'] is False
        assert 'required' in result['error'].lower()

    def test_create_permission_validates_action_field(self, db_session):
        """Test that action field is required."""
        service = PermissionService()

        result = service.create_permission({
            'name': 'test_perm',
            'description': 'Test',
            'resource': 'test'
            # Missing action
        })

        assert result['success'] is False
        assert 'required' in result['error'].lower()

    def test_multiple_users_same_permission(self, db_session, sample_role, sample_permissions):
        """Test that multiple users can have the same permission through roles."""
        service = PermissionService()

        # Create two users with same role
        user1 = User(
            email='user1@test.com',
            first_name='User',
            last_name='One',
            role=UserRole.CLIENT,
            is_active=True
        )
        user1.set_password('password')
        user1.roles.append(sample_role)

        user2 = User(
            email='user2@test.com',
            first_name='User',
            last_name='Two',
            role=UserRole.CLIENT,
            is_active=True
        )
        user2.set_password('password')
        user2.roles.append(sample_role)

        db_session.session.add_all([user1, user2])
        db_session.session.commit()

        # Both should have the same permissions
        result1 = service.get_user_permissions(user1.id)
        result2 = service.get_user_permissions(user2.id)

        assert result1['success'] is True
        assert result2['success'] is True
        assert result1['total'] == result2['total'] == 3

    def test_user_permission_through_multiple_roles(self, db_session, user_with_roles):
        """Test that user gets permissions from all assigned roles."""
        service = PermissionService()

        # user_with_roles has both sample_role and sample_system_role
        # Should have union of all permissions (no duplicates)
        result = service.get_user_permissions(user_with_roles.id)

        assert result['success'] is True
        assert result['total'] == 9
        # Check uniqueness by comparing list length to set of permission names
        perm_names = [p for p in result['data']]
        assert len(perm_names) == len(set(perm_names))
