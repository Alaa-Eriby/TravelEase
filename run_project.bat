@echo off
cd /d "%~dp0"

echo ===================================================
echo Starting TravelEase Application...
echo ===================================================

start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8000/"

echo Server is starting at http://127.0.0.1:8000/
echo Close this window or press Ctrl+C to stop the server.
echo ===================================================

"%~dp0venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000

pause
