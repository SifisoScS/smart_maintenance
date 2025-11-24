"""
Base Repository Pattern Implementation

Purpose: Abstract database operations from business logic.

Benefits:
- Separates data access from domain logic
- Makes code testable (can mock repositories)
- Centralizes database operations
- Follows Single Responsibility Principle
- Automatic tenant isolation for multi-tenancy

OOP Principles:
- Abstraction: Hides SQLAlchemy complexity
- Encapsulation: Database operations internal to repository
- DRY: Common CRUD operations in one place
"""

from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy.exc import SQLAlchemyError
from flask import g, has_request_context
from app.database import db
from app.models.base import BaseModel

# Generic type variable for model classes
T = TypeVar('T', bound=BaseModel)


class BaseRepository(Generic[T]):
    """
    Generic repository with common CRUD operations.

    Type parameter T represents the model class (User, Asset, etc.)

    Multi-Tenancy:
    - Automatically filters queries by tenant_id from Flask g.current_tenant_id
    - Can be bypassed with bypass_tenant_filter=True for admin operations
    - Tenant model itself is excluded from tenant filtering

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

    def _should_filter_by_tenant(self) -> bool:
        """
        Determine if queries should be filtered by tenant_id.

        Returns:
            True if tenant filtering should be applied, False otherwise
        """
        # Don't filter Tenant model itself
        if self.model_class.__name__ == 'Tenant':
            return False

        # Don't filter TenantSubscription model
        if self.model_class.__name__ == 'TenantSubscription':
            return False

        # Check if model has tenant_id attribute
        if not hasattr(self.model_class, 'tenant_id'):
            return False

        # Check if we're in a request context with tenant_id
        if not has_request_context():
            return False

        # Check if current_tenant_id is set in Flask g
        if not hasattr(g, 'current_tenant_id') or g.current_tenant_id is None:
            return False

        return True

    def _apply_tenant_filter(self, query, bypass_tenant_filter: bool = False):
        """
        Apply tenant_id filter to query if applicable.

        Args:
            query: SQLAlchemy query object
            bypass_tenant_filter: If True, skip tenant filtering (for admin operations)

        Returns:
            Query with tenant filter applied (if applicable)
        """
        if bypass_tenant_filter:
            return query

        if self._should_filter_by_tenant():
            return query.filter(self.model_class.tenant_id == g.current_tenant_id)

        return query

    def create(self, **kwargs) -> T:
        """
        Create a new instance of the model.

        Automatically sets tenant_id if in tenant context.

        Args:
            **kwargs: Model field values

        Returns:
            Created model instance

        Raises:
            ValueError: If validation fails
            SQLAlchemyError: If database operation fails
        """
        try:
            # Automatically set tenant_id if applicable
            if self._should_filter_by_tenant() and 'tenant_id' not in kwargs:
                kwargs['tenant_id'] = g.current_tenant_id

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

    def get_by_id(self, id: int, bypass_tenant_filter: bool = False) -> Optional[T]:
        """
        Get model instance by ID.

        Automatically filters by tenant_id unless bypassed.

        Args:
            id: Primary key value
            bypass_tenant_filter: If True, skip tenant filtering (for admin operations)

        Returns:
            Model instance or None if not found
        """
        query = db.session.query(self.model_class).filter(self.model_class.id == id)
        query = self._apply_tenant_filter(query, bypass_tenant_filter)
        return query.first()

    def get_all(self, limit: Optional[int] = None, offset: int = 0,
                bypass_tenant_filter: bool = False) -> List[T]:
        """
        Get all instances of the model.

        Automatically filters by tenant_id unless bypassed.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            bypass_tenant_filter: If True, skip tenant filtering (for admin operations)

        Returns:
            List of model instances
        """
        query = db.session.query(self.model_class)
        query = self._apply_tenant_filter(query, bypass_tenant_filter)

        if offset:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)

        return query.all()

    def get_by_filter(self, bypass_tenant_filter: bool = False, **filters) -> List[T]:
        """
        Get instances matching filter criteria.

        Automatically filters by tenant_id unless bypassed.

        Args:
            bypass_tenant_filter: If True, skip tenant filtering (for admin operations)
            **filters: Field name and value pairs

        Returns:
            List of matching model instances

        Example:
            users = user_repo.get_by_filter(role='admin', is_active=True)
        """
        query = db.session.query(self.model_class).filter_by(**filters)
        query = self._apply_tenant_filter(query, bypass_tenant_filter)
        return query.all()

    def get_one_by_filter(self, bypass_tenant_filter: bool = False, **filters) -> Optional[T]:
        """
        Get single instance matching filter criteria.

        Automatically filters by tenant_id unless bypassed.

        Args:
            bypass_tenant_filter: If True, skip tenant filtering (for admin operations)
            **filters: Field name and value pairs

        Returns:
            Model instance or None if not found
        """
        query = db.session.query(self.model_class).filter_by(**filters)
        query = self._apply_tenant_filter(query, bypass_tenant_filter)
        return query.first()

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

    def delete_by_id(self, id: int, bypass_tenant_filter: bool = False) -> bool:
        """
        Delete model instance by ID.

        Automatically filters by tenant_id unless bypassed.

        Args:
            id: Primary key value
            bypass_tenant_filter: If True, skip tenant filtering (for admin operations)

        Returns:
            True if deleted, False if not found

        Raises:
            SQLAlchemyError: If database operation fails
        """
        instance = self.get_by_id(id, bypass_tenant_filter)
        if instance:
            return self.delete(instance)
        return False

    def exists(self, id: int, bypass_tenant_filter: bool = False) -> bool:
        """
        Check if instance with given ID exists.

        Automatically filters by tenant_id unless bypassed.

        Args:
            id: Primary key value
            bypass_tenant_filter: If True, skip tenant filtering (for admin operations)

        Returns:
            True if exists, False otherwise
        """
        query = db.session.query(self.model_class).filter_by(id=id)
        query = self._apply_tenant_filter(query, bypass_tenant_filter)
        return db.session.query(query.exists()).scalar()

    def count(self, bypass_tenant_filter: bool = False, **filters) -> int:
        """
        Count instances matching filter criteria.

        Automatically filters by tenant_id unless bypassed.

        Args:
            bypass_tenant_filter: If True, skip tenant filtering (for admin operations)
            **filters: Field name and value pairs (optional)

        Returns:
            Number of matching instances
        """
        query = db.session.query(self.model_class)

        if filters:
            query = query.filter_by(**filters)

        query = self._apply_tenant_filter(query, bypass_tenant_filter)

        return query.count()

    def bulk_create(self, instances: List[T]) -> List[T]:
        """
        Create multiple instances in one transaction.

        Automatically sets tenant_id on all instances if in tenant context.

        Args:
            instances: List of model instances to create

        Returns:
            List of created instances

        Raises:
            ValueError: If validation fails for any instance
            SQLAlchemyError: If database operation fails
        """
        try:
            # Set tenant_id on all instances if applicable
            if self._should_filter_by_tenant():
                for instance in instances:
                    if not hasattr(instance, 'tenant_id') or instance.tenant_id is None:
                        instance.tenant_id = g.current_tenant_id

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
