"""
Permission Repository
Data access layer for permissions
"""
from app.models.permission import Permission
from app.database import db


class PermissionRepository:
    """Repository for permission data access operations"""

    def __init__(self):
        self.model = Permission

    def get_all(self):
        """Get all permissions"""
        return self.model.query.order_by(self.model.resource, self.model.action).all()

    def get_by_id(self, permission_id):
        """Get permission by ID"""
        return self.model.query.get(permission_id)

    def get_by_name(self, name):
        """Get permission by name"""
        return self.model.query.filter_by(name=name).first()

    def get_by_resource(self, resource):
        """Get all permissions for a resource"""
        return self.model.query.filter_by(resource=resource).all()

    def get_by_action(self, action):
        """Get all permissions for an action"""
        return self.model.query.filter_by(action=action).all()

    def get_by_resource_and_action(self, resource, action):
        """Get permission by resource and action"""
        return self.model.query.filter_by(resource=resource, action=action).first()

    def create(self, data):
        """
        Create new permission

        Args:
            data (dict): Permission data

        Returns:
            Permission: Created permission
        """
        permission = self.model(
            name=data.get('name'),
            description=data.get('description'),
            resource=data.get('resource'),
            action=data.get('action')
        )

        db.session.add(permission)
        db.session.commit()
        return permission

    def update(self, permission_id, data):
        """
        Update permission

        Args:
            permission_id (int): Permission ID
            data (dict): Updated data

        Returns:
            Permission: Updated permission or None
        """
        permission = self.get_by_id(permission_id)
        if not permission:
            return None

        # Update fields
        if 'description' in data:
            permission.description = data['description']
        if 'resource' in data:
            permission.resource = data['resource']
        if 'action' in data:
            permission.action = data['action']

        db.session.commit()
        return permission

    def delete(self, permission_id):
        """
        Delete permission

        Args:
            permission_id (int): Permission ID

        Returns:
            bool: True if deleted, False if not found
        """
        permission = self.get_by_id(permission_id)
        if not permission:
            return False

        db.session.delete(permission)
        db.session.commit()
        return True

    def bulk_create(self, permissions_data):
        """
        Create multiple permissions at once

        Args:
            permissions_data (list): List of permission dicts

        Returns:
            list: Created permissions
        """
        permissions = []
        for data in permissions_data:
            # Check if permission already exists
            existing = self.get_by_name(data['name'])
            if not existing:
                permission = self.model(
                    name=data['name'],
                    description=data.get('description', ''),
                    resource=data['resource'],
                    action=data['action']
                )
                permissions.append(permission)
                db.session.add(permission)

        db.session.commit()
        return permissions

    def exists(self, name):
        """Check if permission exists by name"""
        return self.get_by_name(name) is not None

    def count(self):
        """Get total count of permissions"""
        return self.model.query.count()

    def get_grouped_by_resource(self):
        """
        Get permissions grouped by resource

        Returns:
            dict: {resource_name: [permissions]}
        """
        permissions = self.get_all()
        grouped = {}
        for perm in permissions:
            if perm.resource not in grouped:
                grouped[perm.resource] = []
            grouped[perm.resource].append(perm)
        return grouped
