@echo off
echo ============================================
echo Email Alerts Configuration Setup
echo ============================================
echo.

cd /d "%~dp0"

if exist ".env" (
    echo .env file already exists!
    echo.
    choice /C YN /M "Do you want to update it"
    if errorlevel 2 goto END
    echo.
) else (
    echo Creating .env file from template...
    copy env.example .env
    echo.
)

echo ============================================
echo Configuration Options:
echo ============================================
echo.
echo 1. Disable email alerts (recommended for testing)
echo 2. Enable with Gmail
echo 3. Enable with custom SMTP
echo 4. Exit without changes
echo.

choice /C 1234 /N /M "Choose option (1-4): "

if errorlevel 4 goto END
if errorlevel 3 goto CUSTOM
if errorlevel 2 goto GMAIL
if errorlevel 1 goto DISABLE

:DISABLE
echo.
echo Setting EMAIL_ALERTS_ENABLED=false...
echo EMAIL_ALERTS_ENABLED=false >> .env
echo.
echo ✓ Email alerts disabled
echo ✓ Warning will be removed after backend restart
goto SUCCESS

:GMAIL
echo.
echo ============================================
echo Gmail App Password Setup
echo ============================================
echo.
echo 1. Go to: https://myaccount.google.com/security
echo 2. Enable 2-Step Verification
echo 3. Create App Password for Mail
echo 4. Copy the 16-character password
echo.
pause
echo.

set /p EMAIL="Enter your Gmail address: "
set /p PASSWORD="Enter your App Password (16 chars, no spaces): "

echo.
echo Adding to .env...
echo EMAIL_ALERTS_ENABLED=true >> .env
echo SMTP_HOST=smtp.gmail.com >> .env
echo SMTP_PORT=587 >> .env
echo ALERT_SENDER_EMAIL=%EMAIL% >> .env
echo ALERT_SENDER_PASSWORD=%PASSWORD% >> .env
echo.
echo ✓ Gmail configuration added
goto SUCCESS

:CUSTOM
echo.
set /p SMTP_HOST="SMTP Host (e.g., smtp.example.com): "
set /p SMTP_PORT="SMTP Port (usually 587 or 465): "
set /p EMAIL="Sender Email: "
set /p PASSWORD="Email Password: "

echo.
echo Adding to .env...
echo EMAIL_ALERTS_ENABLED=true >> .env
echo SMTP_HOST=%SMTP_HOST% >> .env
echo SMTP_PORT=%SMTP_PORT% >> .env
echo ALERT_SENDER_EMAIL=%EMAIL% >> .env
echo ALERT_SENDER_PASSWORD=%PASSWORD% >> .env
echo.
echo ✓ Custom SMTP configuration added
goto SUCCESS

:SUCCESS
echo.
echo ============================================
echo ✓ Configuration Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Restart your backend server
echo 2. The email alert warning should disappear
echo 3. Users can now subscribe to alerts
echo.
echo To restart backend:
echo   - Press Ctrl+C in backend terminal
echo   - Run START_BACKEND.bat again
echo.
goto END

:END
echo.
pause

