@echo off
REM Setup script for Personalized Agentic Assistant
REM Installs all dependencies and starts the server

echo ========================================
echo Personalized Agentic Assistant Setup
echo ========================================
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11.9 from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Installing Python dependencies...
echo.
pip install -r requirements.txt --break-system-packages

if errorlevel 1 (
    echo.
    echo WARNING: Some packages failed to install
    echo Trying alternative installation method...
    pip install fastapi uvicorn websockets python-multipart --break-system-packages
)

echo.
echo [2/4] Checking configuration...
if not exist "config\.env" (
    echo WARNING: config\.env not found
    echo Copying from template...
    copy config\.env.example config\.env
    echo.
    echo IMPORTANT: Edit config\.env and add your API keys!
    echo Press any key to open the file in notepad...
    pause >nul
    notepad config\.env
)

echo.
echo [3/4] Testing API server...
python -c "from fastapi import FastAPI; print('FastAPI installed successfully')" >nul 2>&1
if errorlevel 1 (
    echo ERROR: FastAPI not installed correctly
    echo Please run: pip install fastapi uvicorn --break-system-packages
    pause
    exit /b 1
)

echo.
echo [4/4] Setup complete!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo.
echo 1. Make sure config\.env has your OPENAI_API_KEY or OPENROUTER_API_KEY
echo 2. Start the backend: python api_server.py
echo 3. In another terminal, start the UI:
echo    cd ui
echo    npm install
echo    npm run dev
echo.
echo ========================================
echo.
pause
