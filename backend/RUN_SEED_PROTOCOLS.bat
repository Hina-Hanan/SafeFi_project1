@echo off
echo ============================================
echo Seeding Real DeFi Protocols
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

echo Seeding protocols...
python scripts\seed_real_protocols.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo ✓ Protocols seeded successfully!
    echo ============================================
    echo.
    echo Next steps:
    echo 1. Run RUN_COLLECT_DATA.bat to get live data
    echo 2. Run RUN_CALCULATE_RISKS.bat to calculate risks
    echo 3. Start backend server
) else (
    echo.
    echo ============================================
    echo ✗ Seeding failed!
    echo ============================================
)

echo.
pause


