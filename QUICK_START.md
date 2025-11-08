# 🚀 Quick Start Guide - Smart Maintenance System

## Port Configuration

**Backend (Flask):** http://localhost:5001
**Frontend (Blazor):** https://localhost:5222 (or auto-assigned port)

**Changed from port 5000 to 5001 to avoid conflicts with other projects!**

---

## 🏃 Running the Application

### Step 1: Start the Backend (Terminal 1)

```bash
# Navigate to backend folder
cd "C:\Users\sifisos\Smart Projects\smart_maintenance\backend"

# Run the Flask app
python run.py
```

**Expected Output:**
```
 * Running on http://0.0.0.0:5001
 * Running on http://127.0.0.1:5001
```

✅ Backend is running on **port 5001**

---

### Step 2: Start the Frontend (Terminal 2)

```bash
# Navigate to frontend folder
cd "C:\Users\sifisos\Smart Projects\smart_maintenance\frontend"

# Run the Blazor app with hot reload
dotnet watch run
```

**Expected Output:**
```
info: Microsoft.Hosting.Lifetime[14]
      Now listening on: https://localhost:5222
      Now listening on: http://localhost:5001
```

✅ Frontend is running (note the HTTPS port - usually 5222 or 7001)

---

### Step 3: Open in Browser

Open your browser to: **https://localhost:5222** (or the HTTPS port shown)

Navigate to: **/login**

---

## 🔍 Troubleshooting

### Problem: "Port 5001 is already in use"

**Solution:**
```bash
# Find what's using port 5001
netstat -ano | findstr :5001

# Kill the process (replace PID with the number from above)
taskkill /PID <PID> /F
```

---

### Problem: "CORS error" or "Failed to fetch"

**Solution:**
- Make sure Flask backend is running on **port 5001**
- Check that CORS is configured in `backend/app/config.py`
- Verify the frontend `Program.cs` points to `http://localhost:5001`

**Current CORS Configuration:**
- http://localhost:5222 ✅
- https://localhost:5001 ✅
- http://localhost:5000 ✅
- https://localhost:7001 ✅

---

### Problem: "Cannot connect to backend"

**Checklist:**
1. ✅ Backend is running? Check Terminal 1
2. ✅ Backend shows "Running on http://127.0.0.1:5001"?
3. ✅ Frontend `Program.cs` uses `http://localhost:5001`?
4. ✅ Try in browser: http://localhost:5001/api/v1/health (if you add health endpoint)

---

## 📝 Create Test Users

Before you can login, you need to create test users. Run in Terminal 1 (while in backend folder):

```bash
# Option 1: Use Python shell
python

>>> from app import create_app
>>> from app.database import db
>>> from app.models import User, UserRole
>>> from werkzeug.security import generate_password_hash
>>>
>>> app = create_app('development')
>>> with app.app_context():
...     # Create admin user
...     admin = User(
...         email='admin@test.com',
...         password_hash=generate_password_hash('password123'),
...         full_name='Admin User',
...         role=UserRole.ADMIN,
...         is_active=True
...     )
...     db.session.add(admin)
...
...     # Create technician
...     tech = User(
...         email='tech@test.com',
...         password_hash=generate_password_hash('password123'),
...         full_name='Tech User',
...         role=UserRole.TECHNICIAN,
...         is_active=True
...     )
...     db.session.add(tech)
...
...     # Create client
...     client = User(
...         email='client@test.com',
...         password_hash=generate_password_hash('password123'),
...         full_name='Client User',
...         role=UserRole.CLIENT,
...         is_active=True
...     )
...     db.session.add(client)
...
...     db.session.commit()
...     print("Users created!")
>>> exit()
```

**Test Credentials:**
- Admin: `admin@test.com` / `password123`
- Technician: `tech@test.com` / `password123`
- Client: `client@test.com` / `password123`

---

## 🎯 Testing the Login Page

1. ✅ Start backend (port 5001)
2. ✅ Start frontend (auto-assigned port)
3. ✅ Open browser to frontend URL
4. ✅ Navigate to `/login`
5. ✅ Try logging in with test credentials
6. ✅ Should see success toast and redirect!

---

## 🛑 Stopping the Application

**Stop Backend (Terminal 1):**
```
Ctrl + C
```

**Stop Frontend (Terminal 2):**
```
Ctrl + C
```

---

## 📊 Current Status

### ✅ Completed
- Backend running on port 5001
- Frontend configured for port 5001
- CORS configured for Blazor ports
- Login page created and styled
- Services implemented (Auth, API)
- Models created
- Dependency injection configured

### ⏳ Next Steps
- Test login with real backend
- Create Register page
- Create Dashboard
- Create Request management pages

---

## 🎨 Project URLs

| Component | URL | Status |
|-----------|-----|--------|
| Flask Backend | http://localhost:5001 | ✅ Ready |
| Blazor Frontend | https://localhost:5222 | ✅ Ready |
| Login Page | https://localhost:5222/login | ✅ Created |
| Dashboard | https://localhost:5222/ | ⏳ Coming soon |

---

**Happy Coding! 🚀**
