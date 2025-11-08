"""
Test configuration and fixtures.

Provides reusable test fixtures for all test modules.
"""

import pytest
from app import create_app
from app.database import db
from app.models import User, Asset, MaintenanceRequest, UserRole, AssetCategory, AssetStatus, AssetCondition


@pytest.fixture(scope='session')
def app():
    """
    Create Flask app configured for testing.

    Uses in-memory SQLite for fast, isolated tests.
    """
    app = create_app('testing')
    return app


@pytest.fixture(scope='function')
def client(app):
    """
    Flask test client for making requests.
    """
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """
    Database session for testing with automatic cleanup.

    Creates all tables before test, drops after test.
    """
    with app.app_context():
        # Create all tables
        db.create_all()

        yield db

        # Clean up after test
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_user(db_session):
    """
    Create a sample user for testing.

    Returns:
        User instance (client role)
    """
    user = User(
        email='test@example.com',
        first_name='Test',
        last_name='User',
        role=UserRole.CLIENT,
        is_active=True
    )
    user.set_password('password123')

    db_session.session.add(user)
    db_session.session.commit()

    return user


@pytest.fixture
def sample_technician(db_session):
    """
    Create a sample technician for testing.

    Returns:
        User instance (technician role)
    """
    user = User(
        email='tech@example.com',
        first_name='John',
        last_name='Technician',
        role=UserRole.TECHNICIAN,
        is_active=True
    )
    user.set_password('password123')

    db_session.session.add(user)
    db_session.session.commit()

    return user


@pytest.fixture
def sample_admin(db_session):
    """
    Create a sample admin for testing.

    Returns:
        User instance (admin role)
    """
    user = User(
        email='admin@example.com',
        first_name='Admin',
        last_name='User',
        role=UserRole.ADMIN,
        is_active=True
    )
    user.set_password('password123')

    db_session.session.add(user)
    db_session.session.commit()

    return user


@pytest.fixture
def sample_asset(db_session):
    """
    Create a sample asset for testing.

    Returns:
        Asset instance
    """
    asset = Asset(
        name='Test Asset',
        asset_tag='ASSET-001',
        category=AssetCategory.ELECTRICAL,
        status=AssetStatus.ACTIVE,
        condition=AssetCondition.GOOD,
        building='Main Building',
        floor='1',
        room='101'
    )

    db_session.session.add(asset)
    db_session.session.commit()

    return asset


@pytest.fixture
def multiple_users(db_session):
    """
    Create multiple users with different roles.

    Returns:
        List of User instances
    """
    users = []

    # Create 2 admins
    for i in range(2):
        user = User(
            email=f'admin{i}@example.com',
            first_name=f'Admin{i}',
            last_name='User',
            role=UserRole.ADMIN,
            is_active=True
        )
        user.set_password('password123')
        users.append(user)

    # Create 3 technicians
    for i in range(3):
        user = User(
            email=f'tech{i}@example.com',
            first_name=f'Tech{i}',
            last_name='User',
            role=UserRole.TECHNICIAN,
            is_active=True
        )
        user.set_password('password123')
        users.append(user)

    # Create 5 clients
    for i in range(5):
        user = User(
            email=f'client{i}@example.com',
            first_name=f'Client{i}',
            last_name='User',
            role=UserRole.CLIENT,
            is_active=True
        )
        user.set_password('password123')
        users.append(user)

    db_session.session.add_all(users)
    db_session.session.commit()

    return users


@pytest.fixture
def multiple_assets(db_session):
    """
    Create multiple assets with different statuses and conditions.

    Returns:
        List of Asset instances
    """
    assets = []

    categories = [AssetCategory.ELECTRICAL, AssetCategory.PLUMBING, AssetCategory.HVAC]
    statuses = [AssetStatus.ACTIVE, AssetStatus.IN_REPAIR, AssetStatus.OUT_OF_SERVICE]
    conditions = [AssetCondition.EXCELLENT, AssetCondition.GOOD, AssetCondition.FAIR, AssetCondition.POOR]

    for i in range(10):
        asset = Asset(
            name=f'Asset {i}',
            asset_tag=f'ASSET-{i:03d}',
            category=categories[i % len(categories)],
            status=statuses[i % len(statuses)],
            condition=conditions[i % len(conditions)],
            building='Building A',
            floor=str((i % 3) + 1),
            room=str(100 + i)
        )
        assets.append(asset)

    db_session.session.add_all(assets)
    db_session.session.commit()

    return assets


# JWT Token Fixtures for API Testing

@pytest.fixture
def admin_token(client, sample_admin):
    """
    Get JWT access token for admin user by logging in.

    Returns:
        str: JWT access token
    """
    response = client.post('/api/v1/auth/login', json={
        'email': sample_admin.email,
        'password': 'password123'
    })
    return response.get_json()['access_token']


@pytest.fixture
def technician_token(client, sample_technician):
    """
    Get JWT access token for technician user by logging in.

    Returns:
        str: JWT access token
    """
    response = client.post('/api/v1/auth/login', json={
        'email': sample_technician.email,
        'password': 'password123'
    })
    return response.get_json()['access_token']


@pytest.fixture
def client_token(client, sample_user):
    """
    Get JWT access token for client user by logging in.

    Returns:
        str: JWT access token
    """
    response = client.post('/api/v1/auth/login', json={
        'email': sample_user.email,
        'password': 'password123'
    })
    return response.get_json()['access_token']


@pytest.fixture
def auth_headers_admin(admin_token):
    """
    Authorization headers for admin user.

    Returns:
        dict: Headers with Bearer token
    """
    return {'Authorization': f'Bearer {admin_token}'}


@pytest.fixture
def auth_headers_technician(technician_token):
    """
    Authorization headers for technician user.

    Returns:
        dict: Headers with Bearer token
    """
    return {'Authorization': f'Bearer {technician_token}'}


@pytest.fixture
def auth_headers_client(client_token):
    """
    Authorization headers for client user.

    Returns:
        dict: Headers with Bearer token
    """
    return {'Authorization': f'Bearer {client_token}'}
