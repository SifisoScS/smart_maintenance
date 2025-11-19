# Smart Maintenance Management System

A comprehensive web platform that helps organizations manage maintenance requests, track assets, assign technicians, and monitor job progress with Role-Based Access Control (RBAC).

## Tech Stack

- **Backend**: Flask (Python) + SQLAlchemy + JWT Authentication
- **Frontend**: Blazor WebAssembly (C#) + Bootstrap
- **Database**: SQLite
- **Features**: RBAC, Feature Flags, Analytics Dashboard, Pattern-based Architecture

## Quick Start

### First Time Setup

1. **Run the setup script** (creates database, sample data, and RBAC permissions):
   ```bash
   setup.bat
   ```

2. **Start the application** (starts both backend and frontend):
   ```bash
   start.bat
   ```

3. **Access the application**:
   - Frontend: http://localhost:5112
   - Backend API: http://127.0.0.1:5001

### Default Login Credentials

**Admin User:**
- Email: `admin@smartmaintenance.com`
- Password: `admin123`
- Has full system access with all RBAC permissions

**Technician:**
- Email: `john.tech@smartmaintenance.com`
- Password: `tech123`

**Client:**
- Email: `sarah.client@smartmaintenance.com`
- Password: `client123`

## Features

### ✅ Phase 1: Feature Flags System
- Dynamic feature toggling without redeployment
- User/role-based targeting
- Admin interface for flag management

### ✅ Phase 2: Enhanced RBAC (Role-Based Access Control)
- Granular permission system (31 permissions)
- 5 default roles: Super Admin, Admin, Manager, Technician, Client
- Permission enforcement on all API endpoints
- UI for role/permission management

### 🔄 Core Functionality
- Maintenance request management
- Asset tracking and maintenance history
- User management with different roles
- Real-time dashboard with analytics
- Notification system (Email, SMS, In-App)

## Project Structure

```
smart_maintenance/
├── backend/              # Flask API
│   ├── app/
│   │   ├── models/      # Database models
│   │   ├── repositories/# Data access layer
│   │   ├── services/    # Business logic
│   │   ├── controllers/ # API endpoints
│   │   ├── patterns/    # Design patterns
│   │   └── middleware/  # RBAC & Auth
│   ├── tests/           # Unit & Integration tests
│   ├── seed_data.py     # Sample data seeder
│   └── seed_rbac.py     # RBAC permissions seeder
│
├── frontend/            # Blazor WebAssembly
│   ├── Pages/          # Main views
│   ├── Services/       # API communication
│   └── Models/         # DTOs
│
├── setup.bat           # First-time setup
└── start.bat           # Start application
```

## Development

### Backend Only
```bash
cd backend
python run.py
```

### Frontend Only
```bash
cd frontend
dotnet watch run --launch-profile http
```

### Run Tests
```bash
cd backend
pytest                          # All tests
pytest tests/unit/             # Unit tests only
pytest tests/integration/      # Integration tests only
pytest --cov=app               # With coverage
```

## Design Patterns Implemented

- **Factory Pattern**: Creates specialized maintenance request types
- **Repository Pattern**: Abstracts data access
- **Service Layer Pattern**: Encapsulates business logic
- **Observer Pattern**: Event-driven notifications
- **Strategy Pattern**: Pluggable notification channels
- **Singleton Pattern**: Database connection management
- **Dependency Injection**: Throughout controllers/services

## RBAC Permissions

The system includes 31 granular permissions across 7 resources:

- **Requests**: view, create, edit, delete, assign, start, complete
- **Assets**: view, create, edit, delete, update_condition, view_history
- **Users**: view, create, edit, delete, assign_roles, remove_roles
- **Roles**: view, manage
- **Permissions**: view, manage
- **Feature Flags**: view, toggle, manage
- **Analytics**: view_dashboard, view_reports, export_data
- **System**: view_audit_logs

## Troubleshooting

### Dashboard shows no data
Run the setup script to ensure admin user has RBAC permissions:
```bash
setup.bat
```

### "Permission denied" errors
The admin user needs the Super Admin role assigned. Run:
```bash
cd backend
python assign_admin_role.py
```

### Both servers not starting
Use the unified startup script:
```bash
start.bat
```

## API Documentation

Base URL: `http://127.0.0.1:5001/api/v1`

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token

### Maintenance Requests
- `GET /requests` - List all requests (requires `view_requests`)
- `POST /requests` - Create request (requires `create_requests`)
- `PATCH /requests/:id` - Update request (requires `edit_requests`)
- `DELETE /requests/:id` - Delete request (requires `delete_requests`)

### Assets
- `GET /assets` - List assets (requires `view_assets`)
- `POST /assets` - Create asset (requires `create_assets`)
- `PATCH /assets/:id` - Update asset (requires `edit_assets`)

### Users & RBAC
- `GET /users` - List users (requires `view_users`)
- `GET /roles` - List roles (requires `view_roles`)
- `GET /permissions` - List permissions (requires `view_permissions`)
- `POST /roles/user/:id/assign` - Assign role (requires `assign_roles`)

## License

MIT
