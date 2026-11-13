@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1"
set "lumina_exit=%ERRORLEVEL%"
if not "%lumina_exit%"=="0" (
  echo.
  echo Lumina could not start. Read the error above.
  echo If it is already running, use the existing browser link or stop its original terminal first.
  pause
)
exit /b %lumina_exit%
