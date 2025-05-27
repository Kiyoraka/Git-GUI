@echo off
echo Git-OneClick GUI Builder
echo ======================
echo.

REM Check if Python is installed
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b
)

REM Install required packages
echo Installing required packages...
pip install pyinstaller

REM Create development_types.json if not exists
echo Creating configuration files...
python -c "import json; open('development_types.json', 'w').write(json.dumps({}, indent=2)) if not os.path.exists('development_types.json') else None"

REM Create the executable with development_types.json as a resource
echo Creating executable...
pyinstaller --onefile --windowed --add-data "development_types.json;." --name "Git-OneClick" git_oneclick_gui.py

echo.
echo Build completed!
echo The executable is located in the "dist" folder.
echo.
echo Remember to:
echo 1. Ensure Git is installed on the target system
echo 2. Place the executable in a location where it can be easily accessed
echo 3. You can customize development types through the application's settings
echo.

pause