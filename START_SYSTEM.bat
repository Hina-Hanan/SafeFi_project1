@echo off
echo ============================================
echo DeFi Risk Assessment - Quick Start
echo ============================================
echo.

REM Check if .env files exist
echo Checking configuration files...
if not exist "backend\.env" (
    echo ERROR: backend\.env file not found!
    echo.
    echo Please create backend\.env with the following content:
    echo.
    echo DATABASE_URL=postgresql://postgres:postgres@localhost:5432/defi_risk_db
    echo CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
    echo LOG_LEVEL=INFO
    echo MLFLOW_TRACKING_URI=http://localhost:5000
    echo HOST=0.0.0.0
    echo PORT=8000
    echo.
    pause
    exit /b 1
)

if not exist "frontend\.env" (
    echo ERROR: frontend\.env file not found!
    echo.
    echo Please create frontend\.env with the following content:
    echo.
    echo VITE_API_BASE_URL=http://localhost:8000
    echo VITE_ENV=development
    echo.
    pause
    exit /b 1
)

echo ✓ Configuration files found
echo.

echo Starting Backend Server...
start "DeFi Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --host localhost --port 8000"
timeout /t 5 /nobreak >nul

echo.
echo Starting Frontend Server...
start "DeFi Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ============================================
echo System is starting!
echo ============================================
echo.
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:5173
echo API Documentation: http://localhost:8000/docs
echo.
echo Wait a few seconds for services to start, then:
echo 1. Open http://localhost:5173 in your browser
echo 2. Check the protocol heat map displays
echo.
echo To stop the servers, close the terminal windows.
echo ============================================
echo.
pause


