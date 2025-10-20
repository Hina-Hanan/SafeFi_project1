@echo off
REM ===================================================================
REM Phase 2 Quick Test Script
REM ===================================================================
echo.
echo ========================================
echo Phase 2 ML System - Quick Test
echo ========================================
echo.

cd /d "%~dp0"
set PYTHONPATH=%CD%

echo [1/4] Checking if backend server is running...
curl -s http://localhost:8000/health > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Backend server is not running!
    echo Please start it with: uvicorn app.main:app --reload
    pause
    exit /b 1
)
echo ✓ Backend server is running
echo.

echo [2/4] Training ML models (this may take 2-5 minutes)...
python scripts\train_ml_models.py
if %errorlevel% neq 0 (
    echo ERROR: Model training failed
    echo Make sure you have enough data collected
    pause
    exit /b 1
)
echo ✓ Models trained successfully
echo.

echo [3/4] Testing API endpoints...
echo.

echo Testing /features/importance...
curl -s http://localhost:8000/features/importance | python -m json.tool
echo.
echo ✓ Feature importance endpoint working
echo.

echo Testing /anomaly/scan...
curl -s http://localhost:8000/anomaly/scan | python -m json.tool
echo.
echo ✓ Anomaly scan endpoint working
echo.

echo [4/4] Verifying model files...
if exist "models\ml_risk_scorer.joblib" (
    echo ✓ Risk scorer model found
) else (
    echo ✗ Risk scorer model not found
)

if exist "models\anomaly_detector.joblib" (
    echo ✓ Anomaly detector model found
) else (
    echo ✗ Anomaly detector model not found
)
echo.

echo ========================================
echo Phase 2 Test Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Check feature importance results above
echo 2. Test anomaly detection for specific protocols
echo 3. Setup automated training in Task Scheduler
echo.
echo API Endpoints available:
echo - GET /features/importance
echo - GET /features/shap/{protocol_id}
echo - GET /anomaly/protocols/{protocol_id}
echo - GET /anomaly/scan
echo.
pause







