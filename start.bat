@echo off
REM Personalized Agentic Assistant Launcher for Windows

echo ========================================
echo Personalized Agentic Assistant
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import langchain" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Check for .env file
if not exist "config\.env" (
    echo WARNING: config\.env file not found!
    echo Please create it from config\.env.example and add your API keys.
    echo.
    pause
    exit /b 1
)

REM Launch the application
echo Starting Personalized Agentic Assistant...
echo.
python src\main.py %*

REM Deactivate virtual environment
deactivate
pause
