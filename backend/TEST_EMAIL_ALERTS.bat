@echo off
echo ========================================
echo Email Alerts Configuration Test
echo ========================================
echo.

echo [1/3] Checking .env configuration...
findstr /C:"EMAIL_ALERTS_ENABLED" .env
findstr /C:"SMTP_HOST" .env
findstr /C:"SMTP_PORT" .env
findstr /C:"ALERT_SENDER_EMAIL" .env
echo.

echo [2/3] Testing database table...
python -c "from app.database.connection import SessionLocal; from sqlalchemy import text; db = SessionLocal(); result = db.execute(text('SELECT count(*) FROM email_subscribers')); print('✅ email_subscribers table exists! Row count:', result.scalar()); db.close()" 2>nul

if errorlevel 1 (
    echo ❌ email_subscribers table NOT found!
    echo Run this command to create it:
    echo python -c "from app.database.connection import ENGINE; from sqlalchemy import text; conn = ENGINE.connect().execution_options(isolation_level='AUTOCOMMIT'); conn.execute(text('''CREATE TABLE IF NOT EXISTS email_subscribers (id VARCHAR(36) PRIMARY KEY, email VARCHAR(255) UNIQUE NOT NULL, is_active BOOLEAN DEFAULT TRUE, is_verified BOOLEAN DEFAULT FALSE, high_risk_threshold FLOAT DEFAULT 70.0, medium_risk_threshold FLOAT DEFAULT 40.0, notify_on_high BOOLEAN DEFAULT TRUE, notify_on_medium BOOLEAN DEFAULT TRUE, verification_token VARCHAR(100), unsubscribe_token VARCHAR(100), last_alert_sent TIMESTAMP WITH TIME ZONE, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)''')); print('Table created'); conn.close()"
)
echo.

echo [3/3] Testing email alerts API endpoint...
echo Make sure backend is running on http://localhost:8000
echo.
curl -s http://localhost:8000/email-alerts/status 2>nul

if errorlevel 1 (
    echo.
    echo ❌ Backend is not running!
    echo Please start it with: python -m uvicorn app.main:app --reload
) else (
    echo.
    echo.
    echo ========================================
    echo Next Steps:
    echo ========================================
    echo 1. Make sure EMAIL_ALERTS_ENABLED=true in .env
    echo 2. RESTART the backend server to pick up .env changes
    echo 3. Test email subscription in the frontend
    echo ========================================
)

echo.
pause

