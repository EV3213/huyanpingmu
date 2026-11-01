@echo off
rem EyeGuard installer - double click, then choose language (1 = Chinese, 2 = English)
setlocal
set "PY="
for /d %%d in ("%USERPROFILE%\.workbuddy\binaries\python\versions\*") do set "PY=%%d\python.exe"
if not exist "%PY%" (
  echo [EyeGuard] Python runtime not found.
  echo Please reinstall WorkBuddy first.
  pause
  exit /b 1
)
"%PY%" "%~dp0install.py"
echo.
pause
endlocal
