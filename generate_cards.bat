@echo off
setlocal
chcp 65001 > nul

echo ===============================================================================
echo   logiBUS(R) Mini-Trainer - Trainingskarten-Generator (4diac IEC 61499)
echo ===============================================================================
echo.

python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [FEHLER] Python wurde nicht im Pfad gefunden.
    echo Bitte stelle sicher, dass Python installiert und im PATH registriert ist.
    echo.
    pause
    exit /b 1
)

python generate_cards.py %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [FEHLER] Die Generierung ist mit einem Fehler abgebrochen.
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ===============================================================================
echo   Erfolgreich ausgefuehrt!
echo ===============================================================================
echo.
if "%~1"=="" (
    pause
)
endlocal
