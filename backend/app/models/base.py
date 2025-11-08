"""
Base Model with common functionality for all models.

Demonstrates:
- OOP Inheritance: All models inherit common behavior
- Encapsulation: Common fields and methods in one place
- DRY Principle: Don't repeat timestamp and ID logic
"""

from datetime import datetime
from app.database import db


class BaseModel(db.Model):
    """
    Abstract base model with common fields and methods.

    All domain models inherit from this class to get:
    - Primary key (id)
    - Timestamps (created_at, updated_at)
    - Common CRUD helper methods
    - Validation framework

    OOP Principles:
    - Single Responsibility: Manages only common model concerns
    - Open/Closed: Open for extension, closed for modification
    """

    __abstract__ = True  # SQLAlchemy won't create table for this

    # Common fields for all models
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        """String representation of model instance"""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self):
        """
        Convert model instance to dictionary.

        Returns:
            dict: Dictionary representation of the model

        Note: Override in subclasses to customize serialization
        """
        result = {}
        for column in self.__table__.columns:
            # Skip columns that don't have values (for polymorphic models)
            if not hasattr(self, column.name):
                continue

            value = getattr(self, column.name, None)

            # Skip None values for optional polymorphic columns
            if value is None and column.nullable:
                continue

            # Handle datetime serialization
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result

    def update(self, **kwargs):
        """
        Update model attributes from keyword arguments.

        Args:
            **kwargs: Field names and values to update

        Note: Does not commit to database, just updates instance
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def validate(self):
        """
        Validate model instance.

        Override in subclasses to implement validation logic.
        Raise ValueError with descriptive message if validation fails.

        OOP Principle: Each model validates itself (encapsulation)
        """
        pass

    @classmethod
    def create(cls, **kwargs):
        """
        Factory method to create and validate instance.

        Args:
            **kwargs: Model field values

        Returns:
            Instance of the model

        Raises:
            ValueError: If validation fails
        """
        instance = cls(**kwargs)
        instance.validate()
        return instance
