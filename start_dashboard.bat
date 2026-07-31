@echo off
echo ================================================
echo Email Review Dashboard Setup and Start
echo ================================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo.
    echo Please install Node.js from: https://nodejs.org/
    echo Then run this script again.
    echo.
    pause
    exit /b 1
)

echo Node.js detected:
node --version
echo npm version:
npm --version
echo.

REM Navigate to dashboard directory
cd "%~dp0assets\email-review-dashboard-cap"

echo Installing dependencies...
echo This may take a few minutes on first run...
echo.

call npm install
if errorlevel 1 (
    echo ERROR: npm install failed
    pause
    exit /b 1
)

echo.
echo Installing Express...
call npm install express
if errorlevel 1 (
    echo ERROR: Express installation failed
    pause
    exit /b 1
)

echo.
echo ================================================
echo Starting Dashboard Server on port 4004...
echo ================================================
echo.
echo Dashboard will be available at:
echo   http://localhost:4004
echo.
echo API endpoint:
echo   http://localhost:4004/api/review/ReviewCases
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.

node server.js
