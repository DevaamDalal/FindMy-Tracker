@echo off
title Apple FindMy Tracker Dashboard
color 0A

echo ===================================================
echo     APPLE FIND MY TRACKER - STARTUP SCRIPT
echo ===================================================
echo.

echo [1/3] Checking if Docker containers are running...
docker start anisette macless-haystack >nul 2>&1
timeout /t 3 >nul

echo [2/3] Starting Map Dashboard...
cd /d "%~dp0"
start "Map Dashboard Server" cmd /c "python dashboard.py & pause"

echo [3/3] Opening browser...
timeout /t 2 >nul
start http://localhost:6177

echo.
echo Dashboard is running! 
echo If the map says "Error", your Apple session might have expired.
echo In that case, run "docker attach macless-haystack" to log in again.
echo.
pause
