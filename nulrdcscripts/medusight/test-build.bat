@echo off
echo ========================================
echo Testing PyInstaller Build for MeduSight
echo ========================================
echo.

REM Build just the Python executable
echo Building Python executable...
call poetry run pyinstaller medusight.spec --clean --noconfirm --distpath dist --workpath build

if errorlevel 1 (
    echo.
    echo Build FAILED!
    pause
    exit /b 1
)

echo.
echo Build completed!
echo.

REM Check if executable exists
if exist "dist\MeduSight.exe" (
    echo âœ" Executable created: dist\MeduSight.exe
    echo.
    echo Testing executable...
    echo.
    start "" "dist\MeduSight.exe"
) else (
    echo âœ— Executable NOT found at dist\MeduSight.exe
)

echo.
pause