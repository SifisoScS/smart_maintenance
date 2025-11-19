"""
Role Service
Business logic for role management
"""
from app.repositories.role_repository import RoleRepository
from app.repositories.permission_repository import PermissionRepository
from app.repositories.user_repository import UserRepository


class RoleService:
    """Service for role-related business logic"""

    def __init__(self, role_repo=None, permission_repo=None, user_repo=None):
        """
        Initialize service with repositories

        Args:
            role_repo (RoleRepository): Role repository
            permission_repo (PermissionRepository): Permission repository
            user_repo (UserRepository): User repository
        """
        self.role_repo = role_repo or RoleRepository()
        self.permission_repo = permission_repo or PermissionRepository()
        self.user_repo = user_repo or UserRepository()

    def get_all_roles(self, include_permissions=False, include_users=False):
        """
        Get all roles

        Args:
            include_permissions (bool): Include permissions in response
            include_users (bool): Include users in response

        Returns:
            dict: Response with roles
        """
        try:
            roles = self.role_repo.get_all()
            return {
                'success': True,
                'data': [r.to_dict(include_permissions, include_users) for r in roles],
                'total': len(roles)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to retrieve roles: {str(e)}"
            }

    def get_role_by_id(self, role_id, include_permissions=False, include_users=False):
        """
        Get role by ID

        Args:
            role_id (int): Role ID
            include_permissions (bool): Include permissions
            include_users (bool): Include users

        Returns:
            dict: Response with role
        """
        try:
            role = self.role_repo.get_by_id(role_id)
            if not role:
                return {
                    'success': False,
                    'error': 'Role not found'
                }

            return {
                'success': True,
                'data': role.to_dict(include_permissions, include_users)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to retrieve role: {str(e)}"
            }

    def get_role_by_name(self, name, include_permissions=False):
        """
        Get role by name

        Args:
            name (str): Role name
            include_permissions (bool): Include permissions

        Returns:
            dict: Response with role
        """
        try:
            role = self.role_repo.get_by_name(name)
            if not role:
                return {
                    'success': False,
                    'error': 'Role not found'
                }

            return {
                'success': True,
                'data': role.to_dict(include_permissions)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to retrieve role: {str(e)}"
            }

    def create_role(self, data):
        """
        Create new role

        Args:
            data (dict): Role data (name, description, permission_ids)

        Returns:
            dict: Response with created role
        """
        try:
            # Validate required fields
            if not data.get('name'):
                return {
                    'success': False,
                    'error': 'Role name is required'
                }

            # Check if role already exists
            if self.role_repo.exists(data['name']):
                return {
                    'success': False,
                    'error': f"Role '{data['name']}' already exists"
                }

            # Create role
            role = self.role_repo.create({
                'name': data['name'],
                'description': data.get('description', ''),
                'is_system': False  # Custom roles are never system roles
            })

            # Add permissions if provided
            if data.get('permission_ids'):
                self.role_repo.set_permissions(role.id, data['permission_ids'])
                # Refresh role to get updated permissions
                role = self.role_repo.get_by_id(role.id)

            return {
                'success': True,
                'data': role.to_dict(include_permissions=True),
                'message': 'Role created successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to create role: {str(e)}"
            }

    def update_role(self, role_id, data):
        """
        Update role

        Args:
            role_id (int): Role ID
            data (dict): Updated data (name, description, permission_ids)

        Returns:
            dict: Response with updated role
        """
        try:
            # Check if role exists
            role = self.role_repo.get_by_id(role_id)
            if not role:
                return {
                    'success': False,
                    'error': 'Role not found'
                }

            # Update basic info
            if 'name' in data or 'description' in data:
                role = self.role_repo.update(role_id, {
                    'name': data.get('name'),
                    'description': data.get('description')
                })

            # Update permissions if provided
            if 'permission_ids' in data:
                self.role_repo.set_permissions(role_id, data['permission_ids'])
                # Refresh role to get updated permissions
                role = self.role_repo.get_by_id(role_id)

            return {
                'success': True,
                'data': role.to_dict(include_permissions=True),
                'message': 'Role updated successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to update role: {str(e)}"
            }

    def delete_role(self, role_id):
        """
        Delete role (only if not system role)

        Args:
            role_id (int): Role ID

        Returns:
            dict: Response
        """
        try:
            role = self.role_repo.get_by_id(role_id)
            if not role:
                return {
                    'success': False,
                    'error': 'Role not found'
                }

            if role.is_system:
                return {
                    'success': False,
                    'error': 'System roles cannot be deleted'
                }

            success = self.role_repo.delete(role_id)
            if not success:
                return {
                    'success': False,
                    'error': 'Failed to delete role'
                }

            return {
                'success': True,
                'message': 'Role deleted successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to delete role: {str(e)}"
            }

    def add_permission_to_role(self, role_id, permission_id):
        """
        Add permission to role

        Args:
            role_id (int): Role ID
            permission_id (int): Permission ID

        Returns:
            dict: Response
        """
        try:
            success = self.role_repo.add_permission(role_id, permission_id)
            if not success:
                return {
                    'success': False,
                    'error': 'Role or permission not found'
                }

            role = self.role_repo.get_by_id(role_id)
            return {
                'success': True,
                'data': role.to_dict(include_permissions=True),
                'message': 'Permission added to role successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to add permission: {str(e)}"
            }

    def remove_permission_from_role(self, role_id, permission_id):
        """
        Remove permission from role

        Args:
            role_id (int): Role ID
            permission_id (int): Permission ID

        Returns:
            dict: Response
        """
        try:
            success = self.role_repo.remove_permission(role_id, permission_id)
            if not success:
                return {
                    'success': False,
                    'error': 'Role or permission not found'
                }

            role = self.role_repo.get_by_id(role_id)
            return {
                'success': True,
                'data': role.to_dict(include_permissions=True),
                'message': 'Permission removed from role successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to remove permission: {str(e)}"
            }

    def assign_role_to_user(self, user_id, role_id):
        """
        Assign role to user

        Args:
            user_id (int): User ID
            role_id (int): Role ID

        Returns:
            dict: Response
        """
        try:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            role = self.role_repo.get_by_id(role_id)
            if not role:
                return {
                    'success': False,
                    'error': 'Role not found'
                }

            user.assign_role(role)
            from app.database import db
            db.session.commit()

            return {
                'success': True,
                'message': f"Role '{role.name}' assigned to user successfully"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to assign role: {str(e)}"
            }

    def remove_role_from_user(self, user_id, role_id):
        """
        Remove role from user

        Args:
            user_id (int): User ID
            role_id (int): Role ID

        Returns:
            dict: Response
        """
        try:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            role = self.role_repo.get_by_id(role_id)
            if not role:
                return {
                    'success': False,
                    'error': 'Role not found'
                }

            user.remove_role(role)
            from app.database import db
            db.session.commit()

            return {
                'success': True,
                'message': f"Role '{role.name}' removed from user successfully"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to remove role: {str(e)}"
            }

    def get_user_roles(self, user_id):
        """
        Get all roles assigned to user

        Args:
            user_id (int): User ID

        Returns:
            dict: Response with user roles
        """
        try:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            return {
                'success': True,
                'data': [r.to_dict(include_permissions=True) for r in user.roles],
                'total': len(user.roles)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to retrieve user roles: {str(e)}"
            }

    def get_role_users(self, role_id):
        """
        Get all users with specific role

        Args:
            role_id (int): Role ID

        Returns:
            dict: Response with users
        """
        try:
            users = self.role_repo.get_users_with_role(role_id)
            return {
                'success': True,
                'data': [{'id': u.id, 'email': u.email, 'full_name': u.full_name} for u in users],
                'total': len(users)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to retrieve role users: {str(e)}"
            }
