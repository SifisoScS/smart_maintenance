"""
Unit tests for RoleService.

Tests role creation, retrieval, updating, deletion, permission management, and user assignment.
"""

import pytest
from app.services.role_service import RoleService
from app.models.role import Role
from app.models.permission import Permission
from app.models.user import User, UserRole


class TestRoleService:
    """Test suite for RoleService."""

    def test_create_role(self, db_session):
        """Test creating a new role."""
        service = RoleService()

        result = service.create_role({
            'name': 'Test Role',
            'description': 'A test role for testing'
        })

        assert result['success'] is True
        assert 'data' in result
        assert result['data']['name'] == 'Test Role'
        assert result['data']['description'] == 'A test role for testing'
        assert result['data']['is_system'] is False

    def test_create_role_with_permissions(self, db_session, sample_permissions):
        """Test creating role with initial permissions."""
        service = RoleService()

        result = service.create_role({
            'name': 'Role With Perms',
            'description': 'Test',
            'permission_ids': [sample_permissions[0].id, sample_permissions[1].id]
        })

        assert result['success'] is True
        assert len(result['data']['permissions']) == 2

    def test_create_role_duplicate_name(self, db_session, sample_role):
        """Test that creating a role with duplicate name fails."""
        service = RoleService()

        result = service.create_role({
            'name': sample_role.name,
            'description': 'Duplicate'
        })

        assert result['success'] is False
        assert 'already exists' in result['error']

    def test_create_role_missing_name(self, db_session):
        """Test that name is required."""
        service = RoleService()

        result = service.create_role({
            'description': 'Missing name'
        })

        assert result['success'] is False
        assert 'required' in result['error'].lower()

    def test_get_all_roles(self, db_session, sample_role, sample_system_role):
        """Test retrieving all roles."""
        service = RoleService()

        result = service.get_all_roles()

        assert result['success'] is True
        assert 'data' in result
        assert result['total'] >= 2

    def test_get_all_roles_with_permissions(self, db_session, sample_role):
        """Test retrieving roles with permissions included."""
        service = RoleService()

        result = service.get_all_roles(include_permissions=True)

        assert result['success'] is True
        # Find our sample role
        test_role = next((r for r in result['data'] if r['id'] == sample_role.id), None)
        assert test_role is not None
        assert 'permissions' in test_role
        assert len(test_role['permissions']) == 3

    def test_get_role_by_id(self, db_session, sample_role):
        """Test retrieving role by ID."""
        service = RoleService()

        result = service.get_role_by_id(sample_role.id)

        assert result['success'] is True
        assert 'data' in result
        assert result['data']['id'] == sample_role.id
        assert result['data']['name'] == sample_role.name

    def test_get_role_by_id_not_found(self, db_session):
        """Test retrieving non-existent role."""
        service = RoleService()

        result = service.get_role_by_id(99999)

        assert result['success'] is False
        assert 'not found' in result['error'].lower()

    def test_get_role_by_id_with_permissions(self, db_session, sample_role):
        """Test retrieving role with permissions."""
        service = RoleService()

        result = service.get_role_by_id(sample_role.id, include_permissions=True)

        assert result['success'] is True
        assert 'permissions' in result['data']
        assert len(result['data']['permissions']) == 3

    def test_get_role_by_name(self, db_session, sample_role):
        """Test retrieving role by name."""
        service = RoleService()

        result = service.get_role_by_name(sample_role.name)

        assert result['success'] is True
        assert 'data' in result
        assert result['data']['name'] == sample_role.name

    def test_get_role_by_name_not_found(self, db_session):
        """Test retrieving non-existent role by name."""
        service = RoleService()

        result = service.get_role_by_name('Nonexistent Role')

        assert result['success'] is False
        assert 'not found' in result['error'].lower()

    def test_update_role_name(self, db_session, sample_role):
        """Test updating role name."""
        service = RoleService()

        result = service.update_role(sample_role.id, {
            'name': 'Updated Role Name'
        })

        assert result['success'] is True
        assert result['data']['name'] == 'Updated Role Name'

    def test_update_role_description(self, db_session, sample_role):
        """Test updating role description."""
        service = RoleService()
        original_name = sample_role.name

        result = service.update_role(sample_role.id, {
            'name': original_name,  # Must include name to avoid None
            'description': 'Updated description'
        })

        assert result['success'] is True
        assert result['data']['description'] == 'Updated description'
        assert result['data']['name'] == original_name

    def test_update_role_permissions(self, db_session, sample_role, sample_permissions):
        """Test updating role permissions."""
        service = RoleService()

        # Update to have all permissions
        new_perm_ids = [p.id for p in sample_permissions]
        result = service.update_role(sample_role.id, {
            'permission_ids': new_perm_ids
        })

        assert result['success'] is True
        assert len(result['data']['permissions']) == 9

    def test_update_role_not_found(self, db_session):
        """Test updating non-existent role."""
        service = RoleService()

        result = service.update_role(99999, {'name': 'New Name'})

        assert result['success'] is False
        assert 'not found' in result['error'].lower()

    def test_delete_role(self, db_session, sample_role):
        """Test deleting a custom role."""
        service = RoleService()
        role_id = sample_role.id

        result = service.delete_role(role_id)

        assert result['success'] is True

        # Verify deletion
        check = service.get_role_by_id(role_id)
        assert check['success'] is False

    def test_delete_system_role_forbidden(self, db_session, sample_system_role):
        """Test that system roles cannot be deleted."""
        service = RoleService()

        result = service.delete_role(sample_system_role.id)

        assert result['success'] is False
        assert 'system' in result['error'].lower()

    def test_delete_role_not_found(self, db_session):
        """Test deleting non-existent role."""
        service = RoleService()

        result = service.delete_role(99999)

        assert result['success'] is False

    def test_add_permission_to_role(self, db_session, sample_permissions):
        """Test adding permission to role."""
        service = RoleService()

        # Create a role without permissions
        create_result = service.create_role({
            'name': 'Empty Role',
            'description': 'Role with no permissions'
        })
        role_id = create_result['data']['id']

        # Add a permission
        result = service.add_permission_to_role(role_id, sample_permissions[0].id)

        assert result['success'] is True
        assert len(result['data']['permissions']) == 1

    def test_add_permission_to_role_not_found(self, db_session):
        """Test adding permission to non-existent role."""
        service = RoleService()

        result = service.add_permission_to_role(99999, 1)

        assert result['success'] is False

    def test_remove_permission_from_role(self, db_session, sample_role, sample_permissions):
        """Test removing permission from role."""
        service = RoleService()

        # Remove first permission
        result = service.remove_permission_from_role(sample_role.id, sample_permissions[0].id)

        assert result['success'] is True
        assert len(result['data']['permissions']) == 2

    def test_remove_permission_from_role_not_found(self, db_session):
        """Test removing permission from non-existent role."""
        service = RoleService()

        result = service.remove_permission_from_role(99999, 1)

        assert result['success'] is False

    def test_assign_role_to_user(self, db_session, sample_user, sample_role):
        """Test assigning role to user."""
        service = RoleService()

        result = service.assign_role_to_user(sample_user.id, sample_role.id)

        assert result['success'] is True
        assert sample_role.name in result['message']

        # Verify assignment
        user_roles = service.get_user_roles(sample_user.id)
        assert len(user_roles['data']) == 1
        assert user_roles['data'][0]['id'] == sample_role.id

    def test_assign_role_user_not_found(self, db_session, sample_role):
        """Test assigning role to non-existent user."""
        service = RoleService()

        result = service.assign_role_to_user(99999, sample_role.id)

        assert result['success'] is False
        assert 'user not found' in result['error'].lower()

    def test_assign_role_role_not_found(self, db_session, sample_user):
        """Test assigning non-existent role to user."""
        service = RoleService()

        result = service.assign_role_to_user(sample_user.id, 99999)

        assert result['success'] is False
        assert 'role not found' in result['error'].lower()

    def test_remove_role_from_user(self, db_session, user_with_roles, sample_role):
        """Test removing role from user."""
        service = RoleService()

        # user_with_roles has sample_role assigned
        result = service.remove_role_from_user(user_with_roles.id, sample_role.id)

        assert result['success'] is True

        # Verify removal
        user_roles = service.get_user_roles(user_with_roles.id)
        role_ids = [r['id'] for r in user_roles['data']]
        assert sample_role.id not in role_ids

    def test_remove_role_from_user_not_found(self, db_session, sample_role):
        """Test removing role from non-existent user."""
        service = RoleService()

        result = service.remove_role_from_user(99999, sample_role.id)

        assert result['success'] is False

    def test_get_user_roles(self, db_session, user_with_roles):
        """Test getting all roles for a user."""
        service = RoleService()

        result = service.get_user_roles(user_with_roles.id)

        assert result['success'] is True
        assert 'data' in result
        assert result['total'] == 2
        # Roles should include permissions
        assert 'permissions' in result['data'][0]

    def test_get_user_roles_no_roles(self, db_session, sample_user):
        """Test getting roles for user with no roles."""
        service = RoleService()

        result = service.get_user_roles(sample_user.id)

        assert result['success'] is True
        assert result['total'] == 0

    def test_get_user_roles_user_not_found(self, db_session):
        """Test getting roles for non-existent user."""
        service = RoleService()

        result = service.get_user_roles(99999)

        assert result['success'] is False

    def test_get_role_users(self, db_session, user_with_roles, sample_role):
        """Test getting all users with a specific role."""
        service = RoleService()

        result = service.get_role_users(sample_role.id)

        assert result['success'] is True
        assert 'data' in result
        assert result['total'] >= 1

        # Check that user_with_roles is in the list
        user_ids = [u['id'] for u in result['data']]
        assert user_with_roles.id in user_ids

    def test_get_role_users_empty(self, db_session):
        """Test getting users for a role with no users."""
        service = RoleService()

        # Create role without users
        create_result = service.create_role({
            'name': 'Empty Role',
            'description': 'No users'
        })
        role_id = create_result['data']['id']

        result = service.get_role_users(role_id)

        assert result['success'] is True
        assert result['total'] == 0

    def test_multiple_users_same_role(self, db_session, sample_role):
        """Test assigning same role to multiple users."""
        service = RoleService()

        # Create two users
        user1 = User(
            email='multi1@test.com',
            first_name='Multi',
            last_name='One',
            role=UserRole.CLIENT,
            is_active=True
        )
        user1.set_password('password')

        user2 = User(
            email='multi2@test.com',
            first_name='Multi',
            last_name='Two',
            role=UserRole.CLIENT,
            is_active=True
        )
        user2.set_password('password')

        db_session.session.add_all([user1, user2])
        db_session.session.commit()

        # Assign same role to both
        result1 = service.assign_role_to_user(user1.id, sample_role.id)
        result2 = service.assign_role_to_user(user2.id, sample_role.id)

        assert result1['success'] is True
        assert result2['success'] is True

        # Check role users
        role_users = service.get_role_users(sample_role.id)
        user_ids = [u['id'] for u in role_users['data']]
        assert user1.id in user_ids
        assert user2.id in user_ids

    def test_user_multiple_roles(self, db_session, sample_user, sample_role, sample_system_role):
        """Test assigning multiple roles to same user."""
        service = RoleService()

        # Assign two roles
        result1 = service.assign_role_to_user(sample_user.id, sample_role.id)
        result2 = service.assign_role_to_user(sample_user.id, sample_system_role.id)

        assert result1['success'] is True
        assert result2['success'] is True

        # Check user roles
        user_roles = service.get_user_roles(sample_user.id)
        assert user_roles['total'] == 2
        role_ids = [r['id'] for r in user_roles['data']]
        assert sample_role.id in role_ids
        assert sample_system_role.id in role_ids

    def test_role_permissions_cascade(self, db_session, sample_role, sample_permissions):
        """Test that permission changes cascade to users."""
        service = RoleService()

        # Create user with role
        user = User(
            email='cascade@test.com',
            first_name='Cascade',
            last_name='Test',
            role=UserRole.CLIENT,
            is_active=True
        )
        user.set_password('password')
        db_session.session.add(user)
        db_session.session.commit()

        service.assign_role_to_user(user.id, sample_role.id)

        # User should have 3 permissions from sample_role
        from app.services.permission_service import PermissionService
        perm_service = PermissionService()
        user_perms_before = perm_service.get_user_permissions(user.id)
        assert user_perms_before['total'] == 3

        # Add more permissions to role
        service.add_permission_to_role(sample_role.id, sample_permissions[3].id)

        # User should now have 4 permissions
        user_perms_after = perm_service.get_user_permissions(user.id)
        assert user_perms_after['total'] == 4

    def test_role_validation_prevents_system_flag_on_create(self, db_session):
        """Test that custom roles cannot be created as system roles."""
        service = RoleService()

        # Even if we pass is_system=True, it should be ignored
        result = service.create_role({
            'name': 'Fake System Role',
            'description': 'Trying to be system',
            'is_system': True  # This should be ignored
        })

        assert result['success'] is True
        assert result['data']['is_system'] is False
