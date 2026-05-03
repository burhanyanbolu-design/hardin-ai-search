@echo off
title HARDIN - AI Tool Search Engine Demo
color 0A

echo.
echo ========================================
echo    HARDIN - AI TOOL SEARCH ENGINE
echo    Demo Launcher for YC Application
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo [2/4] Installing dependencies...
pip install Flask Flask-CORS requests schedule --quiet

echo.
echo [3/4] Verifying database...
set /a count=0
for %%f in (data\tools\*.json) do set /a count+=1
echo Found %count% AI tools in database

echo.
echo [4/4] Starting API server...
echo.
echo ========================================
echo   SERVER STARTING
echo ========================================
echo.
echo API Server: http://localhost:5000
echo.
echo The browser will open automatically in 5 seconds...
echo.
echo DEMO SEARCH TERMS:
echo   - chatbot
echo   - langchain  (135k stars!)
echo   - agent
echo   - rag
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start browser after 5 seconds
start /B cmd /c "timeout /t 5 /nobreak >nul && start index.html"

REM Start API server
python api_contribution.py

pause
