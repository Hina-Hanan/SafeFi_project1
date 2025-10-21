@echo off
echo ============================================
echo Email Subscription Setup - Quick Fix
echo ============================================
echo.

cd /d "%~dp0"

REM Check if .env already exists
if exist ".env" (
    echo .env file already exists!
    echo.
    echo Choose an option:
    echo 1. Add email config to existing .env
    echo 2. Overwrite .env completely
    echo 3. Exit
    echo.
    choice /C 123 /N /M "Choose (1-3): "
    
    if errorlevel 3 goto END
    if errorlevel 2 goto OVERWRITE
    if errorlevel 1 goto APPEND
)

:CREATE
echo Creating new .env file...
echo.

REM Create .env with all necessary configuration
(
echo # Database Configuration
echo DATABASE_URL=postgresql+psycopg2://defi_user:usersafety@localhost:5432/defi_risk_assessment
echo.
echo # MLflow Configuration
echo MLFLOW_TRACKING_URI=http://localhost:5000
echo.
echo # LLM Configuration
echo OLLAMA_BASE_URL=http://localhost:11434
echo OLLAMA_MODEL=tinyllama
echo OLLAMA_TEMPERATURE=0.7
echo OLLAMA_EMBEDDING_MODEL=all-minilm
echo OLLAMA_TIMEOUT=120
echo.
echo # RAG Configuration
echo RAG_CHUNK_SIZE=500
echo RAG_CHUNK_OVERLAP=50
echo RAG_TOP_K=5
echo VECTOR_STORE_PATH=./data/vectorstore
echo.
echo # Email Configuration - DISABLED
echo EMAIL_ALERTS_ENABLED=false
echo SMTP_HOST=smtp.gmail.com
echo SMTP_PORT=587
echo ALERT_SENDER_EMAIL=
echo ALERT_SENDER_PASSWORD=
echo.
echo # Environment
echo ENVIRONMENT=development
) > .env

echo ✓ .env file created successfully!
goto SUCCESS

:OVERWRITE
echo.
echo WARNING: This will delete your existing .env!
choice /C YN /M "Are you sure"
if errorlevel 2 goto END

del .env
goto CREATE

:APPEND
echo.
echo Adding email configuration to existing .env...
echo.

REM Append email config if not already present
findstr /C:"EMAIL_ALERTS_ENABLED" .env >nul
if errorlevel 1 (
    echo. >> .env
    echo # Email Configuration - DISABLED >> .env
    echo EMAIL_ALERTS_ENABLED=false >> .env
    echo SMTP_HOST=smtp.gmail.com >> .env
    echo SMTP_PORT=587 >> .env
    echo ALERT_SENDER_EMAIL= >> .env
    echo ALERT_SENDER_PASSWORD= >> .env
    echo ✓ Email config added!
) else (
    echo Email configuration already exists in .env
    echo You may need to edit it manually.
)
goto SUCCESS

:SUCCESS
echo.
echo ============================================
echo ✓ Configuration Complete!
echo ============================================
echo.
echo Email alerts are currently DISABLED
echo This removes the warning on the frontend.
echo.
echo To ENABLE email alerts later:
echo 1. Edit backend\.env
echo 2. Change: EMAIL_ALERTS_ENABLED=false to true
echo 3. Add your Gmail email and app password
echo 4. Restart backend
echo.
echo ============================================
echo Next Steps:
echo ============================================
echo.
echo 1. Restart your backend server
echo    - Press Ctrl+C in backend terminal
echo    - Run: uvicorn app.main:app --reload
echo.
echo 2. Refresh your frontend
echo    - The error should be GONE!
echo.
echo 3. Users can now subscribe (data saved)
echo    - Email sending will work when you enable it
echo.

:END
pause

