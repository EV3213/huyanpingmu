@echo off
rem EyeGuard parent app - settings window (password required)
setlocal
powershell -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0parent_ui.ps1"
endlocal
