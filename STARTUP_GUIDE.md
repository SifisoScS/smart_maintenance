# 🚀 Smart Maintenance Management System - Startup Guide

## Prerequisites

Before running the application, ensure you have:

✅ Python 3.11 installed
✅ PostgreSQL installed and running
✅ PostgreSQL database `smart_maintenance` created
✅ Virtual environment created in `backend/venv/`
✅ All dependencies installed

---

## Step-by-Step Instructions

### 1️⃣ Navigate to Backend Directory

```bash
cd backend
```

### 2️⃣ Activate Virtual Environment

**Windows (Git Bash/MinGW):**
```bash
source venv/Scripts/activate
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` in your terminal prompt.

### 3️⃣ Verify Dependencies are Installed

```bash
pip list | grep Flask
```

You should see Flask, SQLAlchemy, and other packages.

If not installed:
```bash
pip install -r requirements.txt
```

### 4️⃣ Seed the Database with Sample Data

```bash
python seed_data.py
```

This will create:
- **6 users** (1 admin, 3 technicians, 2 clients)
- **5 assets** (HVAC units, electrical fixtures, plumbing)
- **5 maintenance requests** (various statuses)

### 5️⃣ Start the Flask Development Server

```bash
python run.py
```

You should see output like:
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
Press CTRL+C to quit
```

### 6️⃣ Test the API

Open your browser or use `curl` to test the endpoints:

**Health Check:**
```bash
curl http://localhost:5000/api/v1/health
```

**System Statistics:**
```bash
curl http://localhost:5000/api/v1/stats
```

**API Root:**
```bash
curl http://localhost:5000/api/v1/
```

---

## 📋 Sample User Credentials

Use these credentials to test the system (in future phases):

### Admin Account
```
Email: admin@smartmaintenance.com
Password: admin123
```

### Technician Accounts
```
Email: john.tech@smartmaintenance.com
Password: tech123

Email: jane.plumber@smartmaintenance.com
Password: tech123

Email: mike.hvac@smartmaintenance.com
Password: tech123
```

### Client Accounts
```
Email: sarah.client@smartmaintenance.com
Password: client123

Email: bob.client@smartmaintenance.com
Password: client123
```

---

## 🔍 Available Endpoints (Phase 1)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/` | API root information |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/stats` | System statistics |

**Note:** Full CRUD API will be available in Phase 4.

---

## 🗄️ Database Information

**Database:** `smart_maintenance`
**Host:** `localhost:5432`
**User:** `postgres`
**Tables:**
- `users` - User accounts with roles
- `assets` - Equipment and facilities
- `maintenance_requests` - Service requests (polymorphic)
- `alembic_version` - Migration tracking

---

## 🧪 Running Tests

To verify everything is working:

```bash
pytest tests/unit/ -v
```

Expected output: **70 passed**

With coverage:
```bash
pytest tests/unit/ --cov=app --cov-report=term-missing
```

Expected coverage: **~76%**

---

## 🛑 Stopping the Server

Press `CTRL+C` in the terminal where the server is running.

To deactivate virtual environment:
```bash
deactivate
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'flask'"

**Solution:** Virtual environment not activated or dependencies not installed.
```bash
source venv/Scripts/activate
pip install -r requirements.txt
```

### Issue: "sqlalchemy.exc.OperationalError: could not translate host name"

**Solution:** Database URL has special characters that need encoding. Check `.env` file has:
```
DATABASE_URL=postgresql://postgres:Y9*jj%250%23r%406655@localhost:5432/smart_maintenance
```

### Issue: "psycopg2.OperationalError: connection to server failed"

**Solution:** PostgreSQL is not running. Start PostgreSQL service:
```bash
# Windows - check if running
pg_isready

# Check PostgreSQL status
services.msc  # Look for "postgresql" service
```

### Issue: "relation 'users' does not exist"

**Solution:** Database migrations not applied.
```bash
flask db upgrade
```

### Issue: Port 5000 already in use

**Solution:** Change port in `run.py` or kill existing process:
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

---

## 📊 Verifying Seeded Data

### Check Users
```bash
python -c "
from app import create_app
from app.repositories import UserRepository
app = create_app('development')
with app.app_context():
    repo = UserRepository()
    users = repo.get_all()
    for user in users:
        print(f'{user.full_name} - {user.email} - {user.role.value}')
"
```

### Check Assets
```bash
python -c "
from app import create_app
from app.repositories import AssetRepository
app = create_app('development')
with app.app_context():
    repo = AssetRepository()
    assets = repo.get_all()
    for asset in assets:
        print(f'{asset.name} - {asset.asset_tag} - {asset.status.value}')
"
```

---

## 🔄 Resetting Database

If you need to start fresh:

```bash
# Drop all tables and recreate
flask db downgrade base
flask db upgrade

# Reseed data
python seed_data.py
```

---

## 📁 Project Structure

```
backend/
├── app/                    # Application code
│   ├── models/            # Domain models (Phase 1 ✅)
│   ├── repositories/      # Data access (Phase 1 ✅)
│   ├── patterns/          # Design patterns (Phase 1 ✅)
│   ├── services/          # Business logic (Phase 2 🔜)
│   ├── controllers/       # API controllers (Phase 4 🔜)
│   └── routes/            # API routes (Basic in Phase 1 ✅)
├── migrations/            # Database migrations
├── tests/                 # Unit and integration tests
├── .env                   # Environment configuration
├── run.py                 # Application entry point
└── seed_data.py           # Sample data generator
```

---

## 🎯 What's Working (Phase 1)

✅ **Models** - User, Asset, MaintenanceRequest (with polymorphic subtypes)
✅ **Repositories** - Full CRUD operations with specialized queries
✅ **Factory Pattern** - Create specialized requests
✅ **Database** - PostgreSQL with migrations
✅ **Tests** - 70 unit tests with 76% coverage
✅ **Basic API** - Health check and stats endpoints

---

## 🚀 Next Steps

**Phase 2** will add:
- Service Layer Pattern
- Strategy Pattern for notifications
- Business logic and validation
- More complex workflows

For now, enjoy exploring the Phase 1 foundation! 🎉

---

## 📞 Need Help?

Check:
1. `CLAUDE.md` - Development guidelines
2. `ROADMAP.md` - Full project plan
3. Test files in `tests/unit/` - Usage examples
4. Model files for validation rules
