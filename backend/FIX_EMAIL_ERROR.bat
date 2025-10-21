@echo off
REM ============================================
REM Quick Fix for Email Subscription Error
REM ============================================

cd /d "%~dp0"

echo.
echo Fixing email subscription error...
echo.

REM Create .env if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    copy env.example .env >nul 2>&1
    if errorlevel 1 (
        echo Manual creation...
        type nul > .env
    )
)

REM Check if email config exists
findstr /C:"EMAIL_ALERTS_ENABLED" .env >nul 2>&1
if errorlevel 1 (
    echo Adding email configuration...
    echo. >> .env
    echo EMAIL_ALERTS_ENABLED=false >> .env
    echo SMTP_HOST=smtp.gmail.com >> .env
    echo SMTP_PORT=587 >> .env
    echo ALERT_SENDER_EMAIL= >> .env
    echo ALERT_SENDER_PASSWORD= >> .env
)

REM Also ensure database URL exists
findstr /C:"DATABASE_URL" .env >nul 2>&1
if errorlevel 1 (
    echo Adding database configuration...
    echo DATABASE_URL=postgresql+psycopg2://defi_user:usersafety@localhost:5432/defi_risk_assessment >> .env
)

echo.
echo ============================================
echo ✓ Fixed!
echo ============================================
echo.
echo Email alerts are now configured (disabled mode)
echo The error message will disappear after backend restart.
echo.
echo To restart backend:
echo   1. Stop current backend (Ctrl+C)
echo   2. Run: uvicorn app.main:app --reload
echo.
echo ✓ Email subscription will work (saves data)
echo ✓ No actual emails sent (EMAIL_ALERTS_ENABLED=false)
echo ✓ Can enable real emails later by editing .env
echo.
pause

