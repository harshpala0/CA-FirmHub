@echo off
REM ╔══════════════════════════════════════════════════════════════╗
REM ║     AUDIT MANAGEMENT v4 — EXE BUILDER (Admin Only)          ║
REM ╚══════════════════════════════════════════════════════════════╝
cd /d "%~dp0"
echo.
echo  =====================================================
echo    AUDIT MANAGEMENT v4 -- Building .exe Package
echo  =====================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found.
    pause & exit /b 1
)
echo  [OK] Python found

echo  [STEP 1/4] Installing dependencies...
pip install -q pyinstaller pyinstaller-hooks-contrib
pip install -q Flask PyJWT Werkzeug python-docx openpyxl waitress
echo  [OK] Dependencies installed

if not exist firm_identity.json (
    echo  [ERROR] firm_identity.json not found!
    echo  Run this from inside a generated firm package folder.
    pause & exit /b 1
)
echo  [OK] firm_identity.json found

echo  [STEP 2/4] Cleaning previous build...
if exist dist\CAFirmHub rmdir /s /q dist\CAFirmHub
if exist build rmdir /s /q build
echo  [OK] Cleaned

echo  [STEP 3/4] Building exe (this takes 2-5 minutes)...
echo.
python -m PyInstaller audit_management.spec --noconfirm --clean
echo.

if not exist dist\CAFirmHub\CAFirmHub.exe (
    echo  [ERROR] Build failed! Check output above.
    pause & exit /b 1
)
echo  [OK] Build successful

echo  [STEP 4/4] Finalising package...
if not exist dist\CAFirmHub\uploads  mkdir dist\CAFirmHub\uploads
if not exist dist\CAFirmHub\booklets mkdir dist\CAFirmHub\booklets
if not exist dist\CAFirmHub\exports  mkdir dist\CAFirmHub\exports

copy /y firm_identity.json dist\CAFirmHub\firm_identity.json >nul
echo  [OK] firm_identity.json copied

REM ── Create START_HERE.bat that shows errors clearly ───────────
(
echo @echo off
echo cd /d "%%~dp0"
echo echo.
echo echo   ==========================================
echo echo     CA FirmHub
echo echo   ==========================================
echo echo.
echo echo   Starting server... browser will open automatically.
echo echo   Do NOT close this window while using the app.
echo echo   The server stops automatically when you Sign Out.
echo echo.
echo CAFirmHub.exe
echo set EXIT_CODE=%%ERRORLEVEL%%
echo echo.
echo if %%EXIT_CODE%% NEQ 0 (
echo     echo   [ERROR] Server stopped unexpectedly! Code: %%EXIT_CODE%%
echo     echo   Please send this window as screenshot to your administrator.
echo ) else (
echo     echo   Server has stopped. Safe to close this window.
echo )
echo echo.
echo pause
) > dist\CAFirmHub\START_HERE.bat

REM ── Create a DEBUG launcher to capture crash errors ───────────
(
echo @echo off
echo cd /d "%%~dp0"
echo echo ============================================================
echo echo  DEBUG MODE - CA FirmHub
echo echo  This window shows all errors for troubleshooting.
echo echo ============================================================
echo echo.
echo echo Running CAFirmHub.exe...
echo echo.
echo CAFirmHub.exe 2^>^&1
echo echo.
echo echo ============================================================
echo echo  EXIT CODE: %%ERRORLEVEL%%
echo echo  If you see errors above, screenshot this and send to admin.
echo echo ============================================================
echo pause
) > dist\CAFirmHub\DEBUG_RUN.bat

echo  [OK] START_HERE.bat and DEBUG_RUN.bat created

echo.
echo  =====================================================
echo    BUILD COMPLETE
echo  =====================================================
echo.
echo  Package ready at: %~dp0dist\CAFirmHub\
echo.
echo  Share the CAFirmHub folder (zipped) with the CA firm.
echo  They double-click START_HERE.bat to launch.
echo.
dir /b dist\CAFirmHub\
echo.
pause
