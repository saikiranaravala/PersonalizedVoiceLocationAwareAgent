@echo off
REM Start the FastAPI backend server

echo ========================================
echo Starting Agentic Assistant Backend
echo ========================================
echo.

REM Check if config/.env exists
if not exist "config\.env" (
    echo ERROR: config\.env not found!
    echo.
    echo Please run setup.bat first or create config\.env manually
    echo Copy from: config\.env.example
    echo.
    pause
    exit /b 1
)

REM Check if FastAPI is installed
python -c "from fastapi import FastAPI" >nul 2>&1
if errorlevel 1 (
    echo ERROR: FastAPI not installed!
    echo.
    echo Please run: pip install fastapi uvicorn --break-system-packages
    echo Or run: setup.bat
    echo.
    pause
    exit /b 1
)

echo Starting server on http://localhost:8000
echo.
echo API Endpoints:
echo   Health Check: http://localhost:8000/health
echo   Chat API:     http://localhost:8000/chat
echo   WebSocket:    ws://localhost:8000/ws/{session_id}
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

REM Start the server
python api_server.py

pause
