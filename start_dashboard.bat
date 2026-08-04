@echo off
setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
set "DASHBOARD_DIR=%SCRIPT_DIR%assets\email-review-dashboard-cap"

echo ================================================
echo Email Review Dashboard Setup and Start
echo ================================================
echo.

REM Check if Node.js is installed
echo [1/4] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Node.js is not installed!
    echo.
    echo Please install Node.js from: https://nodejs.org/
    echo Download the LTS version and run the installer.
    echo Then run this script again.
    echo.
    pause
    exit /b 1
)

echo [OK] Node.js detected:
node --version
echo [OK] npm version:
npm --version
echo.

REM Check if dashboard directory exists
echo [2/4] Checking dashboard directory...
if not exist "%DASHBOARD_DIR%" (
    echo.
    echo [ERROR] Dashboard directory not found!
    echo Expected location: %DASHBOARD_DIR%
    echo.
    pause
    exit /b 1
)
echo [OK] Dashboard directory found
echo.

REM Navigate to dashboard directory
cd /d "%DASHBOARD_DIR%"

REM Check if node_modules exists, if not install dependencies
echo [3/4] Checking dependencies...
if not exist "node_modules" (
    echo Dependencies not found. Installing...
    echo This may take a few minutes on first run...
    echo.
    call npm install
    if errorlevel 1 (
        echo.
        echo [ERROR] npm install failed!
        echo Please check your internet connection and try again.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [OK] Dependencies installed successfully!
) else (
    echo [OK] Dependencies already installed
)
echo.

REM Check if server.js exists
if not exist "server.js" (
    echo.
    echo [ERROR] server.js not found!
    echo Expected location: %DASHBOARD_DIR%\server.js
    echo.
    pause
    exit /b 1
)

REM Start the server
echo [4/4] Starting Dashboard Server...
echo ================================================
echo.
echo Dashboard Server Starting on port 4004...
echo.
echo Once started, access the dashboard at:
echo   http://localhost:4004
echo.
echo API endpoint:
echo   http://localhost:4004/api/review/ReviewCases
echo.
echo ================================================
echo Press Ctrl+C to stop the server
echo ================================================
echo.

REM Start the server and keep window open
node server.js

REM If server stops unexpectedly
echo.
echo.
echo ================================================
echo [WARNING] Server has stopped
echo ================================================
echo.
echo The server has stopped running. This could be due to:
echo   - Manual stop (Ctrl+C)
echo   - Port 4004 already in use
echo   - Server crash or error
echo.
echo Check the error messages above for details.
echo.
pause
