"""
Permission Model
Represents granular permissions for actions on resources
"""
from app.database import db
from datetime import datetime


class Permission(db.Model):
    """
    Permission model for fine-grained access control
    Permissions are actions that can be performed on resources
    """
    __tablename__ = 'permissions'
    __table_args__ = (
        db.UniqueConstraint('name', 'tenant_id', name='uq_permission_name_tenant'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    resource = db.Column(db.String(50), nullable=False)  # 'requests', 'assets', 'users', etc.
    action = db.Column(db.String(50), nullable=False)  # 'view', 'create', 'edit', 'delete'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-Tenancy
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)
    tenant = db.relationship('Tenant', backref='permissions')

    # Relationships
    roles = db.relationship('Role', secondary='role_permissions', back_populates='permissions')

    def __repr__(self):
        return f'<Permission {self.name}>'

    def to_dict(self):
        """Convert permission to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'resource': self.resource,
            'action': self.action,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def generate_permission_name(resource, action):
        """Generate standardized permission name"""
        return f"{action}_{resource}"
