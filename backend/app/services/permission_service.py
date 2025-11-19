"""
Permission Service
Business logic for permission management
"""
from app.repositories.permission_repository import PermissionRepository
from app.repositories.user_repository import UserRepository


class PermissionService:
    """Service for permission-related business logic"""

    def __init__(self, permission_repo=None, user_repo=None):
        """
        Initialize service with repositories

        Args:
            permission_repo (PermissionRepository): Permission repository
            user_repo (UserRepository): User repository
        """
        self.permission_repo = permission_repo or PermissionRepository()
        self.user_repo = user_repo or UserRepository()

    def get_all_permissions(self):
        """
        Get all permissions

        Returns:
            dict: Response with permissions
        """
        try:
            permissions = self.permission_repo.get_all()
            return {
                'success': True,
                'data': [p.to_dict() for p in permissions],
                'total': len(permissions)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to retrieve permissions: {str(e)}"
            }

    def get_permission_by_id(self, permission_id):
        """
        Get permission by ID

        Args:
            permission_id (int): Permission ID

        Returns:
            dict: Response with permission
        """
        try:
            permission = self.permission_repo.get_by_id(permission_id)
            if not permission:
                return {
                    'success': False,
                    'error': 'Permission not found'
                }

            return {
                'success': True,
                'data': permission.to_dict()
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to retrieve permission: {str(e)}"
            }

    def get_permission_by_name(self, name):
        """
        Get permission by name

        Args:
            name (str): Permission name

        Returns:
            dict: Response with permission
        """
        try:
            permission = self.permission_repo.get_by_name(name)
            if not permission:
                return {
                    'success': False,
                    'error': 'Permission not found'
                }

            return {
                'success': True,
                'data': permission.to_dict()
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to retrieve permission: {str(e)}"
            }

    def get_permissions_grouped(self):
        """
        Get permissions grouped by resource

        Returns:
            dict: Response with grouped permissions
        """
        try:
            grouped = self.permission_repo.get_grouped_by_resource()
            # Convert to serializable format
            result = {}
            for resource, permissions in grouped.items():
                result[resource] = [p.to_dict() for p in permissions]

            return {
                'success': True,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to retrieve grouped permissions: {str(e)}"
            }

    def create_permission(self, data):
        """
        Create new permission

        Args:
            data (dict): Permission data

        Returns:
            dict: Response with created permission
        """
        try:
            # Validate required fields
            if not data.get('name'):
                return {
                    'success': False,
                    'error': 'Permission name is required'
                }

            if not data.get('resource'):
                return {
                    'success': False,
                    'error': 'Resource is required'
                }

            if not data.get('action'):
                return {
                    'success': False,
                    'error': 'Action is required'
                }

            # Check if permission already exists
            if self.permission_repo.exists(data['name']):
                return {
                    'success': False,
                    'error': f"Permission '{data['name']}' already exists"
                }

            permission = self.permission_repo.create(data)
            return {
                'success': True,
                'data': permission.to_dict(),
                'message': 'Permission created successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to create permission: {str(e)}"
            }

    def update_permission(self, permission_id, data):
        """
        Update permission

        Args:
            permission_id (int): Permission ID
            data (dict): Updated data

        Returns:
            dict: Response with updated permission
        """
        try:
            permission = self.permission_repo.update(permission_id, data)
            if not permission:
                return {
                    'success': False,
                    'error': 'Permission not found'
                }

            return {
                'success': True,
                'data': permission.to_dict(),
                'message': 'Permission updated successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to update permission: {str(e)}"
            }

    def delete_permission(self, permission_id):
        """
        Delete permission

        Args:
            permission_id (int): Permission ID

        Returns:
            dict: Response
        """
        try:
            success = self.permission_repo.delete(permission_id)
            if not success:
                return {
                    'success': False,
                    'error': 'Permission not found'
                }

            return {
                'success': True,
                'message': 'Permission deleted successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to delete permission: {str(e)}"
            }

    def check_user_permission(self, user_id, permission_name):
        """
        Check if user has specific permission

        Args:
            user_id (int): User ID
            permission_name (str): Permission name

        Returns:
            dict: Response with permission check result
        """
        try:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            has_permission = user.has_permission_by_name(permission_name)
            return {
                'success': True,
                'has_permission': has_permission,
                'user_id': user_id,
                'permission': permission_name
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to check permission: {str(e)}"
            }

    def get_user_permissions(self, user_id):
        """
        Get all permissions for user

        Args:
            user_id (int): User ID

        Returns:
            dict: Response with user permissions
        """
        try:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            permissions = user.get_all_permissions()
            return {
                'success': True,
                'data': list(permissions),
                'user_id': user_id,
                'total': len(permissions)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to retrieve user permissions: {str(e)}"
            }
