@echo off
echo ========================================
echo   HARDIN - Opening Search Interface
echo ========================================
echo.

cd /d "%~dp0"

echo Opening index.html in your default browser...
echo.
echo IMPORTANT: Make sure the API server is running!
echo If not, run START-API-SERVER.bat first
echo.

start index.html

echo.
echo Browser opened!
echo You can now search for AI tools.
echo.
echo Try searching for:
echo   - chatbot
echo   - langchain
echo   - agent
echo   - rag
echo.
pause
