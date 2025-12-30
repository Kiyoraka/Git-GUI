@echo off
echo ============================================
echo   Git-OneClick Normal Version - Build Script
echo ============================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo.
echo Building Git-OneClick Normal Version...
echo.

REM Build the executable
pyinstaller --onefile --windowed --icon=git-gui.ico --name="Git-OneClick" --add-data "development_types.json;." git_oneclick_normal.py

echo.
echo ============================================
echo   Build Complete!
echo   Output: dist\Git-OneClick.exe
echo ============================================
echo.
pause
