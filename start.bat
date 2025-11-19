@echo off
REM Smart Maintenance Application Startup Script
REM Starts both backend (Flask) and frontend (Blazor) servers

echo ========================================
echo Smart Maintenance Management System
echo Starting Application...
echo ========================================
echo.

REM Start backend in a new window
echo [1/2] Starting Flask Backend Server...
start "Flask Backend - http://127.0.0.1:5001" cmd /k "cd backend && python run.py"
timeout /t 3 /nobreak > nul

REM Start frontend in a new window
echo [2/2] Starting Blazor Frontend Server...
start "Blazor Frontend - http://localhost:5112" cmd /k "cd frontend && dotnet watch run --launch-profile http"

echo.
echo ========================================
echo Application Started Successfully!
echo ========================================
echo.
echo Backend:  http://127.0.0.1:5001
echo Frontend: http://localhost:5112
echo.
echo Press Ctrl+C in each terminal to stop
echo ========================================
