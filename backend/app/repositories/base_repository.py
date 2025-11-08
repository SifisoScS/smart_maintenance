"""
Base Repository Pattern Implementation

Purpose: Abstract database operations from business logic.

Benefits:
- Separates data access from domain logic
- Makes code testable (can mock repositories)
- Centralizes database operations
- Follows Single Responsibility Principle

OOP Principles:
- Abstraction: Hides SQLAlchemy complexity
- Encapsulation: Database operations internal to repository
- DRY: Common CRUD operations in one place
"""

from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy.exc import SQLAlchemyError
from app.database import db
from app.models.base import BaseModel

# Generic type variable for model classes
T = TypeVar('T', bound=BaseModel)


class BaseRepository(Generic[T]):
    """
    Generic repository with common CRUD operations.

    Type parameter T represents the model class (User, Asset, etc.)

    OOP Principle: Dependency Inversion - Business logic depends on
    repository abstraction, not concrete database implementation.
    """

    def __init__(self, model_class: Type[T]):
        """
        Initialize repository with model class.

        Args:
            model_class: The SQLAlchemy model class (e.g., User, Asset)
        """
        self.model_class = model_class

    def create(self, **kwargs) -> T:
        """
        Create a new instance of the model.

        Args:
            **kwargs: Model field values

        Returns:
            Created model instance

        Raises:
            ValueError: If validation fails
            SQLAlchemyError: If database operation fails
        """
        try:
            # Use model's create method which includes validation
            instance = self.model_class.create(**kwargs)
            db.session.add(instance)
            db.session.commit()
            db.session.refresh(instance)  # Refresh to get updated values
            return instance
        except ValueError as e:
            db.session.rollback()
            raise e
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error creating {self.model_class.__name__}: {str(e)}")

    def get_by_id(self, id: int) -> Optional[T]:
        """
        Get model instance by ID.

        Args:
            id: Primary key value

        Returns:
            Model instance or None if not found
        """
        return db.session.get(self.model_class, id)

    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """
        Get all instances of the model.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of model instances
        """
        query = db.session.query(self.model_class)

        if offset:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)

        return query.all()

    def get_by_filter(self, **filters) -> List[T]:
        """
        Get instances matching filter criteria.

        Args:
            **filters: Field name and value pairs

        Returns:
            List of matching model instances

        Example:
            users = user_repo.get_by_filter(role='admin', is_active=True)
        """
        return db.session.query(self.model_class).filter_by(**filters).all()

    def get_one_by_filter(self, **filters) -> Optional[T]:
        """
        Get single instance matching filter criteria.

        Args:
            **filters: Field name and value pairs

        Returns:
            Model instance or None if not found
        """
        return db.session.query(self.model_class).filter_by(**filters).first()

    def update(self, instance: T, **kwargs) -> T:
        """
        Update existing model instance.

        Args:
            instance: Model instance to update
            **kwargs: Field values to update

        Returns:
            Updated model instance

        Raises:
            ValueError: If validation fails
            SQLAlchemyError: If database operation fails
        """
        try:
            # Use model's update method
            instance.update(**kwargs)

            # Validate after update
            instance.validate()

            db.session.commit()
            db.session.refresh(instance)
            return instance
        except ValueError as e:
            db.session.rollback()
            raise e
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error updating {self.model_class.__name__}: {str(e)}")

    def delete(self, instance: T) -> bool:
        """
        Delete model instance.

        Args:
            instance: Model instance to delete

        Returns:
            True if deleted successfully

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            db.session.delete(instance)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error deleting {self.model_class.__name__}: {str(e)}")

    def delete_by_id(self, id: int) -> bool:
        """
        Delete model instance by ID.

        Args:
            id: Primary key value

        Returns:
            True if deleted, False if not found

        Raises:
            SQLAlchemyError: If database operation fails
        """
        instance = self.get_by_id(id)
        if instance:
            return self.delete(instance)
        return False

    def exists(self, id: int) -> bool:
        """
        Check if instance with given ID exists.

        Args:
            id: Primary key value

        Returns:
            True if exists, False otherwise
        """
        return db.session.query(
            db.session.query(self.model_class).filter_by(id=id).exists()
        ).scalar()

    def count(self, **filters) -> int:
        """
        Count instances matching filter criteria.

        Args:
            **filters: Field name and value pairs (optional)

        Returns:
            Number of matching instances
        """
        query = db.session.query(self.model_class)

        if filters:
            query = query.filter_by(**filters)

        return query.count()

    def bulk_create(self, instances: List[T]) -> List[T]:
        """
        Create multiple instances in one transaction.

        Args:
            instances: List of model instances to create

        Returns:
            List of created instances

        Raises:
            ValueError: If validation fails for any instance
            SQLAlchemyError: If database operation fails
        """
        try:
            # Validate all instances before committing
            for instance in instances:
                instance.validate()

            db.session.add_all(instances)
            db.session.commit()

            # Refresh all instances
            for instance in instances:
                db.session.refresh(instance)

            return instances
        except ValueError as e:
            db.session.rollback()
            raise e
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error bulk creating {self.model_class.__name__}: {str(e)}")
