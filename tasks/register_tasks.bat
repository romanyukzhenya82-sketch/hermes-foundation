@echo off
echo Registering Hermes Foundation scheduled tasks...

REM --- Hourly agents scan ---
schtasks /Create /SC HOURLY /MO 1 /TN "Hermes_Agents_Hourly" /TR "cmd.exe /c \"C:\Users\DJlinnuJ\hermes_foundation\run_agents.bat\"" /ST 06:00 /F
if %ERRORLEVEL% EQU 0 (
    echo [OK] Hermes_Agents_Hourly registered
) else (
    echo [FAIL] Hermes_Agents_Hourly — error %ERRORLEVEL%
)

REM --- Daily evaluate at 08:00 ---
schtasks /Create /SC DAILY /TN "Hermes_Evaluate_Daily" /TR "cmd.exe /c \"C:\Users\DJlinnuJ\hermes_foundation\run_evaluate.bat\"" /ST 08:00 /F
if %ERRORLEVEL% EQU 0 (
    echo [OK] Hermes_Evaluate_Daily registered
) else (
    echo [FAIL] Hermes_Evaluate_Daily — error %ERRORLEVEL%
)

echo.
echo Listing Hermes tasks:
schtasks /Query /TN "Hermes_Agents_Hourly" /FO LIST 2>NUL
schtasks /Query /TN "Hermes_Evaluate_Daily" /FO LIST 2>NUL

echo Done.
pause
