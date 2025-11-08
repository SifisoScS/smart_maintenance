# Phase 3 Plan: API Layer & Controllers

**Status:** 📋 READY TO BEGIN
**Prerequisites:** ✅ Phase 1 & 2 Complete
**Estimated Duration:** 4-6 hours
**Complexity:** MEDIUM-HIGH

---

## Table of Contents

1. [Overview](#overview)
2. [Goals & Objectives](#goals--objectives)
3. [Architecture](#architecture)
4. [Implementation Plan](#implementation-plan)
5. [API Endpoints](#api-endpoints)
6. [Authentication & Authorization](#authentication--authorization)
7. [Input Validation](#input-validation)
8. [Error Handling](#error-handling)
9. [Testing Strategy](#testing-strategy)
10. [Success Criteria](#success-criteria)

---

## Overview

Phase 3 adds the **API Layer** (Controllers/Routes) to expose Phase 2 services as RESTful HTTP endpoints. This layer handles HTTP request/response, authentication, authorization, input validation, and error formatting.

**What We're Building:**
- RESTful API endpoints for all services
- JWT-based authentication
- Role-based access control (RBAC)
- Request/response validation
- Standardized error responses
- API documentation (OpenAPI/Swagger)

**Technologies:**
- Flask (existing)
- Flask-JWT-Extended (JWT tokens)
- Flask-CORS (Cross-origin support)
- Marshmallow (Serialization/validation)
- Swagger UI (API documentation)

---

## Goals & Objectives

### Primary Goals

1. **Expose Services via REST API**
   - Create HTTP endpoints for all Phase 2 services
   - Follow RESTful conventions
   - Proper HTTP status codes

2. **Implement Authentication**
   - JWT token-based authentication
   - Login/logout endpoints
   - Token refresh mechanism
   - Secure password handling (already done in Phase 2)

3. **Implement Authorization**
   - Role-based access control (RBAC)
   - Protect admin-only endpoints
   - Validate user permissions

4. **Add Input Validation**
   - Request body validation
   - Query parameter validation
   - Return 400 for invalid input

5. **Standardize Responses**
   - Consistent response format
   - Proper HTTP status codes
   - Meaningful error messages

### Secondary Goals

6. **API Documentation**
   - OpenAPI/Swagger specification
   - Interactive API testing
   - Request/response examples

7. **CORS Support**
   - Enable cross-origin requests
   - Configure allowed origins
   - Prepare for frontend integration

---

## Architecture

### Layered Architecture (Complete Stack)

```
┌─────────────────────────────────────────┐
│         Frontend (Phase 5)              │
│      React/Vue/Angular                  │
└─────────────────────────────────────────┘
                 ↕ HTTP/JSON
┌─────────────────────────────────────────┐
│      API Layer (Phase 3) ← NEW          │
│   - Controllers/Routes                  │
│   - Authentication (JWT)                │
│   - Authorization (RBAC)                │
│   - Input Validation                    │
│   - Error Handling                      │
└─────────────────────────────────────────┘
                 ↕ Function Calls
┌─────────────────────────────────────────┐
│    Service Layer (Phase 2)              │
│   - Business Logic                      │
│   - Orchestration                       │
│   - Validation                          │
└─────────────────────────────────────────┘
                 ↕ Function Calls
┌─────────────────────────────────────────┐
│  Repository Layer (Phase 1)             │
│   - Data Access                         │
│   - Query Building                      │
└─────────────────────────────────────────┘
                 ↕ SQL Queries
┌─────────────────────────────────────────┐
│      Database (PostgreSQL)              │
└─────────────────────────────────────────┘
```

### Component Structure

```
backend/
├── app/
│   ├── controllers/          ← NEW (Phase 3)
│   │   ├── __init__.py
│   │   ├── auth_controller.py      # Login, logout, refresh
│   │   ├── user_controller.py      # User management
│   │   ├── asset_controller.py     # Asset management
│   │   ├── request_controller.py   # Maintenance requests
│   │   └── notification_controller.py  # Notifications
│   │
│   ├── middleware/           ← NEW (Phase 3)
│   │   ├── __init__.py
│   │   ├── auth_middleware.py      # JWT authentication
│   │   ├── rbac_middleware.py      # Role-based access
│   │   └── error_handler.py        # Global error handling
│   │
│   ├── schemas/              ← NEW (Phase 3)
│   │   ├── __init__.py
│   │   ├── user_schemas.py         # User validation schemas
│   │   ├── asset_schemas.py        # Asset validation schemas
│   │   └── request_schemas.py      # Request validation schemas
│   │
│   ├── services/             (Phase 2 - exists)
│   ├── repositories/         (Phase 1 - exists)
│   └── models/               (Phase 1 - exists)
│
└── tests/
    └── integration/          ← NEW (Phase 3)
        ├── test_auth_api.py
        ├── test_user_api.py
        ├── test_asset_api.py
        └── test_request_api.py
```

---

## Implementation Plan

### Step 1: Setup & Dependencies (30 minutes)

**Install Packages:**
```bash
pip install flask-jwt-extended flask-cors marshmallow flask-swagger-ui
```

**Configure Flask App:**
- Add JWT secret key
- Configure CORS
- Register error handlers

### Step 2: Authentication System (1 hour)

**Create:**
1. JWT configuration
2. Auth middleware (token validation)
3. Login endpoint (POST /api/v1/auth/login)
4. Logout endpoint (POST /api/v1/auth/logout)
5. Refresh token endpoint (POST /api/v1/auth/refresh)
6. Get current user endpoint (GET /api/v1/auth/me)

**Features:**
- Token expiration (15 min access, 30 day refresh)
- Token blacklisting (logout)
- Password validation
- Return user info + tokens

### Step 3: Authorization System (30 minutes)

**Create:**
1. RBAC decorators (@admin_required, @technician_required)
2. Permission checker middleware
3. Role validation

**Features:**
- Role hierarchy (admin > technician > client)
- Protect admin-only endpoints
- Return 403 for unauthorized access

### Step 4: User Management Endpoints (45 minutes)

**Endpoints:**
```
POST   /api/v1/users              - Register user (public)
GET    /api/v1/users              - List users (admin only)
GET    /api/v1/users/:id          - Get user (self or admin)
PUT    /api/v1/users/:id          - Update user (self or admin)
DELETE /api/v1/users/:id          - Delete user (admin only)
GET    /api/v1/users/technicians  - List technicians (authenticated)
POST   /api/v1/users/:id/password - Change password (self only)
```

### Step 5: Asset Management Endpoints (30 minutes)

**Endpoints:**
```
POST   /api/v1/assets             - Create asset (admin only)
GET    /api/v1/assets             - List assets (authenticated)
GET    /api/v1/assets/:id         - Get asset (authenticated)
PUT    /api/v1/assets/:id         - Update asset (admin only)
DELETE /api/v1/assets/:id         - Delete asset (admin only)
GET    /api/v1/assets/maintenance - Assets needing maintenance (authenticated)
GET    /api/v1/assets/statistics  - Asset statistics (authenticated)
PATCH  /api/v1/assets/:id/condition - Update condition (technician/admin)
```

### Step 6: Maintenance Request Endpoints (1 hour)

**Endpoints:**
```
POST   /api/v1/requests           - Create request (authenticated)
GET    /api/v1/requests           - List requests (filtered by role)
GET    /api/v1/requests/:id       - Get request (authenticated)
PUT    /api/v1/requests/:id       - Update request (creator or admin)
DELETE /api/v1/requests/:id       - Delete request (admin only)

POST   /api/v1/requests/:id/assign    - Assign request (admin only)
POST   /api/v1/requests/:id/start     - Start work (assigned technician)
POST   /api/v1/requests/:id/complete  - Complete work (assigned technician)

GET    /api/v1/requests/unassigned         - Unassigned requests (admin)
GET    /api/v1/requests/my-requests        - Current user's requests
GET    /api/v1/technicians/:id/workload   - Technician workload (admin)
```

### Step 7: Input Validation Schemas (45 minutes)

**Create Marshmallow schemas for:**
- User registration/update
- Asset creation/update
- Request creation
- Login credentials
- Password change

**Features:**
- Required field validation
- Type validation
- Enum validation
- Custom validators

### Step 8: Error Handling (30 minutes)

**Standardize errors:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": {
      "email": ["Not a valid email address"],
      "password": ["Password must be at least 8 characters"]
    }
  },
  "status": 400
}
```

**Error types:**
- 400 Bad Request (validation errors)
- 401 Unauthorized (no/invalid token)
- 403 Forbidden (insufficient permissions)
- 404 Not Found (resource not found)
- 500 Internal Server Error (unexpected errors)

### Step 9: API Documentation (30 minutes)

**Add:**
- OpenAPI/Swagger specification
- Swagger UI at /api/docs
- Request/response examples
- Authentication guide

### Step 10: Integration Tests (1 hour)

**Test:**
- Authentication flow (login, access protected route, logout)
- Authorization (admin-only routes)
- CRUD operations for each resource
- Error responses (400, 401, 403, 404)
- End-to-end workflows

---

## API Endpoints

### Complete API Specification

#### Authentication Endpoints

```
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
GET    /api/v1/auth/me
```

#### User Endpoints

```
POST   /api/v1/users                    [Public]
GET    /api/v1/users                    [Admin]
GET    /api/v1/users/:id                [Self/Admin]
PUT    /api/v1/users/:id                [Self/Admin]
DELETE /api/v1/users/:id                [Admin]
GET    /api/v1/users/technicians        [Authenticated]
POST   /api/v1/users/:id/password       [Self]
```

#### Asset Endpoints

```
POST   /api/v1/assets                   [Admin]
GET    /api/v1/assets                   [Authenticated]
GET    /api/v1/assets/:id               [Authenticated]
PUT    /api/v1/assets/:id               [Admin]
DELETE /api/v1/assets/:id               [Admin]
GET    /api/v1/assets/maintenance       [Authenticated]
GET    /api/v1/assets/statistics        [Authenticated]
PATCH  /api/v1/assets/:id/condition     [Technician/Admin]
```

#### Maintenance Request Endpoints

```
POST   /api/v1/requests                 [Authenticated]
GET    /api/v1/requests                 [Authenticated]
GET    /api/v1/requests/:id             [Authenticated]
PUT    /api/v1/requests/:id             [Creator/Admin]
DELETE /api/v1/requests/:id             [Admin]
POST   /api/v1/requests/:id/assign      [Admin]
POST   /api/v1/requests/:id/start       [Assigned Technician]
POST   /api/v1/requests/:id/complete    [Assigned Technician]
GET    /api/v1/requests/unassigned      [Admin]
GET    /api/v1/requests/my-requests     [Authenticated]
GET    /api/v1/technicians/:id/workload [Admin]
```

#### Notification Endpoints (Bonus)

```
GET    /api/v1/notifications            [Authenticated]
GET    /api/v1/notifications/:id        [Authenticated]
PATCH  /api/v1/notifications/:id/read   [Authenticated]
```

---

## Authentication & Authorization

### JWT Token Structure

**Access Token (15 min expiry):**
```json
{
  "user_id": 1,
  "email": "admin@example.com",
  "role": "admin",
  "exp": 1699564800,
  "type": "access"
}
```

**Refresh Token (30 day expiry):**
```json
{
  "user_id": 1,
  "exp": 1702243200,
  "type": "refresh"
}
```

### Authorization Rules

**Role Hierarchy:**
```
admin > technician > client
```

**Permission Matrix:**

| Endpoint                  | Admin | Technician | Client |
|---------------------------|-------|------------|--------|
| POST /users               | ✅    | ✅         | ✅     |
| GET /users (all)          | ✅    | ❌         | ❌     |
| DELETE /users/:id         | ✅    | ❌         | ❌     |
| POST /assets              | ✅    | ❌         | ❌     |
| GET /assets               | ✅    | ✅         | ✅     |
| PATCH /assets/:id/condition | ✅  | ✅         | ❌     |
| POST /requests            | ✅    | ✅         | ✅     |
| POST /requests/:id/assign | ✅    | ❌         | ❌     |
| POST /requests/:id/start  | ✅ (any) | ✅ (own) | ❌ |
| POST /requests/:id/complete | ✅ (any) | ✅ (own) | ❌ |

### Decorators

```python
@jwt_required()               # Any authenticated user
@admin_required()             # Admin only
@technician_required()        # Technician or Admin
@owner_or_admin_required()    # Resource owner or Admin
```

---

## Input Validation

### Marshmallow Schemas

**UserRegistrationSchema:**
```python
class UserRegistrationSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    first_name = fields.String(required=True, validate=validate.Length(min=1))
    last_name = fields.String(required=True, validate=validate.Length(min=1))
    role = fields.String(required=True, validate=validate.OneOf(['admin', 'technician', 'client']))
    phone = fields.String()
    department = fields.String()
```

**RequestCreationSchema:**
```python
class RequestCreationSchema(Schema):
    request_type = fields.String(required=True, validate=validate.OneOf(['electrical', 'plumbing', 'hvac']))
    asset_id = fields.Integer(required=True, validate=validate.Range(min=1))
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(required=True, validate=validate.Length(min=1))
    priority = fields.String(validate=validate.OneOf(['low', 'medium', 'high', 'urgent']))

    # Type-specific fields (optional)
    voltage = fields.String()
    circuit_number = fields.String()
    # ... etc
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  },
  "status": 400
}
```

### Error Codes

```python
VALIDATION_ERROR = 400       # Invalid input
UNAUTHORIZED = 401           # No/invalid token
FORBIDDEN = 403              # Insufficient permissions
NOT_FOUND = 404              # Resource not found
CONFLICT = 409               # Duplicate resource
INTERNAL_ERROR = 500         # Unexpected error
```

### Global Error Handler

```python
@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Invalid input",
            "details": e.messages
        },
        "status": 400
    }), 400
```

---

## Testing Strategy

### Integration Tests

**Test Coverage:**
- ✅ Authentication flow (login, access, logout)
- ✅ Authorization (admin-only routes return 403)
- ✅ CRUD operations for each resource
- ✅ Input validation (400 errors)
- ✅ Error handling (401, 403, 404, 500)
- ✅ End-to-end workflows

**Test Structure:**
```python
def test_login_success(client):
    """Test successful login returns tokens"""

def test_create_request_as_client(client, client_token):
    """Test client can create request"""

def test_assign_request_as_admin(client, admin_token):
    """Test admin can assign request"""

def test_assign_request_as_client_fails(client, client_token):
    """Test client cannot assign request (403)"""
```

**Tools:**
- pytest for test framework
- Flask test client for HTTP requests
- Fixtures for authentication tokens
- Database rollback between tests

---

## Success Criteria

### Phase 3 Complete When:

✅ All endpoints implemented (25+ endpoints)
✅ JWT authentication working
✅ RBAC working (admin-only routes protected)
✅ Input validation working (returns 400 for invalid input)
✅ Error handling standardized
✅ Integration tests passing (50+ tests)
✅ API documentation available
✅ Postman collection created
✅ Code review passed

### Quality Metrics

- **Test Coverage:** 80%+ for controllers
- **Response Time:** <100ms for simple operations
- **Error Rate:** 0% for valid requests
- **Documentation:** All endpoints documented

---

## Timeline

| Step | Duration | Status |
|------|----------|--------|
| 1. Setup & Dependencies | 30 min | ⏳ Pending |
| 2. Authentication System | 1 hour | ⏳ Pending |
| 3. Authorization System | 30 min | ⏳ Pending |
| 4. User Endpoints | 45 min | ⏳ Pending |
| 5. Asset Endpoints | 30 min | ⏳ Pending |
| 6. Request Endpoints | 1 hour | ⏳ Pending |
| 7. Validation Schemas | 45 min | ⏳ Pending |
| 8. Error Handling | 30 min | ⏳ Pending |
| 9. API Documentation | 30 min | ⏳ Pending |
| 10. Integration Tests | 1 hour | ⏳ Pending |
| **Total** | **~6 hours** | ⏳ Pending |

---

## Next Steps

1. **Review this plan** - Confirm approach
2. **Install dependencies** - Set up packages
3. **Begin Step 1** - Setup & configuration
4. **Implement incrementally** - One step at a time
5. **Test continuously** - Test each endpoint as built

---

**Ready to begin Phase 3?** 🚀

**Previous Phase:** Phase 2 - Service Layer (COMPLETE ✅)
**Current Phase:** Phase 3 - API Layer (READY 📋)
**Next Phase:** Phase 4 - Advanced Features

---

**Generated:** 2025-11-08
**Author:** Claude Code
**Project:** Smart Maintenance Management System
