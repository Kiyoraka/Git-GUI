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

REM Check if icon file exists
if not exist "git-gui.ico" (
    echo Warning: git-gui.ico not found in current directory
    echo The executable will be created without a custom icon
    echo.
    set ICON_PARAM=
) else (
    echo Found git-gui.ico - will use as application icon
    set ICON_PARAM=--icon="git-gui.ico"
)

REM Install required packages
echo Installing required packages...
pip install pyinstaller

REM Create development_types.json if not exists
echo Creating configuration files...
python -c "import json; import os; open('development_types.json', 'w').write(json.dumps({}, indent=2)) if not os.path.exists('development_types.json') else None"

REM Create the executable with development_types.json as a resource and optional icon
echo Creating executable...
if defined ICON_PARAM (
    pyinstaller --onefile --windowed %ICON_PARAM% --add-data "development_types.json;." --name "Git-OneClick" git_oneclick_gui.py
) else (
    pyinstaller --onefile --windowed --add-data "development_types.json;." --name "Git-OneClick" git_oneclick_gui.py
)

echo.
echo Build completed!
echo The executable is located in the "dist" folder.
echo.
echo Remember to:
echo 1. Ensure Git is installed on the target system
echo 2. Place the executable in a location where it can be easily accessed
echo 3. You can customize development types through the application's settings
if exist "git-gui.ico" (
    echo 4. The application icon has been set to git-gui.ico
)
echo.

pause