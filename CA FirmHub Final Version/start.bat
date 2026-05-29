@echo off
REM ===============================================
REM  AUDIT MANAGEMENT SYSTEM v4 - Windows Launcher
REM  Double-click this file to start
REM  The server starts with the app and stops when
REM  you sign out — no manual management needed.
REM ===============================================
cd /d "%~dp0"
echo.
echo   ============================================
echo     AUDIT MANAGEMENT SYSTEM v4 - Setup
echo   ============================================
echo.

REM --- Check Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo   [ERROR] Python is not installed!
    echo.
    echo   Download from: https://python.org
    echo   IMPORTANT: Check "Add Python to PATH" during install!
    echo.
    pause
    exit /b 1
)
echo   [OK] Python found

REM --- Install Dependencies (silently) ---
echo   [SETUP] Checking required libraries...
pip install -q Flask PyJWT Werkzeug python-docx openpyxl waitress 2>nul
if errorlevel 1 (
    pip install Flask PyJWT Werkzeug python-docx openpyxl 2>nul
)
echo   [OK] Libraries ready

REM --- Create Directories ---
if not exist uploads mkdir uploads
if not exist booklets mkdir booklets
if not exist exports mkdir exports

REM --- Add Firewall Rule (needs admin, silent fail if not) ---
netsh advfirewall firewall delete rule name="CAFirmHub" >nul 2>&1
netsh advfirewall firewall add rule name="CAFirmHub" dir=in action=allow protocol=TCP localport=8000 >nul 2>&1

echo.
echo   ============================================
echo     Starting CA FirmHub Server...
echo   ============================================
echo.
echo   The browser will open automatically.
echo   If not, open: http://127.0.0.1:8000
echo.
echo   IMPORTANT: The server stops automatically
echo   when you Sign Out from the application.
echo   Do NOT close this window while using the app.
echo.

python main.py

REM --- If python exits (user signed out or Ctrl+C) ---
echo.
echo   ============================================
echo     Server has stopped.
echo   ============================================
echo.
echo   You have been signed out. It is safe to
echo   close this window.
echo.
pause
