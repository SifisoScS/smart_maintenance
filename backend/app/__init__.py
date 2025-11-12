"""
Flask Application Factory

Demonstrates:
- Factory Pattern for app creation
- Dependency Injection configuration
- Centralized app initialization
"""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import get_config
from app.database import init_db


def create_app(config_name='default'):
    """
    Application factory for creating Flask app instances.

    Args:
        config_name: Configuration environment ('development', 'testing', 'production')

    Returns:
        Configured Flask application instance

    Benefits of Factory Pattern:
    - Easy testing with different configurations
    - Multiple app instances possible
    - Clean separation of configuration
    """
    # Create Flask app
    app = Flask(__name__)

    # Load configuration using Singleton pattern
    config = get_config(config_name)
    app.config.from_object(config)

    # Initialize extensions
    init_db(app)
    # Enable CORS for all routes - allow all origins in development
    CORS(app, resources={r"/*": {"origins": "*"}})
    jwt = JWTManager(app)

    # Import models to register with SQLAlchemy
    # This must happen after db initialization
    with app.app_context():
        from app import models  # noqa

    # Register observers for event-driven architecture
    register_observers(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    return app


def register_blueprints(app):
    """
    Register Flask blueprints.

    Args:
        app: Flask application instance
    """
    # Import controllers
    from app.controllers.health_controller import health_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.user_controller import user_bp
    from app.controllers.asset_controller import asset_bp
    from app.controllers.request_controller import request_bp
    from app.controllers.feature_flag_controller import feature_flag_bp

    # Register API blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(asset_bp)
    app.register_blueprint(request_bp)
    app.register_blueprint(feature_flag_bp)

    # Register legacy API blueprint if it exists
    try:
        from app.routes.api import api_bp
        app.register_blueprint(api_bp)
    except ImportError:
        pass  # Legacy blueprint doesn't exist, that's fine


def register_observers(app):
    """
    Register event observers with EventBus.

    This sets up the event-driven architecture by:
    1. Creating observer instances
    2. Subscribing them to relevant event types
    3. Enabling decoupled, reactive system behavior

    Args:
        app: Flask application instance
    """
    from app.patterns.event_bus import EventBus
    from app.events.event_types import EventTypes
    from app.observers import (
        NotificationObserver,
        LoggingObserver,
        MetricsObserver,
        AssetStatusObserver
    )

    # Get EventBus singleton instance
    event_bus = EventBus()

    # Create observer instances
    # Note: NotificationObserver gets None for now as NotificationService
    # will be injected when needed in production
    notification_observer = NotificationObserver(notification_service=None)
    logging_observer = LoggingObserver()
    metrics_observer = MetricsObserver()
    asset_status_observer = AssetStatusObserver()

    # Subscribe NotificationObserver to user/request events
    event_bus.subscribe(EventTypes.USER_REGISTERED, notification_observer)
    event_bus.subscribe(EventTypes.REQUEST_CREATED, notification_observer)
    event_bus.subscribe(EventTypes.REQUEST_ASSIGNED, notification_observer)
    event_bus.subscribe(EventTypes.REQUEST_STARTED, notification_observer)
    event_bus.subscribe(EventTypes.REQUEST_COMPLETED, notification_observer)

    # Subscribe LoggingObserver to ALL event types (for audit trail)
    for event_type in EventTypes.all_events():
        event_bus.subscribe(event_type, logging_observer)

    # Subscribe MetricsObserver to tracked events
    event_bus.subscribe(EventTypes.REQUEST_CREATED, metrics_observer)
    event_bus.subscribe(EventTypes.REQUEST_COMPLETED, metrics_observer)
    event_bus.subscribe(EventTypes.REQUEST_ASSIGNED, metrics_observer)
    event_bus.subscribe(EventTypes.ASSET_CREATED, metrics_observer)
    event_bus.subscribe(EventTypes.ASSET_CONDITION_CHANGED, metrics_observer)

    # Subscribe AssetStatusObserver to asset/request events
    event_bus.subscribe(EventTypes.REQUEST_ASSIGNED, asset_status_observer)
    event_bus.subscribe(EventTypes.REQUEST_COMPLETED, asset_status_observer)
    event_bus.subscribe(EventTypes.ASSET_CONDITION_CHANGED, asset_status_observer)

    app.logger.info("✓ Event observers registered successfully")


def register_error_handlers(app):
    """
    Register global error handlers.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500

    @app.errorhandler(ValueError)
    def validation_error(error):
        return {'error': str(error)}, 400
