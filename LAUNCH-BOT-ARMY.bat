@echo off
echo ========================================
echo  BOT ARMY LAUNCHER
echo ========================================
echo.
echo Choose your mission:
echo.
echo 1. Quick Mission (One-time population)
echo 2. News Agent Network (24/7 monitoring)
echo 3. Both (Population + Monitoring)
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" goto quick
if "%choice%"=="2" goto news
if "%choice%"=="3" goto both
goto end

:quick
echo.
echo ========================================
echo  LAUNCHING QUICK MISSION
echo ========================================
echo.
echo This will:
echo  - Create bot army (10 bots)
echo  - Scout for AI tools
echo  - Extract knowledge
echo  - Validate quality
echo  - Save to database
echo.
echo Time: ~5-10 minutes
echo.
pause
python bot_army.py
goto end

:news
echo.
echo ========================================
echo  LAUNCHING NEWS AGENT NETWORK
echo ========================================
echo.
echo This will:
echo  - Deploy 8 news agents
echo  - Monitor GitHub 24/7
echo  - Auto-process new tools
echo  - Update database continuously
echo.
echo This runs forever until you stop it!
echo.
pause
python bot_news_agent.py
goto end

:both
echo.
echo ========================================
echo  LAUNCHING FULL SYSTEM
echo ========================================
echo.
echo Phase 1: Quick population
python bot_army.py
echo.
echo Phase 2: Starting 24/7 monitoring
python bot_news_agent.py
goto end

:end
echo.
echo ========================================
echo  MISSION COMPLETE
echo ========================================
pause
