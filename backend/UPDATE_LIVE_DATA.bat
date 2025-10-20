@echo off
REM ================================================================
REM Live Data Update Script
REM Updates protocol data to simulate live market changes
REM ================================================================

echo.
echo ===============================================
echo   DeFi Risk Monitor - LIVE DATA UPDATE
echo ===============================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Updating protocol data with live market changes...
python scripts\update_live_data.py

echo.
echo ===============================================
echo   Update Complete!
echo ===============================================
echo.
echo Press any key to close...
pause > nul


