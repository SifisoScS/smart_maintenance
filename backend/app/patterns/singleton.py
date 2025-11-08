"""
Singleton Pattern Implementation

Purpose: Ensures a class has only one instance and provides global access to it.
Use Case: Configuration management, database connections, logging.

OOP Principle: Encapsulation - Controls instance creation internally.
"""


class SingletonMeta(type):
    """
    Metaclass for implementing the Singleton pattern.

    This metaclass ensures that only one instance of a class exists.
    Thread-safe implementation for production use.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Override __call__ to control instance creation.

        If an instance doesn't exist, create it and store in _instances.
        Always return the same instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
