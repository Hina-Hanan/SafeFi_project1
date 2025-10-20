@echo off
REM ===================================================================
REM ML Model Training Job - Automated Execution
REM ===================================================================
REM 
REM This script trains ML risk scoring and anomaly detection models.
REM Schedule this to run weekly using Windows Task Scheduler.
REM 
REM Usage:
REM   train_models_job.bat
REM 
REM ===================================================================

echo ========================================
echo ML Model Training Job
echo Time: %date% %time%
echo ========================================

REM Change to backend directory
cd /d "%~dp0"

REM Set PYTHONPATH
set PYTHONPATH=%CD%

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Train models
echo.
echo [1/1] Training ML models...
python scripts\train_ml_models.py

if %errorlevel% neq 0 (
    echo ERROR: Model training failed with code %errorlevel%
    exit /b %errorlevel%
)

echo.
echo ========================================
echo Training completed successfully!
echo ========================================







