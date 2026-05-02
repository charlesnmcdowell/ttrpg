@echo off
REM KenjiDMTool_Launcher.bat — double-clickable wrapper for the launcher.
REM Bypasses PowerShell execution policy. Window stays visible so errors
REM surface — close it manually after the dashboard launches.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0KenjiDMTool_Launcher.ps1"
if errorlevel 1 (
    echo.
    echo Launcher exited with error code %errorlevel%.
    pause
)
