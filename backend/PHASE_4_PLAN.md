# Phase 4 Implementation Plan
## API Testing Suite

**Status**: 🚧 IN PROGRESS
**Phase**: 4 of 5 - Comprehensive API Integration Testing
**Goal**: Write 50+ integration tests for all API endpoints

---

## 🎯 Objectives

### Primary Goals
1. Test all 26 API endpoints with integration tests
2. Verify authentication flows (register, login, refresh, logout)
3. Test authorization (role-based access control)
4. Validate input validation (valid/invalid inputs)
5. Test error handling (404, 401, 403, 400, 500)
6. Test complete workflows end-to-end
7. Achieve >80% code coverage for controllers

### Success Criteria
- ✅ 50+ integration tests written
- ✅ All authentication flows tested
- ✅ All authorization scenarios tested
- ✅ All endpoints have positive and negative test cases
- ✅ Complete workflow tests pass
- ✅ >80% controller code coverage
- ✅ All tests passing

---

## 📋 Testing Strategy

### Test Categories

**1. Authentication Tests (10-12 tests)**
- User registration (valid, duplicate email, invalid data)
- User login (valid credentials, invalid credentials, inactive user)
- Token refresh (valid token, expired token, blacklisted token)
- Logout (valid logout, already logged out)
- Get current user (authenticated, unauthenticated)

**2. Authorization Tests (8-10 tests)**
- Admin-only endpoints (with admin, with technician, with client, unauthenticated)
- Technician-only endpoints (with technician, with client, with admin)
- Resource ownership (own resource, other's resource, admin access)
- Role hierarchy validation

**3. User Management Tests (10-12 tests)**
- List users (admin success, non-admin forbidden)
- Get user profile (self, other as admin, other as non-admin)
- Update profile (self, other as admin, other as non-admin)
- Change password (correct old password, wrong old password, weak password)
- List technicians (authenticated success)

**4. Asset Management Tests (12-15 tests)**
- Create asset (admin success, non-admin forbidden, invalid data)
- List assets (authenticated success)
- Get asset (exists, not found)
- Update asset condition (technician success, invalid condition)
- Assets needing maintenance
- Asset statistics

**5. Request Management Tests (15-18 tests)**
- Create request (valid electrical, valid plumbing, valid HVAC, invalid data)
- List requests (authenticated success)
- Get request (exists, not found)
- Assign request (admin success, non-admin forbidden, invalid technician)
- Start work (assigned technician, unassigned technician, wrong technician)
- Complete work (assigned technician, missing notes, invalid hours)
- List unassigned (admin success, non-admin forbidden)

**6. Input Validation Tests (10-12 tests)**
- Missing required fields
- Invalid field types
- Invalid enum values
- Length constraints
- Email format validation
- Password complexity

**7. Workflow Tests (5-8 tests)**
- Complete maintenance request lifecycle
- Multiple requests with same technician
- Request reassignment
- Asset condition update after maintenance

**Total Estimated Tests**: 50-60 integration tests

---

## 🏗️ Test Structure

### Directory Structure
```
backend/tests/
├── conftest.py                    # Pytest configuration and fixtures
├── test_integration/              # Integration tests
│   ├── __init__.py
│   ├── test_auth_endpoints.py     # Authentication tests
│   ├── test_user_endpoints.py     # User management tests
│   ├── test_asset_endpoints.py    # Asset management tests
│   ├── test_request_endpoints.py  # Request management tests
│   ├── test_authorization.py      # RBAC tests
│   ├── test_validation.py         # Input validation tests
│   └── test_workflows.py          # End-to-end workflow tests
└── fixtures/                      # Test data fixtures
    ├── __init__.py
    ├── user_fixtures.py
    ├── asset_fixtures.py
    └── request_fixtures.py
```

### Pytest Fixtures Plan

**Core Fixtures**:
```python
@pytest.fixture
def app():
    """Create test Flask application."""

@pytest.fixture
def client(app):
    """Create test client."""

@pytest.fixture
def db_session(app):
    """Create database session with transaction rollback."""

@pytest.fixture
def admin_user(db_session):
    """Create admin user for testing."""

@pytest.fixture
def technician_user(db_session):
    """Create technician user for testing."""

@pytest.fixture
def client_user(db_session):
    """Create client user for testing."""

@pytest.fixture
def admin_token(client, admin_user):
    """Get JWT token for admin user."""

@pytest.fixture
def technician_token(client, technician_user):
    """Get JWT token for technician user."""

@pytest.fixture
def client_token(client, client_user):
    """Get JWT token for client user."""

@pytest.fixture
def sample_asset(db_session, admin_user):
    """Create sample asset for testing."""

@pytest.fixture
def sample_request(db_session, client_user, sample_asset):
    """Create sample maintenance request for testing."""
```

---

## 📝 Test Examples

### Example 1: Authentication Test
```python
def test_register_user_success(client):
    """Test successful user registration."""
    response = client.post('/api/v1/auth/register', json={
        'email': 'newuser@example.com',
        'password': 'SecurePass123!',
        'first_name': 'New',
        'last_name': 'User',
        'role': 'client'
    })

    assert response.status_code == 201
    data = response.get_json()
    assert 'message' in data
    assert data['data']['email'] == 'newuser@example.com'

def test_login_success(client, client_user):
    """Test successful login."""
    response = client.post('/api/v1/auth/login', json={
        'email': client_user.email,
        'password': 'password123'
    })

    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['user']['id'] == client_user.id
```

### Example 2: Authorization Test
```python
def test_create_asset_as_admin_success(client, admin_token):
    """Test admin can create asset."""
    response = client.post('/api/v1/assets',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'name': 'Test Asset',
            'asset_tag': 'TEST-001',
            'category': 'IT Equipment',
            # ... other fields
        })

    assert response.status_code == 201

def test_create_asset_as_client_forbidden(client, client_token):
    """Test client cannot create asset."""
    response = client.post('/api/v1/assets',
        headers={'Authorization': f'Bearer {client_token}'},
        json={
            'name': 'Test Asset',
            'asset_tag': 'TEST-001',
            'category': 'IT Equipment',
        })

    assert response.status_code == 403
```

### Example 3: Validation Test
```python
def test_create_request_missing_required_fields(client, client_token):
    """Test request creation fails with missing required fields."""
    response = client.post('/api/v1/requests',
        headers={'Authorization': f'Bearer {client_token}'},
        json={
            'title': 'Test Request'
            # Missing: request_type, asset_id, description
        })

    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error']['code'] == 'VALIDATION_ERROR'
```

### Example 4: Workflow Test
```python
def test_complete_maintenance_request_workflow(
    client, admin_token, technician_token, client_token,
    sample_asset
):
    """Test complete maintenance request lifecycle."""
    # 1. Client creates request
    response = client.post('/api/v1/requests',
        headers={'Authorization': f'Bearer {client_token}'},
        json={
            'request_type': 'electrical',
            'asset_id': sample_asset.id,
            'title': 'Power Issue',
            'description': 'Server power failure',
            'priority': 'high',
            'voltage': '220V',
            'circuit_number': 'C15',
            'breaker_location': 'Panel A'
        })
    assert response.status_code == 201
    request_id = response.get_json()['data']['id']

    # 2. Admin assigns to technician
    response = client.post(f'/api/v1/requests/{request_id}/assign',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'technician_id': technician_user.id})
    assert response.status_code == 200

    # 3. Technician starts work
    response = client.post(f'/api/v1/requests/{request_id}/start',
        headers={'Authorization': f'Bearer {technician_token}'})
    assert response.status_code == 200

    # 4. Technician completes work
    response = client.post(f'/api/v1/requests/{request_id}/complete',
        headers={'Authorization': f'Bearer {technician_token}'},
        json={
            'completion_notes': 'Replaced breaker',
            'actual_hours': 2.5
        })
    assert response.status_code == 200

    # 5. Verify final state
    response = client.get(f'/api/v1/requests/{request_id}',
        headers={'Authorization': f'Bearer {client_token}'})
    data = response.get_json()
    assert data['data']['status'] == 'completed'
```

---

## 🔧 Testing Tools

### Required Packages
```
pytest==8.0.0
pytest-flask==1.3.0
pytest-cov==4.1.0
```

### Test Configuration (pytest.ini)
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-branch
```

---

## 📊 Coverage Goals

### Target Coverage by Module
- **Controllers**: >85%
- **Middleware**: >90%
- **Schemas**: >80%
- **Overall**: >80%

### Coverage Exclusions
- Configuration files (config.py)
- Database migrations
- __init__.py files
- Development scripts

---

## ✅ Testing Checklist

### Setup
- [ ] Create test directory structure
- [ ] Configure pytest with pytest.ini
- [ ] Create conftest.py with fixtures
- [ ] Set up test database configuration

### Authentication Tests
- [ ] Test user registration (valid, duplicate, invalid)
- [ ] Test user login (valid, invalid credentials)
- [ ] Test token refresh
- [ ] Test logout
- [ ] Test get current user

### Authorization Tests
- [ ] Test admin-only endpoints
- [ ] Test technician-only endpoints
- [ ] Test resource ownership
- [ ] Test unauthenticated access

### User Management Tests
- [ ] Test list users
- [ ] Test get user profile
- [ ] Test update profile
- [ ] Test change password
- [ ] Test list technicians

### Asset Management Tests
- [ ] Test create asset
- [ ] Test list assets
- [ ] Test get asset
- [ ] Test update asset condition
- [ ] Test assets needing maintenance
- [ ] Test asset statistics

### Request Management Tests
- [ ] Test create request (all types)
- [ ] Test list requests
- [ ] Test get request
- [ ] Test assign request
- [ ] Test start work
- [ ] Test complete work
- [ ] Test list unassigned

### Validation Tests
- [ ] Test missing required fields
- [ ] Test invalid field types
- [ ] Test invalid enum values
- [ ] Test length constraints
- [ ] Test email validation
- [ ] Test password complexity

### Workflow Tests
- [ ] Test complete request lifecycle
- [ ] Test multiple concurrent requests
- [ ] Test request reassignment
- [ ] Test asset condition tracking

### Coverage & Quality
- [ ] Run all tests
- [ ] Check coverage report
- [ ] Fix any failing tests
- [ ] Refactor duplicated test code
- [ ] Document test patterns

---

## 🚀 Implementation Plan

### Phase 4.1: Setup & Fixtures (Day 1)
1. Create test directory structure
2. Configure pytest
3. Create core fixtures (app, client, db)
4. Create user fixtures (admin, technician, client)
5. Create authentication token fixtures

### Phase 4.2: Authentication Tests (Day 1-2)
1. Write registration tests
2. Write login tests
3. Write token refresh tests
4. Write logout tests
5. Write get current user tests

### Phase 4.3: Authorization Tests (Day 2)
1. Write admin-only access tests
2. Write technician-only access tests
3. Write resource ownership tests
4. Write role hierarchy tests

### Phase 4.4: Resource Tests (Day 2-3)
1. Write user management endpoint tests
2. Write asset management endpoint tests
3. Write request management endpoint tests

### Phase 4.5: Validation Tests (Day 3)
1. Write validation tests for all schemas
2. Write error handling tests
3. Write edge case tests

### Phase 4.6: Workflow Tests (Day 3-4)
1. Write complete lifecycle tests
2. Write concurrent request tests
3. Write complex scenario tests

### Phase 4.7: Review & Refinement (Day 4)
1. Run all tests
2. Check coverage report
3. Fix failing tests
4. Refactor duplicated code
5. Create Phase 4 summary

---

## 📈 Expected Outcomes

### Test Statistics
- **Total Tests**: 50-60 integration tests
- **Test Categories**: 7 categories
- **Code Coverage**: >80% overall, >85% controllers
- **Test Execution Time**: <30 seconds

### Quality Metrics
- **Pass Rate**: 100%
- **Flaky Tests**: 0
- **Test Maintenance**: Easy (good fixtures)
- **Documentation**: Clear test names and docstrings

### Benefits
1. **Confidence** - Deploy knowing all endpoints work
2. **Regression Prevention** - Catch bugs before production
3. **Documentation** - Tests show how to use the API
4. **Maintainability** - Safe refactoring with test coverage
5. **Quality** - Production-ready code

---

## 🎯 Success Criteria

Phase 4 will be considered complete when:

✅ All 50+ integration tests written and passing
✅ >80% code coverage achieved
✅ All authentication flows tested
✅ All authorization scenarios tested
✅ All endpoints have positive and negative tests
✅ Complete workflow tests pass
✅ Documentation created (this plan + summary)
✅ No flaky or skipped tests

---

*Phase 4: API Testing Suite*
*Smart Maintenance Management System*
*Goal: Comprehensive integration testing of all API endpoints*
