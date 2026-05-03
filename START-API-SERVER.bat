@echo off
echo ========================================
echo STARTING HARDIN API SERVER
echo ========================================
echo.
echo Server will start on: http://localhost:5000
echo.
echo Once server is running:
echo 1. Open index.html in your browser
echo 2. Search will work automatically
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

cd /d "%~dp0"
python api_contribution.py

pause
