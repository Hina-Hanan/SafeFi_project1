@echo off
REM Automated Data Collection Script for DeFi Risk Assessment
REM This script collects live data from DeFi APIs and stores in database

cd /d "C:\Users\hinah\main-project\backend"

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set Python path
set PYTHONPATH=C:\Users\hinah\main-project\backend

REM Run data collection
echo [%date% %time%] Starting data collection...
python scripts\collect_live_data.py

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo [%date% %time%] Data collection completed successfully
) else (
    echo [%date% %time%] Data collection failed with error code %ERRORLEVEL%
)

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat








