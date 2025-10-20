@echo off
REM Automated Risk Calculation Script for DeFi Risk Assessment
REM This script calculates risk scores based on collected metrics

cd /d "C:\Users\hinah\main-project\backend"

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set Python path
set PYTHONPATH=C:\Users\hinah\main-project\backend

REM Run risk calculation
echo [%date% %time%] Starting risk calculation...
python scripts\calculate_risks.py

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo [%date% %time%] Risk calculation completed successfully
) else (
    echo [%date% %time%] Risk calculation failed with error code %ERRORLEVEL%
)

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat








