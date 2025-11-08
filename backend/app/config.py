"""
Configuration Management using Singleton Pattern

Ensures single source of truth for application configuration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from app.patterns.singleton import SingletonMeta

# Load environment variables from .env file
basedir = Path(__file__).parent.parent
load_dotenv(basedir / '.env')


class Config(metaclass=SingletonMeta):
    """
    Central configuration class using Singleton pattern.

    OOP Principles:
    - Single Responsibility: Manages only configuration
    - Encapsulation: Hides environment variable access
    """

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{basedir / "smart_maintenance.db"}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 28800))  # 8 hours (for development)
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))  # 30 days
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    # CORS Configuration - Allow Blazor frontend origins
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5112,http://localhost:5222,https://localhost:5001,http://localhost:5000,https://localhost:7001').split(',')

    # Notification Configuration (for future Strategy pattern use)
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')

    @classmethod
    def get_instance(cls):
        """
        Explicitly get the singleton instance.
        """
        return cls()


class DevelopmentConfig(Config):
    """Development-specific configuration"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing-specific configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    """Production-specific configuration"""
    DEBUG = False
    TESTING = False
    # In production, these MUST come from environment variables
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


# Configuration factory
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env_name='default'):
    """
    Factory function to get appropriate configuration.

    Args:
        env_name: Environment name (development, testing, production)

    Returns:
        Configuration class instance
    """
    return config_by_name.get(env_name, DevelopmentConfig)()
