"""
Role Repository
Data access layer for roles
"""
from app.models.role import Role
from app.models.permission import Permission
from app.database import db


class RoleRepository:
    """Repository for role data access operations"""

    def __init__(self):
        self.model = Role

    def get_all(self):
        """Get all roles"""
        return self.model.query.order_by(self.model.name).all()

    def get_by_id(self, role_id):
        """Get role by ID"""
        return self.model.query.get(role_id)

    def get_by_name(self, name):
        """Get role by name"""
        return self.model.query.filter_by(name=name).first()

    def get_system_roles(self):
        """Get all system roles (cannot be deleted)"""
        return self.model.query.filter_by(is_system=True).all()

    def get_custom_roles(self):
        """Get all custom roles (can be deleted)"""
        return self.model.query.filter_by(is_system=False).all()

    def create(self, data):
        """
        Create new role

        Args:
            data (dict): Role data

        Returns:
            Role: Created role
        """
        role = self.model(
            name=data.get('name'),
            description=data.get('description'),
            is_system=data.get('is_system', False)
        )

        db.session.add(role)
        db.session.commit()
        return role

    def update(self, role_id, data):
        """
        Update role

        Args:
            role_id (int): Role ID
            data (dict): Updated data

        Returns:
            Role: Updated role or None
        """
        role = self.get_by_id(role_id)
        if not role:
            return None

        # Update fields
        if 'name' in data:
            role.name = data['name']
        if 'description' in data:
            role.description = data['description']
        # Note: is_system cannot be changed after creation for security

        db.session.commit()
        return role

    def delete(self, role_id):
        """
        Delete role (only if not system role)

        Args:
            role_id (int): Role ID

        Returns:
            bool: True if deleted, False if not found or system role
        """
        role = self.get_by_id(role_id)
        if not role or role.is_system:
            return False

        db.session.delete(role)
        db.session.commit()
        return True

    def add_permission(self, role_id, permission_id):
        """
        Add permission to role

        Args:
            role_id (int): Role ID
            permission_id (int): Permission ID

        Returns:
            bool: True if added, False if failed
        """
        role = self.get_by_id(role_id)
        permission = Permission.query.get(permission_id)

        if not role or not permission:
            return False

        role.add_permission(permission)
        db.session.commit()
        return True

    def remove_permission(self, role_id, permission_id):
        """
        Remove permission from role

        Args:
            role_id (int): Role ID
            permission_id (int): Permission ID

        Returns:
            bool: True if removed, False if failed
        """
        role = self.get_by_id(role_id)
        permission = Permission.query.get(permission_id)

        if not role or not permission:
            return False

        role.remove_permission(permission)
        db.session.commit()
        return True

    def set_permissions(self, role_id, permission_ids):
        """
        Set role permissions (replaces all existing)

        Args:
            role_id (int): Role ID
            permission_ids (list): List of permission IDs

        Returns:
            Role: Updated role or None
        """
        role = self.get_by_id(role_id)
        if not role:
            return None

        # Clear existing permissions
        role.permissions.clear()

        # Add new permissions
        permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
        role.permissions.extend(permissions)

        db.session.commit()
        return role

    def get_role_permissions(self, role_id):
        """
        Get all permissions for a role

        Args:
            role_id (int): Role ID

        Returns:
            list: List of Permission objects
        """
        role = self.get_by_id(role_id)
        return role.permissions if role else []

    def bulk_create(self, roles_data):
        """
        Create multiple roles at once

        Args:
            roles_data (list): List of role dicts

        Returns:
            list: Created roles
        """
        roles = []
        for data in roles_data:
            # Check if role already exists
            existing = self.get_by_name(data['name'])
            if not existing:
                role = self.model(
                    name=data['name'],
                    description=data.get('description', ''),
                    is_system=data.get('is_system', False)
                )
                roles.append(role)
                db.session.add(role)

        db.session.commit()
        return roles

    def exists(self, name):
        """Check if role exists by name"""
        return self.get_by_name(name) is not None

    def count(self):
        """Get total count of roles"""
        return self.model.query.count()

    def get_users_with_role(self, role_id):
        """
        Get all users that have this role

        Args:
            role_id (int): Role ID

        Returns:
            list: List of User objects
        """
        role = self.get_by_id(role_id)
        return role.users if role else []
