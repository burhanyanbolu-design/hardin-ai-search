@echo off
title Hardin - Deploy to GitHub
color 0A

cls
echo.
echo ========================================
echo   HARDIN - DEPLOY TO GITHUB
echo ========================================
echo.
echo This will:
echo   1. Initialize Git repository
echo   2. Add all files
echo   3. Create initial commit
echo   4. Prepare for GitHub push
echo.
echo ========================================
echo.
pause

cd /d "%~dp0"

echo.
echo [1/5] Initializing Git repository...
git init

echo.
echo [2/5] Adding files...
git add .

echo.
echo [3/5] Creating commit...
git commit -m "Initial commit - Hardin AI Search Engine with 84 tools"

echo.
echo [4/5] Setting main branch...
git branch -M main

echo.
echo ========================================
echo   NEXT STEPS:
echo ========================================
echo.
echo 1. Create GitHub repository:
echo    - Go to: https://github.com/new
echo    - Name: hardin-ai-search
echo    - Make it PUBLIC
echo    - Don't initialize with README
echo    - Click "Create repository"
echo.
echo 2. Copy your repository URL
echo    Example: https://github.com/YOUR_USERNAME/hardin-ai-search.git
echo.
echo 3. Run these commands:
echo    git remote add origin YOUR_REPO_URL
echo    git push -u origin main
echo.
echo 4. Deploy to Vercel:
echo    - Go to: https://vercel.com
echo    - Sign in with GitHub
echo    - Import your repository
echo    - Click Deploy!
echo.
echo ========================================
echo.
pause
