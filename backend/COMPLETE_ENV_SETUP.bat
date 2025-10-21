@echo off
REM ============================================
REM Complete Environment Setup
REM Creates .env with all necessary settings
REM ============================================

echo.
echo ============================================
echo Complete Environment Setup
echo ============================================
echo.

cd /d "%~dp0"

if exist ".env" (
    echo WARNING: .env file already exists!
    echo.
    choice /C YN /M "Do you want to overwrite it"
    if errorlevel 2 (
        echo.
        echo Cancelled. Your existing .env is unchanged.
        goto END
    )
    del .env
)

echo Creating .env file with complete configuration...
echo.

REM Write complete .env file
(
echo # ============================================================================
echo # DeFi Risk Assessment - Environment Configuration
echo # ============================================================================
echo.
echo # Database Configuration
echo DATABASE_URL=postgresql+psycopg2://defi_user:usersafety@localhost:5432/defi_risk_assessment
echo.
echo # MLflow Configuration
echo MLFLOW_TRACKING_URI=http://localhost:5000
echo.
echo # LLM Configuration ^(Ollama^)
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
echo # Email Alert Configuration
echo # Set EMAIL_ALERTS_ENABLED=true to enable email notifications
echo # For Gmail: Get App Password from https://myaccount.google.com/apppasswords
echo EMAIL_ALERTS_ENABLED=false
echo SMTP_HOST=smtp.gmail.com
echo SMTP_PORT=587
echo ALERT_SENDER_EMAIL=
echo ALERT_SENDER_PASSWORD=
echo.
echo # Environment
echo ENVIRONMENT=development
) > .env

echo.
echo ✓ .env file created successfully!
echo.
echo ============================================
echo Configuration Summary:
echo ============================================
echo.
echo ✓ Database: PostgreSQL (localhost:5432)
echo ✓ MLflow: http://localhost:5000
echo ✓ LLM: Ollama with TinyLlama
echo ✓ Email Alerts: DISABLED (no error messages)
echo.
echo ============================================
echo Next Steps:
echo ============================================
echo.
echo 1. Start PostgreSQL if not running
echo.
echo 2. Start Backend:
echo    cd backend
echo    venv\Scripts\activate
echo    uvicorn app.main:app --reload
echo.
echo 3. Start Frontend (in new terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 4. Access Dashboard:
echo    http://localhost:5173
echo.
echo ✓ Email subscription will work (saves data)
echo ✓ No error messages will appear
echo.
echo To enable real email alerts:
echo    - Edit backend\.env
echo    - Set EMAIL_ALERTS_ENABLED=true
echo    - Add Gmail email and app password
echo    - Restart backend
echo.

:END
pause

