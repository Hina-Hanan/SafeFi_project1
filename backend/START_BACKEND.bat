@echo off
echo ============================================
echo Starting Backend Server
echo ============================================
echo.

cd /d "%~dp0"

if not exist ".env" (
    echo ERROR: .env file not found!
    echo.
    echo Please run CREATE_ENV_FILES.bat first
    echo Or manually create backend\.env file
    pause
    exit /b 1
)

if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo.
echo Starting FastAPI server...
echo Backend will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

REM Use localhost instead of 0.0.0.0 for Windows compatibility
uvicorn app.main:app --reload --host localhost --port 8000


