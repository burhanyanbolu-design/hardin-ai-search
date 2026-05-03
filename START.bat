@echo off
echo ========================================
echo  AI TOOL SEARCH ENGINE - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install -r requirements.txt

echo.
echo [2/4] Creating data directories...
if not exist "data\tools" mkdir data\tools
if not exist "data\contributions" mkdir data\contributions
if not exist "data\agents" mkdir data\agents

echo.
echo [3/4] Starting API server...
echo.
echo ========================================
echo  Server starting on http://localhost:5000
echo ========================================
echo.
echo  API Endpoints:
echo  - POST /api/contribute/discover
echo  - POST /api/contribute/update
echo  - POST /api/contribute/experience
echo  - GET  /api/search
echo  - GET  /api/tools/{tool_name}
echo  - GET  /api/stats
echo.
echo  Web Interface:
echo  - Open index.html in your browser
echo  - Or visit http://localhost:5000
echo.
echo  Press Ctrl+C to stop the server
echo ========================================
echo.

python api_contribution.py

pause
