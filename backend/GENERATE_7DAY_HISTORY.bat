@echo off
REM ================================================================
REM Generate 7-Day Historical Data
REM Creates historical risk trends for 7-Day Analysis chart
REM ================================================================

echo.
echo ===============================================
echo   Generate 7-Day Historical Risk Data
echo ===============================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Generating 7 days of historical data (28 points per protocol)...
python scripts\generate_7day_history.py

echo.
echo ===============================================
echo   7-Day History Generation Complete!
echo ===============================================
echo.
echo Refresh your 7-Day Analysis tab to see the trends!
echo.
pause


