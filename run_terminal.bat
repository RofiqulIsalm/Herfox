@echo off
title The Life - Forex Confluence Terminal
color 0b

echo =====================================================================
echo           THE LIFE - INSTITUTIONAL CONFLUENCE TERMINAL
echo =====================================================================
echo Starting Local Quantitative Trading Engine...

:: 1. Terminate any previous zombie python processes on port 8000
echo Ensuring clean port 8000 environment...
taskkill /f /im python.exe >nul 2>&1
timeout /t 1 /nobreak >nul

:: 2. Activate Python Virtual Environment
call .\.venv\Scripts\activate.bat

:: 3. Launch FastAPI Server in Background
echo Launching FastAPI Server and Real-Time WebSocket Engine on port 8000...
start "The Life Backend Server" /b .\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000

:: 4. Wait for Backend initialization
timeout /t 3 /nobreak >nul

:: 5. Launch Desktop Terminal Window in Native App Mode via Microsoft Edge WebView
echo Launching Institutional Terminal Window...
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app=http://localhost:8000 --window-size=1600,950
) else if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files\Microsoft\Edge\Application\msedge.exe" --app=http://localhost:8000 --window-size=1600,950
) else (
    start http://localhost:8000
)

echo.
echo Terminal Running! Press any key or close this window to stop the server.
echo =====================================================================
pause
taskkill /f /im python.exe >nul 2>&1

