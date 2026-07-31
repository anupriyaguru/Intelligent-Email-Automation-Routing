@echo off
REM Stop all agents and dashboard

echo Stopping Email Orchestration Multi-Agent System
echo ================================================
echo.

echo Killing processes on ports...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000') do (
    echo Stopping Orchestrator Agent (port 5000^)...
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5001') do (
    echo Stopping AR Agent (port 5001^)...
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5002') do (
    echo Stopping AP Agent (port 5002^)...
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5003') do (
    echo Stopping Treasury Agent (port 5003^)...
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5004') do (
    echo Stopping Collections Agent (port 5004^)...
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5005') do (
    echo Stopping CS Agent (port 5005^)...
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :4004') do (
    echo Stopping Review Dashboard (port 4004^)...
    taskkill /F /PID %%a 2>nul
)

echo.
echo All services stopped.
echo.

pause
