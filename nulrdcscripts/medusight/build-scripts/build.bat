@echo off
setlocal enabledelayedexpansion

echo ================================
echo Building MeduSight Distribution
echo ================================
echo.

REM Get the script's directory and project root
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
cd /d "%PROJECT_ROOT%"

REM Step 1: Install Python dependencies
echo Step 1: Installing Python dependencies...
call poetry install --no-interaction
if errorlevel 1 (
    echo Error: Failed to install Python dependencies
    exit /b 1
)

REM Step 2: Build Python executable with PyInstaller
echo.
echo Step 2: Building Python executable...
call poetry run pyinstaller medusight.spec --clean --noconfirm --distpath dist --workpath build
if errorlevel 1 (
    echo Error: Failed to build Python executable
    exit /b 1
)

if not exist "dist\medusight\medusight.exe" (
    echo Error: Python executable not created!
    exit /b 1
)

echo Python executable created successfully
echo.

REM Step 3: Setup Electron
echo Step 3: Setting up Electron...
cd electron

if not exist "node_modules\" (
    echo Installing Electron dependencies...
    call npm install
    if errorlevel 1 (
        echo Error: Failed to install Electron dependencies
        exit /b 1
    )
)

REM Step 4: Verify Python dist
echo.
echo Step 4: Verifying Python executable...
if exist "..\dist\medusight\" (
    echo Python dist folder ready for packaging
) else (
    echo Error: Python dist folder not found!
    exit /b 1
)

REM Step 5: Build Electron app
echo.
echo Step 5: Building Electron application...
call npm run build:win
if errorlevel 1 (
    echo Error: Failed to build Electron application
    exit /b 1
)

echo.
echo ================================
echo Build completed successfully!
echo ================================
echo.
echo Your application is in: electron\dist\
echo.
echo To run in development mode:
echo   1. Terminal 1: poetry run python medusight\main.py
echo   2. Terminal 2: cd electron ^&^& npm start
echo.

pause