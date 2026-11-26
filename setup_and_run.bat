@echo off
cd /d "%~dp0"

echo ===================================================
echo [1/4] Checking Python installation...
echo ===================================================

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH!
    echo Please install Python (version 3.10 or higher) and make sure
    echo to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b
)

echo Python is detected successfully.

echo ===================================================
echo [2/4] Setting up Virtual Environment (venv)...
echo ===================================================

if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b
    )
)

echo ===================================================
echo [3/4] Installing / Updating Packages...
echo ===================================================

if exist "requirements.txt" (
    echo Installing requirements from requirements.txt...
    "%~dp0venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
    "%~dp0venv\Scripts\python.exe" -m pip install -r requirements.txt
)

echo ===================================================
echo [4/4] Setting up Database...
echo ===================================================

"%~dp0venv\Scripts\python.exe" manage.py migrate

echo ===================================================
echo SETUP COMPLETED SUCCESSFULLY!
echo Now starting the project...
echo ===================================================

start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8000/"

"%~dp0venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000

pause
