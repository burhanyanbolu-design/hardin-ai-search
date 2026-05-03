@echo off
echo ========================================
echo  AI TOOL DATABASE - AUTOMATED SETUP
echo ========================================
echo.
echo This will automatically populate your database
echo with 100+ popular AI tools from GitHub.
echo.
echo No manual work needed!
echo.
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed!
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
pip install -r requirements.txt

echo.
echo [2/3] Creating directories...
if not exist "data\tools" mkdir data\tools
if not exist "data\contributions" mkdir data\contributions
if not exist "data\agents" mkdir data\agents

echo.
echo [3/3] Starting automated population...
echo.
echo ========================================
echo  BOT WILL NOW DISCOVER AND ADD TOOLS
echo ========================================
echo.
echo  This will take about 15-30 minutes
echo  The bot will:
echo  - Search GitHub for AI tools
echo  - Extract information from READMEs
echo  - Create structured profiles
echo  - Save to database
echo.
echo  You can grab a coffee! ☕
echo ========================================
echo.

python auto_populate_database.py

echo.
echo ========================================
echo  DATABASE SETUP COMPLETE!
echo ========================================
echo.
echo Next steps:
echo  1. Run START.bat to start the server
echo  2. Open index.html in your browser
echo  3. Deploy to production!
echo.
pause
