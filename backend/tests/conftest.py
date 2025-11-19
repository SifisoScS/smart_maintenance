"""
Test configuration and fixtures.

Provides reusable test fixtures for all test modules.
"""

import pytest
from app import create_app
from app.database import db
from app.models import User, Asset, MaintenanceRequest, UserRole, AssetCategory, AssetStatus, AssetCondition
from app.models.permission import Permission
from app.models.role import Role


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


@pytest.fixture
def admin_permissions_token(client, admin_with_permissions):
    """
    Get JWT access token for admin user with RBAC permissions.

    Returns:
        str: JWT access token
    """
    response = client.post('/api/v1/auth/login', json={
        'email': admin_with_permissions.email,
        'password': 'password123'
    })
    return response.get_json()['access_token']


# RBAC Fixtures

@pytest.fixture
def sample_permissions(db_session):
    """
    Create sample permissions for testing.

    Returns:
        List of Permission instances
    """
    permissions = [
        Permission(name='view_requests', description='View requests', resource='requests', action='view'),
        Permission(name='create_requests', description='Create requests', resource='requests', action='create'),
        Permission(name='edit_requests', description='Edit requests', resource='requests', action='edit'),
        Permission(name='delete_requests', description='Delete requests', resource='requests', action='delete'),
        Permission(name='view_assets', description='View assets', resource='assets', action='view'),
        Permission(name='create_assets', description='Create assets', resource='assets', action='create'),
        Permission(name='edit_assets', description='Edit assets', resource='assets', action='edit'),
        Permission(name='view_users', description='View users', resource='users', action='view'),
        # Add RBAC-specific permissions for testing endpoints
        Permission(name='view_permissions', description='View permissions', resource='permissions', action='view'),
        Permission(name='manage_permissions', description='Manage permissions', resource='permissions', action='manage'),
        Permission(name='view_roles', description='View roles', resource='roles', action='view'),
        Permission(name='manage_roles', description='Manage roles', resource='roles', action='manage'),
        Permission(name='assign_roles', description='Assign roles to users', resource='roles', action='assign'),
        Permission(name='remove_roles', description='Remove roles from users', resource='roles', action='remove'),
    ]

    db_session.session.add_all(permissions)
    db_session.session.commit()

    return permissions


@pytest.fixture
def sample_role(db_session, sample_permissions):
    """
    Create a sample role with permissions for testing.

    Returns:
        Role instance
    """
    role = Role(
        name='Test Role',
        description='A test role with some permissions',
        is_system=False
    )

    db_session.session.add(role)
    db_session.session.commit()

    # Add first 3 permissions to the role
    for perm in sample_permissions[:3]:
        role.permissions.append(perm)

    db_session.session.commit()

    return role


@pytest.fixture
def sample_system_role(db_session, sample_permissions):
    """
    Create a system role that cannot be deleted.

    Returns:
        Role instance
    """
    role = Role(
        name='System Admin',
        description='System administrator role',
        is_system=True
    )

    db_session.session.add(role)
    db_session.session.commit()

    # Add all permissions
    for perm in sample_permissions:
        role.permissions.append(perm)

    db_session.session.commit()

    return role


@pytest.fixture
def user_with_roles(db_session, sample_role, sample_system_role):
    """
    Create a user with multiple roles assigned.

    Returns:
        User instance with roles
    """
    user = User(
        email='rbac_user@example.com',
        first_name='RBAC',
        last_name='User',
        role=UserRole.CLIENT,
        is_active=True
    )
    user.set_password('password123')

    db_session.session.add(user)
    db_session.session.commit()

    # Assign both roles to the user
    user.roles.append(sample_role)
    user.roles.append(sample_system_role)
    db_session.session.commit()

    return user


@pytest.fixture
def admin_with_permissions(db_session, sample_admin, sample_permissions):
    """
    Give the admin user all necessary RBAC permissions for testing.

    Returns:
        User instance (admin with full permissions)
    """
    # Create an admin role with all permissions
    admin_role = Role(
        name='Test Admin Role',
        description='Admin role for testing with all permissions',
        is_system=False
    )

    db_session.session.add(admin_role)
    db_session.session.commit()

    # Add all permissions to the admin role
    for perm in sample_permissions:
        admin_role.permissions.append(perm)

    # Assign the role to the admin user
    sample_admin.roles.append(admin_role)
    db_session.session.commit()

    return sample_admin
