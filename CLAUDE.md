# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Smart Maintenance Management System (SMMS)** is a full-stack maintenance operations platform demonstrating OOP principles and software design patterns in a real-world enterprise context.

**Tech Stack:**
- **Backend**: Flask (Python 3.x) + SQLAlchemy ORM + JWT Authentication
- **Frontend**: Blazor WebAssembly (C#) + Bootstrap/Tailwind
- **Database**: SQLite or SQL Server
- **Visualization**: Chart.js / Recharts for analytics dashboard

**User Roles:**
- **Admin**: Manages users, assets, assignments, monitors system via analytics dashboard
- **Technician**: Views and updates assigned maintenance jobs
- **Client**: Submits and tracks maintenance requests

## System Architecture

### Multi-Layer Backend Architecture

The backend follows strict **separation of concerns** across five layers:

```
backend/app/
├── models/          # ORM entities (User, Asset, MaintenanceRequest)
├── repositories/    # Data access abstraction (Repository Pattern)
├── services/        # Business logic + pattern orchestration
├── controllers/     # Flask Blueprints (thin HTTP handlers)
├── patterns/        # Reusable pattern implementations
└── routes/          # API registration (aggregates blueprints)
```

**Dependency Flow**: Controllers → Services → Repositories → Models

**Key Principle**: Controllers should be thin. All business logic lives in the service layer, which orchestrates patterns and repositories.

### Frontend Architecture

```
frontend/SmartMaintenance.Blazor/
├── Pages/          # Main views (Dashboard, Requests, Assets, Login, Register)
├── Components/     # Reusable UI (RequestCard, NotificationPanel)
├── Services/       # ApiService (REST calls), AuthService (JWT handling)
├── Models/         # C# DTOs mirroring backend models
└── wwwroot/        # Static assets
```

**Communication**: All backend communication goes through `ApiService.cs` using `HttpClient` for REST API calls.

## Design Patterns Integration

This system demonstrates **pattern composition** — multiple patterns working together to solve complex problems:

| Pattern | Location | Purpose |
|---------|----------|---------|
| **Factory** | `patterns/factory.py` | Creates specialized request types (Electrical, Plumbing, HVAC) |
| **Repository** | `repositories/` | Abstracts database operations for testability |
| **Service Layer** | `services/` | Orchestrates business logic and pattern interactions |
| **Observer** | `patterns/observer.py` | Notifies users when request status changes |
| **Strategy** | `patterns/strategy.py` | Pluggable notification channels (Email, SMS, In-App) |
| **Singleton** | `patterns/singleton.py`, `config.py` | Manages database connections and configuration |
| **Dependency Injection** | Throughout controllers/services | Enables flexibility and testability |

### Pattern Interaction Example

**Workflow**: When a maintenance request status changes:

1. **Controller** receives HTTP request, delegates to **Service Layer**
2. **Service** uses **Repository Pattern** to fetch and update request data
3. **Factory Pattern** determines request type (Electrical/Plumbing/HVAC) for specialized behavior
4. **Observer Pattern** detects status change, triggers notification event
5. **Strategy Pattern** selects notification method (Email vs SMS vs In-App)
6. **Singleton** provides centralized config (API keys, SMTP settings) to notification strategies

**The patterns aren't isolated** — they form a cohesive system where each pattern solves a specific concern.

## Development Commands

### Backend (Flask)

**Initial Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Run Development Server:**
```bash
python run.py
```

**Database Operations:**
```bash
flask db init                      # First-time setup
flask db migrate -m "description"  # Create migration
flask db upgrade                   # Apply migrations
flask db downgrade                 # Rollback last migration
```

**Testing:**
```bash
pytest                                      # All tests
pytest tests/test_services.py               # Specific file
pytest tests/test_services.py::test_name    # Single test
pytest -v                                   # Verbose output
pytest --cov=app                            # Coverage report
```

### Frontend (Blazor)

**Initial Setup:**
```bash
cd frontend/SmartMaintenance.Blazor
dotnet restore
```

**Run Development Server:**
```bash
dotnet run
# Or with watch mode:
dotnet watch run
```

**Build & Test:**
```bash
dotnet build                    # Compile
dotnet build --configuration Release
dotnet test                     # Run tests
dotnet test --logger "console;verbosity=detailed"
```

**Create New Components:**
```bash
# Razor components go in Components/ or Pages/
dotnet new razorcomponent -n ComponentName
```

## Core Entities & Relationships

**User** (role: Admin/Technician/Client)
- Has many: MaintenanceRequests (as submitter)
- Has many: MaintenanceRequests (as assigned technician)

**Asset** (equipment/facility being maintained)
- Has many: MaintenanceRequests
- Fields: category, location, condition, status

**MaintenanceRequest** (polymorphic base class)
- Belongs to: User (submitter)
- Belongs to: User (assigned technician)
- Belongs to: Asset
- Subtypes: ElectricalRequest, PlumbingRequest, HVACRequest
- Status flow: Submitted → Assigned → In Progress → Completed

**Factory creates specialized requests** based on type, each with unique validation and attributes.

## API Design Conventions

**Endpoint Structure:** `/api/v1/{resource}`

**Authentication:** JWT tokens in Authorization header (`Bearer <token>`)

**Standard Responses:**
- 200: Success with data
- 201: Created (with Location header)
- 400: Validation error
- 401: Unauthorized
- 403: Forbidden (authenticated but insufficient permissions)
- 404: Not found
- 500: Server error

**Blueprint Organization:**
- `user_controller.py` → `/api/v1/users`
- `request_controller.py` → `/api/v1/requests`
- `asset_controller.py` → `/api/v1/assets`

## Testing Strategy

**Unit Tests (Services):**
- Mock repositories using dependency injection
- Test business logic in isolation
- Test pattern implementations independently

**Integration Tests (Controllers):**
- Test actual HTTP endpoints with test database
- Verify request/response formats
- Test authentication/authorization

**Pattern Tests:**
- Factory: Verify correct subclass creation
- Observer: Verify notification triggers
- Strategy: Verify correct strategy selection

## Development Workflow

When implementing new features:

1. **Models First**: Define SQLAlchemy model with relationships
2. **Repository Layer**: Add CRUD methods to repository class
3. **Service Layer**: Implement business logic, integrate patterns
4. **Controller Layer**: Create Flask blueprint with endpoints
5. **Frontend Models**: Create matching C# DTOs in `Models/`
6. **API Service**: Add methods to `ApiService.cs` for new endpoints
7. **UI Components**: Build Blazor pages/components
8. **Testing**: Write tests for each layer

## Important Conventions

**Backend:**
- Repositories return model instances or None (not dicts)
- Services accept repositories via `__init__` (dependency injection)
- Controllers are thin — validation and logic belong in services
- Pattern implementations should be reusable and well-documented
- Use type hints throughout Python code

**Frontend:**
- All API calls go through `ApiService.cs` (don't scatter HttpClient usage)
- Handle JWT token refresh in `AuthService.cs`
- Use dependency injection for services in Blazor components
- Models should match backend structure exactly (snake_case → PascalCase)

**Notifications:**
- Observer pattern triggers events synchronously
- Strategy pattern executes notifications (potentially async)
- Failed notifications should log but not block request processing

## Configuration Management

Configuration follows Singleton pattern in `backend/app/config.py`:

**Environment-based configs:**
- Development: SQLite, debug mode, verbose logging
- Production: SQL Server, JWT secrets from environment variables

**Critical settings:**
- Database connection strings
- JWT secret keys and expiration times
- Notification API keys (email, SMS gateways)
- CORS origins for frontend

**Never commit**: API keys, JWT secrets, production connection strings
