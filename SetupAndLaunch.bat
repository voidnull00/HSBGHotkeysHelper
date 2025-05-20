@echo off
REM ───────────────────────────────────────────────
REM SetupAndLaunch.bat
REM Installs requirements (once) and launches HSBGHotkeysHelper
REM ───────────────────────────────────────────────

cd /d "%~dp0"

echo Checking and installing dependencies...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

echo.
echo Launching Hearthstone Battlegrounds Hotkey Helper...
python HSBGHotkeysHelper.py

pause
