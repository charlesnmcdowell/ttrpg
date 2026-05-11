@echo off
REM Run_Chapter_TTS.bat - double-clickable launcher for the chapter audiobook
REM generator. Prompts for a chapter file path, parses speakers via Claude,
REM validates voice IDs in tts_config.json, then synthesizes via ElevenLabs.
REM
REM No rebuild needed when chapter_tts.py changes - this .bat just calls the
REM Python script directly.

setlocal
cd /d "%~dp0"

REM Make the title bar useful when the window is on the taskbar.
title Chapter TTS - Audiobook Generator

REM Find Python. Prefer "py -3" (Windows Python launcher) which handles the
REM 3.x picker; fall back to "python" on PATH.
where py >nul 2>nul
if %errorlevel% equ 0 (
    set "PY=py -3"
) else (
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        set "PY=python"
    ) else (
        echo.
        echo ERROR: Python is not installed or not on PATH.
        echo.
        echo Install Python 3.10 or later from https://www.python.org/downloads/
        echo Make sure to check "Add Python to PATH" during installation.
        echo.
        pause
        exit /b 1
    )
)

REM Quick check that the anthropic SDK is importable. If not, offer to install.
%PY% -c "import anthropic" >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo The 'anthropic' Python package is not installed.
    echo It is required for the speaker-attribution step.
    echo.
    set /p INSTALL="Install it now via pip? (y/n): "
    if /i "%INSTALL%"=="y" (
        %PY% -m pip install anthropic
        if errorlevel 1 (
            echo.
            echo pip install failed. Try running manually:
            echo     %PY% -m pip install anthropic
            echo.
            pause
            exit /b 1
        )
    ) else (
        echo Cannot continue without the anthropic package. Exiting.
        pause
        exit /b 1
    )
)

REM Run the interactive script. It handles the prompt, dry-run offer, and
REM pause-at-end. We don't pause here because the script does.
%PY% "%~dp0chapter_tts_interactive.py"

REM If the Python script crashed before its own pause-at-end ran, give the
REM user a chance to see why.
if errorlevel 99 (
    echo.
    echo Script crashed unexpectedly. See the error above.
    pause
)

endlocal
