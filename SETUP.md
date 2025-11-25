# Smart Maintenance Management System - Setup Guide

Complete guide for cloning and running the Smart Maintenance Management System on your machine.

## Table of Contents
- [Project Overview](#project-overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup Instructions](#detailed-setup-instructions)
- [Database Configuration](#database-configuration)
- [Running the Application](#running-the-application)
- [Default User Accounts](#default-user-accounts)
- [Features Overview](#features-overview)
- [Troubleshooting](#troubleshooting)
- [Development Workflow](#development-workflow)

---

## Project Overview

**Smart Maintenance Management System (SMMS)** is a full-stack enterprise maintenance operations platform featuring:

- **Zero-cost predictive maintenance** with AI-ready architecture
- **Multi-tenant support** with complete data isolation
- **Role-based access control** (Admin, Technician, Client)
- **Smart technician assignment** with workload optimization
- **Real-time analytics** and maintenance scheduling
- **Comprehensive asset health monitoring**

### Tech Stack
- **Backend**: Flask (Python 3.8+) + SQLAlchemy ORM + PostgreSQL
- **Frontend**: Blazor WebAssembly (C# .NET 6.0+)
- **Authentication**: JWT tokens with refresh capability
- **Database**: PostgreSQL (or SQLite for development)

---

## Prerequisites

Ensure you have the following installed:

### Required Software

1. **Python 3.8 or higher**
   ```bash
   python --version
   ```

2. **Node.js 14+ and npm** (for frontend build tools)
   ```bash
   node --version
   npm --version
   ```

3. **.NET SDK 6.0 or higher**
   ```bash
   dotnet --version
   ```

4. **PostgreSQL 12+ or SQLite** (recommended: PostgreSQL for production features)
   - Download PostgreSQL: https://www.postgresql.org/download/
   - Default port: 5432
   - Remember your postgres user password during installation

5. **Git**
   ```bash
   git --version
   ```

### Optional but Recommended

- **Visual Studio Code** with Python and C# extensions
- **Postman** or **Insomnia** for API testing
- **pgAdmin 4** for PostgreSQL database management

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/smart_maintenance.git
cd smart_maintenance
```

### 2. Backend Setup (5 minutes)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (Command Prompt):
venv\Scripts\activate
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up database (see Database Configuration section below)
flask db upgrade

# Run backend server
python run.py
```

Backend will run on: **http://localhost:5000**

### 3. Frontend Setup (3 minutes)

Open a **new terminal** (keep backend running):

```bash
cd frontend

# Restore dependencies
dotnet restore

# Run frontend
dotnet run
```

Frontend will run on: **http://localhost:5112**

### 4. Access the Application

Navigate to: **http://localhost:5112**

**Default Admin Login:**
- Email: `admin@smartmaintenance.com`
- Password: `Admin123!`

---

## Detailed Setup Instructions

### Step 1: Backend Configuration

#### 1.1 Create Virtual Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### 1.2 Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Key dependencies installed:**
- Flask 2.3.x (web framework)
- Flask-SQLAlchemy (ORM)
- Flask-Migrate (database migrations)
- Flask-JWT-Extended (authentication)
- Flask-CORS (cross-origin support)
- psycopg2-binary (PostgreSQL adapter)
- python-dotenv (environment variables)

#### 1.3 Configure Environment Variables

Create `.env` file in `backend/` directory:

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this-in-production

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/smart_maintenance

# OR for SQLite (development only):
# DATABASE_URL=sqlite:///smart_maintenance.db

# CORS Configuration
CORS_ORIGINS=http://localhost:5112,http://localhost:5113

# Application Settings
DEBUG=True
TESTING=False
```

**Important:** Change `SECRET_KEY` and `JWT_SECRET_KEY` to random strings in production!

Generate secure keys:
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Database Configuration

### Option 1: PostgreSQL (Recommended)

#### Step 1: Install PostgreSQL

Download and install from: https://www.postgresql.org/download/

During installation:
- Set postgres user password (remember this!)
- Default port: 5432
- Include pgAdmin 4 (database management GUI)

#### Step 2: Create Database

**Using pgAdmin 4:**
1. Open pgAdmin 4
2. Connect to PostgreSQL server (localhost)
3. Right-click "Databases" → Create → Database
4. Database name: `smart_maintenance`
5. Owner: postgres
6. Click "Save"

**Using Command Line:**
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE smart_maintenance;

# Exit
\q
```

#### Step 3: Update Database URL

In `backend/.env`:
```env
DATABASE_URL=postgresql://postgres:YourPassword@localhost:5432/smart_maintenance
```

Replace `YourPassword` with your postgres password.

#### Step 4: Run Migrations

```bash
cd backend
# Activate virtual environment first!

# Initialize migrations (only first time)
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration to database
flask db upgrade
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> abc123def456, Initial migration
```

#### Step 5: Verify Database Setup

Check tables created:
```bash
psql -U postgres -d smart_maintenance -c "\dt"
```

**Expected tables:**
- users
- assets
- maintenance_requests
- notifications
- alembic_version (migration tracking)

### Option 2: SQLite (Development Only)

For quick testing without PostgreSQL:

In `backend/.env`:
```env
DATABASE_URL=sqlite:///smart_maintenance.db
```

Then run migrations:
```bash
flask db upgrade
```

**Note:** SQLite doesn't support all PostgreSQL features (enums, advanced queries). Use PostgreSQL for production.

---

### Seeding the Database (Optional)

Create initial test data:

Create `backend/seed_data.py`:

```python
from app import create_app, db
from app.models.user import User, UserRole
from app.models.asset import Asset, AssetCondition, AssetStatus
from werkzeug.security import generate_password_hash
from datetime import datetime, date

app = create_app()

with app.app_context():
    # Create admin user
    admin = User(
        email='admin@smartmaintenance.com',
        password_hash=generate_password_hash('Admin123!'),
        full_name='System Administrator',
        role=UserRole.ADMIN,
        is_active=True,
        tenant_id=1
    )

    # Create technician
    tech = User(
        email='technician@smartmaintenance.com',
        password_hash=generate_password_hash('Tech123!'),
        full_name='John Technician',
        role=UserRole.TECHNICIAN,
        is_active=True,
        tenant_id=1
    )

    # Create client
    client = User(
        email='client@smartmaintenance.com',
        password_hash=generate_password_hash('Client123!'),
        full_name='Jane Client',
        role=UserRole.CLIENT,
        is_active=True,
        tenant_id=1
    )

    db.session.add_all([admin, tech, client])
    db.session.commit()

    # Create sample asset
    asset = Asset(
        name='Main HVAC System',
        asset_tag='HVAC-001',
        category='HVAC',
        location='Building A - Floor 1',
        condition=AssetCondition.GOOD,
        status=AssetStatus.OPERATIONAL,
        purchase_date=date(2020, 1, 15),
        tenant_id=1
    )

    db.session.add(asset)
    db.session.commit()

    print("✅ Database seeded successfully!")
    print("\nDefault Accounts:")
    print("Admin: admin@smartmaintenance.com / Admin123!")
    print("Technician: technician@smartmaintenance.com / Tech123!")
    print("Client: client@smartmaintenance.com / Client123!")
```

Run seeding:
```bash
cd backend
python seed_data.py
```

---

### Step 2: Frontend Configuration

#### 2.1 Navigate to Frontend Directory

```bash
cd frontend
```

#### 2.2 Restore .NET Dependencies

```bash
dotnet restore
```

**Packages restored:**
- Microsoft.AspNetCore.Components.WebAssembly
- Microsoft.AspNetCore.Components.WebAssembly.DevServer
- System.Net.Http.Json
- Microsoft.Extensions.Http

#### 2.3 Configure API Base URL

Open `frontend/wwwroot/appsettings.json`:

```json
{
  "ApiBaseUrl": "http://localhost:5000/api/v1",
  "AppSettings": {
    "ApplicationName": "Smart Maintenance Management System",
    "Version": "1.0.0"
  }
}
```

**For production:** Update `ApiBaseUrl` to your production backend URL.

#### 2.4 Build Frontend (Optional)

```bash
# Development build
dotnet build

# Production build
dotnet build --configuration Release
```

---

## Running the Application

### Development Mode (Recommended)

Run both backend and frontend simultaneously.

#### Terminal 1: Backend

```bash
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Run Flask development server
python run.py
```

**Backend runs on:** http://localhost:5000

**API documentation:** http://localhost:5000/api/v1/health

#### Terminal 2: Frontend

```bash
cd frontend

# Run Blazor development server
dotnet run

# Or with hot reload:
dotnet watch run
```

**Frontend runs on:** http://localhost:5112

**Note:** `dotnet watch run` enables hot reload - changes to .razor files automatically refresh the browser.

### Production Mode

#### Backend (Production)

```bash
# Use gunicorn (install first: pip install gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

#### Frontend (Production)

```bash
# Build for production
dotnet publish -c Release -o ./publish

# Serve with a web server (nginx, IIS, Apache)
```

---

## Default User Accounts

After seeding the database, these accounts are available:

### Administrator Account
- **Email:** `admin@smartmaintenance.com`
- **Password:** `Admin123!`
- **Role:** Admin
- **Permissions:** Full system access, analytics dashboard, predictive insights, user management

### Technician Account
- **Email:** `technician@smartmaintenance.com`
- **Password:** `Tech123!`
- **Role:** Technician
- **Permissions:** View and update assigned maintenance requests

### Client Account
- **Email:** `client@smartmaintenance.com`
- **Password:** `Client123!`
- **Role:** Client
- **Permissions:** Submit and track maintenance requests

---

## Features Overview

### 🔮 Predictive Maintenance (Zero Cost)

**Access:** Admin Dashboard → Predictive Insights

**Features:**
- Asset health scoring (0-100 scale)
- Failure prediction with confidence intervals
- MTBF (Mean Time Between Failures) analysis
- Multi-factor risk assessment (Time 35%, Frequency 25%, Condition 25%, Age 15%)
- Maintenance schedule recommendations (30/60/90 days)
- Critical asset alerts

**How it works:**
1. Navigate to Admin Dashboard
2. Click "Predictive Maintenance Insights" card
3. View risk-scored assets sorted by urgency
4. See 30-day maintenance calendar
5. Review smart recommendations

**Technology:** Rule-based Strategy Pattern (upgradable to ML-based predictions)

### 🎯 Smart Technician Assignment

**Features:**
- Multi-factor technician scoring algorithm
- Workload-aware assignment (30% weight)
- Urgency alignment (25% weight)
- Performance tracking (15% weight)
- Availability calculation (10% weight)
- Load balancing recommendations

**Usage:**
- Automatic: System assigns best-fit technician on request creation
- Manual override: Admins can reassign via request details page

### 📊 Analytics Dashboard

**Admin-only features:**
- Total requests by status
- Asset condition distribution
- Technician workload visualization
- Request priority breakdown
- Maintenance trends over time
- System health overview

### 🔐 Multi-Tenant Architecture

**Features:**
- Complete data isolation per organization
- Tenant-specific user management
- Cross-tenant security enforcement
- Scalable to hundreds of organizations

**Field:** `tenant_id` on User, Asset, MaintenanceRequest models

---

## Troubleshooting

### Backend Issues

#### Issue: "No module named 'flask'"

**Solution:**
```bash
# Ensure virtual environment is activated
# Windows:
venv\Scripts\activate

# Then reinstall dependencies
pip install -r requirements.txt
```

#### Issue: "psycopg2 installation failed"

**Solution (Windows):**
```bash
pip install psycopg2-binary
```

**Solution (macOS/Linux):**
```bash
# Install PostgreSQL development files first
sudo apt-get install libpq-dev  # Ubuntu/Debian
brew install postgresql  # macOS

pip install psycopg2
```

#### Issue: Database connection error

**Check:**
1. PostgreSQL service is running:
   ```bash
   # Windows: Check Services app
   # Linux:
   sudo systemctl status postgresql
   ```

2. Database exists:
   ```bash
   psql -U postgres -c "\l" | grep smart_maintenance
   ```

3. Connection string in `.env` is correct

#### Issue: "Working outside of application context"

**Solution:** Always use `with app.app_context():` when running scripts:
```python
from app import create_app, db

app = create_app()
with app.app_context():
    # Your database operations here
    pass
```

#### Issue: Enum comparison errors

**Symptom:** `TypeError: 'UserRole' object is not iterable`

**Cause:** Comparing enum to string instead of enum object

**Fix:**
```python
# Wrong:
if user.role == 'admin':

# Correct:
from app.models.user import UserRole
if user.role == UserRole.ADMIN:
```

### Frontend Issues

#### Issue: "Failed to load insights: 500 Internal Server Error"

**Check:**
1. Backend is running on port 5000
2. Check backend terminal for error details
3. Verify API base URL in `appsettings.json`
4. Check browser console (F12) for details

#### Issue: CORS errors in browser console

**Solution:** Add frontend URL to CORS_ORIGINS in backend `.env`:
```env
CORS_ORIGINS=http://localhost:5112,http://localhost:5113
```

#### Issue: "Cannot reach backend API"

**Check:**
1. Backend running: `curl http://localhost:5000/api/v1/health`
2. Firewall not blocking port 5000
3. ApiService.cs has correct base URL

#### Issue: Blazor hot reload not working

**Solution:** Use `dotnet watch run` instead of `dotnet run`

### Database Migration Issues

#### Issue: "Target database is not up to date"

**Solution:**
```bash
flask db upgrade
```

#### Issue: Migration conflicts

**Solution:**
```bash
# Downgrade to previous version
flask db downgrade

# Delete problematic migration file in migrations/versions/
# Recreate migration
flask db migrate -m "New migration"

# Apply
flask db upgrade
```

#### Issue: Enum type errors (PostgreSQL)

**Symptom:** `UndefinedObject: type "userrole" does not exist`

**Solution:** Recreate database:
```bash
# Backup data first!
dropdb -U postgres smart_maintenance
createdb -U postgres smart_maintenance
flask db upgrade
```

---

## Development Workflow

### Making Changes

1. **Backend changes:**
   - Edit Python files in `backend/app/`
   - Restart Flask server to see changes (or use Flask debug mode)
   - Write tests in `backend/tests/`

2. **Frontend changes:**
   - Edit .razor files in `frontend/Pages/` or `frontend/Components/`
   - Blazor hot reload automatically updates browser
   - No restart needed with `dotnet watch run`

3. **Database schema changes:**
   ```bash
   # Make model changes in backend/app/models/
   # Create migration
   flask db migrate -m "Description of change"

   # Review migration file in migrations/versions/
   # Apply migration
   flask db upgrade
   ```

### Adding New API Endpoints

1. **Create service method** in `backend/app/services/`
2. **Add controller endpoint** in `backend/app/controllers/`
3. **Register blueprint** in `backend/app/__init__.py` (if new controller)
4. **Create C# DTOs** in `frontend/Models/`
5. **Add API method** to `frontend/Services/ApiService.cs`
6. **Create/update Razor page** in `frontend/Pages/`

### Testing

#### Backend Tests
```bash
cd backend
pytest                                    # All tests
pytest tests/test_services.py             # Specific file
pytest -v                                 # Verbose
pytest --cov=app                          # Coverage report
```

#### Frontend Tests
```bash
cd frontend
dotnet test
dotnet test --logger "console;verbosity=detailed"
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Description of changes"

# Push to remote
git push origin feature/your-feature-name

# Create pull request on GitHub
```

---

## Architecture Overview

### Backend Architecture (5 Layers)

```
backend/app/
├── models/          # SQLAlchemy ORM entities
│   ├── user.py      # User, UserRole enum
│   ├── asset.py     # Asset, AssetCondition, AssetStatus enums
│   └── request.py   # MaintenanceRequest, RequestStatus, RequestPriority enums
│
├── repositories/    # Data access layer (Repository Pattern)
│   ├── user_repository.py
│   ├── asset_repository.py
│   └── request_repository.py
│
├── services/        # Business logic orchestration
│   ├── prediction_strategy.py         # Strategy Pattern for predictions
│   ├── asset_health_service.py        # Health analysis
│   ├── smart_assignment_service.py    # Technician assignment
│   └── predictive_maintenance_service.py  # Main orchestration facade
│
├── controllers/     # Flask Blueprints (HTTP handlers)
│   ├── user_controller.py
│   ├── asset_controller.py
│   ├── request_controller.py
│   └── predictive_controller.py       # 12 predictive endpoints
│
├── patterns/        # Reusable pattern implementations
│   ├── factory.py   # Factory Pattern (request types)
│   ├── observer.py  # Observer Pattern (notifications)
│   ├── strategy.py  # Strategy Pattern (notification channels)
│   └── singleton.py # Singleton Pattern (config, DB connection)
│
└── config.py        # Application configuration
```

### Frontend Architecture

```
frontend/
├── Pages/           # Main views
│   ├── Dashboard.razor
│   ├── Requests.razor
│   ├── Assets.razor
│   ├── PredictiveInsights.razor  # Predictive maintenance dashboard
│   ├── Login.razor
│   └── Register.razor
│
├── Components/      # Reusable UI components
│   ├── RequestCard.razor
│   └── NotificationPanel.razor
│
├── Services/        # Business services
│   ├── ApiService.cs       # REST API calls
│   └── AuthService.cs      # JWT authentication
│
├── Models/          # C# DTOs
│   ├── UserModel.cs
│   ├── AssetModel.cs
│   ├── RequestModel.cs
│   └── PredictiveInsightsModel.cs
│
└── wwwroot/         # Static assets
    ├── css/
    ├── js/
    └── appsettings.json
```

### Design Patterns Used

| Pattern | Purpose | Location |
|---------|---------|----------|
| **Strategy** | Swap prediction algorithms (Rule-based ↔ ML-based) | `services/prediction_strategy.py` |
| **Repository** | Abstract database operations | `repositories/` |
| **Factory** | Create specialized request types | `patterns/factory.py` |
| **Observer** | Event-driven notifications | `patterns/observer.py` |
| **Singleton** | Single DB connection, config | `patterns/singleton.py` |
| **Facade** | Simplify complex subsystems | `services/predictive_maintenance_service.py` |
| **Dependency Injection** | Flexible, testable services | Throughout controllers/services |

---

## API Documentation

### Base URL
```
http://localhost:5000/api/v1
```

### Authentication

All endpoints (except login/register) require JWT token:

```http
Authorization: Bearer <your-jwt-token>
```

### Key Endpoints

#### Authentication
- `POST /auth/login` - Login (returns JWT)
- `POST /auth/register` - Register new user
- `POST /auth/refresh` - Refresh JWT token

#### Users
- `GET /users` - List users (admin only)
- `GET /users/<id>` - Get user details
- `PUT /users/<id>` - Update user
- `DELETE /users/<id>` - Delete user (admin only)

#### Assets
- `GET /assets` - List assets
- `POST /assets` - Create asset
- `GET /assets/<id>` - Get asset details
- `PUT /assets/<id>` - Update asset
- `DELETE /assets/<id>` - Delete asset

#### Maintenance Requests
- `GET /requests` - List requests
- `POST /requests` - Create request
- `GET /requests/<id>` - Get request details
- `PUT /requests/<id>` - Update request
- `PUT /requests/<id>/assign` - Assign technician

#### Predictive Maintenance (12 Endpoints)
- `GET /predictive/health/asset/<id>` - Individual asset health
- `GET /predictive/health/all` - All assets health analysis
- `GET /predictive/health/critical` - High-risk assets only
- `GET /predictive/schedule` - Maintenance schedule (30/60/90 days)
- `POST /predictive/schedule/create` - Create preventive maintenance
- `GET /predictive/workload` - Technician workload distribution
- `POST /predictive/assignment/auto/<id>` - Auto-assign request
- `GET /predictive/assignment/recommendations` - Load balancing suggestions
- `GET /predictive/dashboard` - Dashboard summary
- `GET /predictive/insights` - Complete predictive insights
- `GET /predictive/history/asset/<id>` - Historical trends
- `GET /predictive/history/trends` - Organization-wide trends

---

## Environment Variables Reference

### Flask Backend (.env)

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development  # or production
SECRET_KEY=<random-string-32-chars>
DEBUG=True  # False in production

# JWT Configuration
JWT_SECRET_KEY=<random-string-32-chars>
JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 hour in seconds
JWT_REFRESH_TOKEN_EXPIRES=2592000  # 30 days in seconds

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/smart_maintenance
# Or SQLite: sqlite:///smart_maintenance.db

# CORS
CORS_ORIGINS=http://localhost:5112,http://localhost:5113

# Application
TESTING=False
```

### Blazor Frontend (appsettings.json)

```json
{
  "ApiBaseUrl": "http://localhost:5000/api/v1",
  "AppSettings": {
    "ApplicationName": "Smart Maintenance Management System",
    "Version": "1.0.0"
  }
}
```

---

## Support and Contributing

### Getting Help

1. **Check this setup guide** for common issues
2. **Review error logs** in terminal output
3. **Check browser console** (F12) for frontend errors
4. **PostgreSQL logs** (usually in `/var/log/postgresql/`)

### Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open pull request

---

## License

This project is licensed under the MIT License.

---

## Credits

**Author:** Sifiso Shezi (ARISAN SIFISO)

**Technologies:**
- Flask (Pallets Projects)
- Blazor (Microsoft)
- PostgreSQL (PostgreSQL Global Development Group)
- SQLAlchemy (Mike Bayer)

---

## Appendix: Complete Command Reference

### Python/Flask Commands
```bash
# Virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Dependencies
pip install -r requirements.txt
pip freeze > requirements.txt

# Database migrations
flask db init
flask db migrate -m "message"
flask db upgrade
flask db downgrade

# Run server
python run.py
flask run
gunicorn -w 4 -b 0.0.0.0:5000 run:app  # Production

# Testing
pytest
pytest -v
pytest --cov=app
pytest tests/test_services.py
```

### .NET/Blazor Commands
```bash
# Dependencies
dotnet restore
dotnet clean

# Build
dotnet build
dotnet build --configuration Release

# Run
dotnet run
dotnet watch run  # With hot reload

# Publish
dotnet publish -c Release -o ./publish

# Testing
dotnet test
dotnet test --logger "console;verbosity=detailed"
```

### PostgreSQL Commands
```bash
# Connect to PostgreSQL
psql -U postgres

# List databases
\l

# Connect to database
\c smart_maintenance

# List tables
\dt

# Describe table
\d users

# Run SQL file
psql -U postgres -d smart_maintenance -f schema.sql

# Backup database
pg_dump -U postgres smart_maintenance > backup.sql

# Restore database
psql -U postgres smart_maintenance < backup.sql
```

### Git Commands
```bash
# Clone repository
git clone https://github.com/yourusername/smart_maintenance.git

# Create branch
git checkout -b feature/your-feature

# Stage changes
git add .
git add specific_file.py

# Commit
git commit -m "Your commit message"

# Push
git push origin feature/your-feature

# Pull latest changes
git pull origin main

# Check status
git status

# View history
git log
git log --oneline
```

---

**Last Updated:** 2025-01-25

**Version:** 1.0.0

**Ready to build amazing maintenance management systems! 🚀**
