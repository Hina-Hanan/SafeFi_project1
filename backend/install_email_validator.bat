@echo off
echo ============================================
echo Installing Email Validator Package
echo ============================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Installing email-validator...
pip install email-validator

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo ✓ Email validator installed successfully!
    echo ============================================
    echo.
    echo You can now restart the backend server.
) else (
    echo.
    echo ============================================
    echo ✗ Installation failed!
    echo ============================================
)

echo.
pause


