@echo off
REM Smart Maintenance Complete Setup Script
REM Sets up database with sample data and RBAC permissions

echo ========================================
echo Smart Maintenance Management System
echo Complete Setup
echo ========================================
echo.

cd backend

echo [1/3] Seeding sample data (users, assets, requests)...
python seed_data.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to seed sample data
    pause
    exit /b 1
)
echo.

echo [2/3] Seeding RBAC permissions and roles...
echo yes | python seed_rbac.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to seed RBAC data
    pause
    exit /b 1
)
echo.

echo [3/3] Assigning Super Admin role to admin user...
python assign_admin_role.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to assign admin role
    pause
    exit /b 1
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Admin Login Credentials:
echo   Email: admin@smartmaintenance.com
echo   Password: admin123
echo.
echo The admin user now has full RBAC permissions!
echo.
echo To start the application, run: start.bat
echo ========================================
echo.
pause
