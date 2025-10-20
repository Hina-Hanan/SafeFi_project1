@echo off
echo ========================================
echo Starting DeFi Risk Assessment Backend
echo ========================================
echo.

cd backend

echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [2/3] Checking Python and dependencies...
python --version
echo.

echo [3/3] Starting backend server...
echo Server will run at: http://localhost:8000
echo API Docs will be at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app.main:app --reload --host localhost --port 8000

pause

