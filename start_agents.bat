@echo off
REM Start all agents for end-to-end testing
REM This script starts all 6 agents and the review dashboard in separate background processes

echo Starting Email Orchestration Multi-Agent System
echo ================================================
echo.

REM Kill any existing processes on these ports
echo Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5001') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5002') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5003') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5004') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5005') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :4004') do taskkill /F /PID %%a 2>nul

REM Create logs directory
if not exist logs mkdir logs

REM Export environment for testing
set IBD_TESTING=1

echo Starting agents...
echo.

REM Start Orchestrator Agent
echo 1. Starting Orchestrator Agent on port 5000...
cd assets\email-orchestrator-agent
start /B python app\main.py --port 5000 > ..\..\logs\orchestrator.log 2>&1
cd ..\..
timeout /t 2 /nobreak >nul

REM Start AR Sub-Agent
echo 2. Starting AR Sub-Agent on port 5001...
cd assets\email-ar-agent
start /B python app\main.py --port 5001 > ..\..\logs\ar-agent.log 2>&1
cd ..\..
timeout /t 1 /nobreak >nul

REM Start AP Sub-Agent
echo 3. Starting AP Sub-Agent on port 5002...
cd assets\email-ap-agent
start /B python app\main.py --port 5002 > ..\..\logs\ap-agent.log 2>&1
cd ..\..
timeout /t 1 /nobreak >nul

REM Start Treasury Sub-Agent
echo 4. Starting Treasury Sub-Agent on port 5003...
cd assets\email-treasury-agent
start /B python app\main.py --port 5003 > ..\..\logs\treasury-agent.log 2>&1
cd ..\..
timeout /t 1 /nobreak >nul

REM Start Collections Sub-Agent
echo 5. Starting Collections Sub-Agent on port 5004...
cd assets\email-collections-agent
start /B python app\main.py --port 5004 > ..\..\logs\collections-agent.log 2>&1
cd ..\..
timeout /t 1 /nobreak >nul

REM Start CS Sub-Agent
echo 6. Starting CS Sub-Agent on port 5005...
cd assets\email-cs-agent
start /B python app\main.py --port 5005 > ..\..\logs\cs-agent.log 2>&1
cd ..\..
timeout /t 1 /nobreak >nul

REM Start Review Dashboard
echo 7. Starting Review Dashboard on port 4004...
cd assets\email-review-dashboard-cap
call npm install --silent
start /B cmd /c "cds watch > ..\..\logs\dashboard.log 2>&1"
cd ..\..

echo.
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

echo.
echo ================================================
echo Service Status
echo ================================================

REM Check each service using curl (if available) or PowerShell
echo Checking services...
curl -s http://localhost:5000/.well-known/agent.json >nul 2>&1 && echo [32m✓[0m Orchestrator Agent (5000): UP || echo [31m✗[0m Orchestrator Agent (5000): DOWN
curl -s http://localhost:5001/.well-known/agent.json >nul 2>&1 && echo [32m✓[0m AR Agent (5001): UP || echo [31m✗[0m AR Agent (5001): DOWN
curl -s http://localhost:5002/.well-known/agent.json >nul 2>&1 && echo [32m✓[0m AP Agent (5002): UP || echo [31m✗[0m AP Agent (5002): DOWN
curl -s http://localhost:5003/.well-known/agent.json >nul 2>&1 && echo [32m✓[0m Treasury Agent (5003): UP || echo [31m✗[0m Treasury Agent (5003): DOWN
curl -s http://localhost:5004/.well-known/agent.json >nul 2>&1 && echo [32m✓[0m Collections Agent (5004): UP || echo [31m✗[0m Collections Agent (5004): DOWN
curl -s http://localhost:5005/.well-known/agent.json >nul 2>&1 && echo [32m✓[0m CS Agent (5005): UP || echo [31m✗[0m CS Agent (5005): DOWN
curl -s http://localhost:4004/odata/v4/review/ReviewCases >nul 2>&1 && echo [32m✓[0m Review Dashboard (4004): UP || echo [31m✗[0m Review Dashboard (4004): DOWN

echo.
echo ================================================
echo All services started!
echo ================================================
echo.
echo Logs available in .\logs\ directory
echo.
echo To run end-to-end test:
echo   python test_e2e_workflow.py
echo.
echo To stop all services:
echo   stop_agents.bat
echo.
echo Press Ctrl+C to stop this script (services will continue running)
echo.

pause
