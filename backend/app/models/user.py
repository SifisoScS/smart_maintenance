"""
User Model with Role-Based Access Control

Demonstrates:
- OOP Encapsulation: Password hashing logic inside model
- Validation: Email format and required fields
- Enum Pattern: Type-safe role management
"""

import re
import bcrypt
from enum import Enum
from app.models.base import BaseModel
from app.database import db


class UserRole(Enum):
    """
    Enumeration for user roles.

    Benefits:
    - Type safety (can't assign invalid role)
    - Clear, predefined options
    - Easy to extend with new roles
    """
    ADMIN = 'admin'
    TECHNICIAN = 'technician'
    CLIENT = 'client'

    @classmethod
    def has_value(cls, value):
        """Check if value is valid role"""
        return value in [role.value for role in cls]


class User(BaseModel):
    """
    User entity with authentication and authorization.

    OOP Principles:
    - Encapsulation: Password hashing is internal, not exposed
    - Single Responsibility: Manages only user data and auth
    - Validation: Self-validates email format and required fields

    Relationships:
    - One user can submit many maintenance requests (as client)
    - One user can be assigned many requests (as technician)
    """

    __tablename__ = 'users'

    # Basic Information
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    # Role-Based Access Control
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.CLIENT)

    # Profile Information
    phone = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(100), nullable=True)

    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships (will be defined when we create MaintenanceRequest model)
    # submitted_requests = relationship with MaintenanceRequest
    # assigned_requests = relationship with MaintenanceRequest

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"

    @property
    def full_name(self):
        """
        Computed property for full name.

        OOP Principle: Encapsulation - Derived data as property
        """
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == UserRole.ADMIN

    @property
    def is_technician(self):
        """Check if user has technician role"""
        return self.role == UserRole.TECHNICIAN

    @property
    def is_client(self):
        """Check if user has client role"""
        return self.role == UserRole.CLIENT

    def set_password(self, password):
        """
        Hash and store password securely.

        Args:
            password (str): Plain text password

        OOP Principle: Encapsulation - External code never sees plaintext passwords
        """
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")

        # Generate salt and hash password
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        """
        Verify password against stored hash.

        Args:
            password (str): Plain text password to check

        Returns:
            bool: True if password matches, False otherwise

        OOP Principle: Encapsulation - Password verification logic internal
        """
        if not password or not self.password_hash:
            return False

        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def validate(self):
        """
        Validate user data.

        Raises:
            ValueError: If validation fails

        OOP Principle: Each model validates itself
        """
        # Email validation
        if not self.email:
            raise ValueError("Email is required")

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.email):
            raise ValueError("Invalid email format")

        # Name validation
        if not self.first_name or not self.first_name.strip():
            raise ValueError("First name is required")

        if not self.last_name or not self.last_name.strip():
            raise ValueError("Last name is required")

        # Role validation
        if not isinstance(self.role, UserRole):
            raise ValueError("Invalid user role")

        # Password validation (must be set before validation)
        if not self.password_hash:
            raise ValueError("Password must be set before creating user")

    def to_dict(self, include_sensitive=False):
        """
        Convert user to dictionary.

        Args:
            include_sensitive (bool): Whether to include sensitive data

        Returns:
            dict: User data

        OOP Principle: Encapsulation - Never expose password hash by default
        """
        data = super().to_dict()

        # Remove password hash from output by default
        if not include_sensitive and 'password_hash' in data:
            del data['password_hash']

        # Convert enum to string value
        if 'role' in data:
            data['role'] = self.role.value if isinstance(self.role, UserRole) else self.role

        # Add computed properties
        data['full_name'] = self.full_name

        return data

    def has_permission(self, required_role):
        """
        Check if user has required permission level.

        Args:
            required_role (UserRole): Required role for action

        Returns:
            bool: True if user has permission

        Role hierarchy: Admin > Technician > Client
        """
        role_hierarchy = {
            UserRole.CLIENT: 1,
            UserRole.TECHNICIAN: 2,
            UserRole.ADMIN: 3
        }

        user_level = role_hierarchy.get(self.role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        return user_level >= required_level
