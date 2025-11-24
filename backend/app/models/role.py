"""
Role Model
Represents user roles with associated permissions
"""
from app.database import db
from datetime import datetime


class Role(db.Model):
    """
    Role model for grouping permissions
    Roles can be assigned to users for access control
    """
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    is_system = db.Column(db.Boolean, default=False)  # System roles can't be deleted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-Tenancy
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)
    tenant = db.relationship('Tenant', backref='roles')

    # Relationships
    permissions = db.relationship('Permission', secondary='role_permissions', back_populates='roles')
    users = db.relationship(
        'User',
        secondary='user_roles',
        primaryjoin='Role.id == user_roles.c.role_id',
        secondaryjoin='User.id == user_roles.c.user_id',
        back_populates='roles'
    )

    def __repr__(self):
        return f'<Role {self.name}>'

    def to_dict(self, include_permissions=False, include_users=False):
        """Convert role to dictionary"""
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_system': self.is_system,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_permissions:
            result['permissions'] = [p.to_dict() for p in self.permissions]
            result['permission_count'] = len(self.permissions)

        if include_users:
            result['users'] = [{'id': u.id, 'email': u.email, 'full_name': f"{u.first_name} {u.last_name}"}
                              for u in self.users]
            result['user_count'] = len(self.users)

        return result

    def has_permission(self, permission_name):
        """Check if role has specific permission"""
        return any(p.name == permission_name for p in self.permissions)

    def add_permission(self, permission):
        """Add permission to role"""
        if permission not in self.permissions:
            self.permissions.append(permission)

    def remove_permission(self, permission):
        """Remove permission from role"""
        if permission in self.permissions:
            self.permissions.remove(permission)


# Association table for role-permission many-to-many relationship
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
    db.Column('assigned_at', db.DateTime, default=datetime.utcnow)
)

# Association table for user-role many-to-many relationship
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    db.Column('assigned_at', db.DateTime, default=datetime.utcnow),
    db.Column('assigned_by', db.Integer, db.ForeignKey('users.id'))
)
