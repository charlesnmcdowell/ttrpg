@echo off
REM Create_Chapter_TTS_Shortcut.bat - one-click wrapper for the shortcut
REM installer PowerShell script. Bypasses PowerShell's execution policy
REM so users don't have to fiddle with security settings.
REM
REM Run this once. It places "Chapter TTS" on your Desktop pointing at
REM Run_Chapter_TTS.bat in this folder. After that you can delete this
REM installer if you want - the shortcut keeps working.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Create_Chapter_TTS_Shortcut.ps1"

if errorlevel 1 (
    echo.
    echo Installer exited with error code %errorlevel%.
    pause
)
