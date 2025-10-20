@echo off
echo ============================================
echo Initializing Database
echo ============================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please ensure venv exists in backend directory.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Running database initialization...
python scripts\init_db.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo ✓ Database initialized successfully!
    echo ============================================
    echo.
    echo Next step: Run RUN_SEED_PROTOCOLS.bat
) else (
    echo.
    echo ============================================
    echo ✗ Database initialization failed!
    echo ============================================
    echo.
    echo Please check:
    echo 1. PostgreSQL is running
    echo 2. .env file exists with correct DATABASE_URL
    echo 3. Database 'defi_risk_db' exists
)

echo.
pause


