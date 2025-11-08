"""
Database initialization and connection management.

Uses Singleton pattern for database instance.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Database instance (will be initialized in app factory)
db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    """
    Initialize database with Flask app.

    Args:
        app: Flask application instance
    """
    db.init_app(app)
    migrate.init_app(app, db)
