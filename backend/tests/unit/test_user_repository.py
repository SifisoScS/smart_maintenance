"""
Unit tests for UserRepository.

Tests demonstrate Repository Pattern benefits:
- Clean separation between data access and business logic
- Easy mocking for testing
- Consistent interface across repositories
"""

import pytest
from app.repositories.user_repository import UserRepository
from app.models import User, UserRole


class TestUserRepository:
    """Test suite for UserRepository"""

    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        """Set up test dependencies"""
        self.repo = UserRepository()

    def test_create_user_success(self, db_session):
        """Test creating a user with valid data"""
        user = self.repo.create_user(
            email='newuser@example.com',
            password='password123',
            first_name='New',
            last_name='User',
            role=UserRole.CLIENT
        )

        assert user.id is not None
        assert user.email == 'newuser@example.com'
        assert user.first_name == 'New'
        assert user.last_name == 'User'
        assert user.role == UserRole.CLIENT
        assert user.is_active is True
        assert user.check_password('password123') is True

    def test_create_user_duplicate_email(self, db_session, sample_user):
        """Test creating user with existing email raises error"""
        with pytest.raises(ValueError, match="already registered"):
            self.repo.create_user(
                email=sample_user.email,
                password='password123',
                first_name='Duplicate',
                last_name='User',
                role=UserRole.CLIENT
            )

    def test_create_user_invalid_password(self, db_session):
        """Test creating user with invalid password raises error"""
        with pytest.raises(ValueError, match="at least 6 characters"):
            self.repo.create_user(
                email='test@example.com',
                password='12345',  # Too short
                first_name='Test',
                last_name='User',
                role=UserRole.CLIENT
            )

    def test_get_by_email(self, db_session, sample_user):
        """Test retrieving user by email"""
        user = self.repo.get_by_email(sample_user.email)

        assert user is not None
        assert user.id == sample_user.id
        assert user.email == sample_user.email

    def test_get_by_email_case_insensitive(self, db_session, sample_user):
        """Test email lookup is case insensitive"""
        user = self.repo.get_by_email(sample_user.email.upper())

        assert user is not None
        assert user.id == sample_user.id

    def test_get_by_email_not_found(self, db_session):
        """Test retrieving non-existent email returns None"""
        user = self.repo.get_by_email('nonexistent@example.com')

        assert user is None

    def test_get_by_role(self, db_session, multiple_users):
        """Test retrieving users by role"""
        admins = self.repo.get_by_role(UserRole.ADMIN)
        technicians = self.repo.get_by_role(UserRole.TECHNICIAN)
        clients = self.repo.get_by_role(UserRole.CLIENT)

        assert len(admins) == 2
        assert len(technicians) == 3
        assert len(clients) == 5

        # Verify all returned users have correct role
        assert all(user.role == UserRole.ADMIN for user in admins)
        assert all(user.role == UserRole.TECHNICIAN for user in technicians)
        assert all(user.role == UserRole.CLIENT for user in clients)

    def test_get_active_users(self, db_session, multiple_users):
        """Test retrieving only active users"""
        # Deactivate one user
        multiple_users[0].is_active = False
        db_session.session.commit()

        active_users = self.repo.get_active_users()

        assert len(active_users) == len(multiple_users) - 1
        assert all(user.is_active for user in active_users)

    def test_get_active_technicians(self, db_session, multiple_users):
        """Test retrieving active technicians"""
        # Deactivate one technician
        technicians = [u for u in multiple_users if u.role == UserRole.TECHNICIAN]
        technicians[0].is_active = False
        db_session.session.commit()

        active_techs = self.repo.get_active_technicians()

        assert len(active_techs) == 2  # 3 total - 1 deactivated
        assert all(user.role == UserRole.TECHNICIAN for user in active_techs)
        assert all(user.is_active for user in active_techs)

    def test_email_exists(self, db_session, sample_user):
        """Test checking if email exists"""
        assert self.repo.email_exists(sample_user.email) is True
        assert self.repo.email_exists('nonexistent@example.com') is False

    def test_authenticate_success(self, db_session, sample_user):
        """Test successful authentication"""
        user = self.repo.authenticate(sample_user.email, 'password123')

        assert user is not None
        assert user.id == sample_user.id

    def test_authenticate_wrong_password(self, db_session, sample_user):
        """Test authentication with wrong password"""
        user = self.repo.authenticate(sample_user.email, 'wrongpassword')

        assert user is None

    def test_authenticate_inactive_user(self, db_session, sample_user):
        """Test authentication fails for inactive user"""
        sample_user.is_active = False
        db_session.session.commit()

        user = self.repo.authenticate(sample_user.email, 'password123')

        assert user is None

    def test_authenticate_nonexistent_user(self, db_session):
        """Test authentication with non-existent email"""
        user = self.repo.authenticate('nonexistent@example.com', 'password')

        assert user is None

    def test_deactivate_user(self, db_session, sample_user):
        """Test deactivating a user"""
        assert sample_user.is_active is True

        result = self.repo.deactivate_user(sample_user.id)

        assert result is True
        db_session.session.refresh(sample_user)
        assert sample_user.is_active is False

    def test_deactivate_nonexistent_user(self, db_session):
        """Test deactivating non-existent user returns False"""
        result = self.repo.deactivate_user(99999)

        assert result is False

    def test_reactivate_user(self, db_session, sample_user):
        """Test reactivating a deactivated user"""
        sample_user.is_active = False
        db_session.session.commit()

        result = self.repo.reactivate_user(sample_user.id)

        assert result is True
        db_session.session.refresh(sample_user)
        assert sample_user.is_active is True

    def test_update_password(self, db_session, sample_user):
        """Test updating user password"""
        old_password_hash = sample_user.password_hash

        result = self.repo.update_password(sample_user.id, 'newpassword123')

        assert result is True
        db_session.session.refresh(sample_user)
        assert sample_user.password_hash != old_password_hash
        assert sample_user.check_password('newpassword123') is True
        assert sample_user.check_password('password123') is False

    def test_update_password_invalid(self, db_session, sample_user):
        """Test updating password with invalid value"""
        with pytest.raises(ValueError):
            self.repo.update_password(sample_user.id, 'short')

    def test_update_password_nonexistent_user(self, db_session):
        """Test updating password for non-existent user"""
        result = self.repo.update_password(99999, 'newpassword123')

        assert result is False

    def test_get_by_id(self, db_session, sample_user):
        """Test retrieving user by ID"""
        user = self.repo.get_by_id(sample_user.id)

        assert user is not None
        assert user.id == sample_user.id
        assert user.email == sample_user.email

    def test_get_all_users(self, db_session, multiple_users):
        """Test retrieving all users"""
        users = self.repo.get_all()

        assert len(users) == len(multiple_users)

    def test_get_all_with_pagination(self, db_session, multiple_users):
        """Test retrieving users with pagination"""
        page1 = self.repo.get_all(limit=5, offset=0)
        page2 = self.repo.get_all(limit=5, offset=5)

        assert len(page1) == 5
        assert len(page2) == 5
        assert page1[0].id != page2[0].id

    def test_count_users(self, db_session, multiple_users):
        """Test counting users"""
        total = self.repo.count()
        assert total == len(multiple_users)

        admins_count = self.repo.count(role=UserRole.ADMIN)
        assert admins_count == 2

    def test_user_full_name_property(self, db_session, sample_user):
        """Test computed full_name property"""
        assert sample_user.full_name == 'Test User'

    def test_user_role_properties(self, db_session, sample_user, sample_admin, sample_technician):
        """Test role check properties"""
        assert sample_user.is_client is True
        assert sample_user.is_admin is False
        assert sample_user.is_technician is False

        assert sample_admin.is_admin is True
        assert sample_admin.is_client is False

        assert sample_technician.is_technician is True
        assert sample_technician.is_admin is False

    def test_user_permission_hierarchy(self, db_session, sample_user, sample_admin, sample_technician):
        """Test permission hierarchy (Admin > Technician > Client)"""
        assert sample_admin.has_permission(UserRole.ADMIN) is True
        assert sample_admin.has_permission(UserRole.TECHNICIAN) is True
        assert sample_admin.has_permission(UserRole.CLIENT) is True

        assert sample_technician.has_permission(UserRole.ADMIN) is False
        assert sample_technician.has_permission(UserRole.TECHNICIAN) is True
        assert sample_technician.has_permission(UserRole.CLIENT) is True

        assert sample_user.has_permission(UserRole.ADMIN) is False
        assert sample_user.has_permission(UserRole.TECHNICIAN) is False
        assert sample_user.has_permission(UserRole.CLIENT) is True
