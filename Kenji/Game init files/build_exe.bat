@echo off
REM Build Kenji DM Tool as a standalone .exe
REM Requires: pip install pyinstaller customtkinter

echo Installing dependencies...
pip install customtkinter pyinstaller

echo.
echo Building exe...
pyinstaller --onefile --noconsole ^
    --name "Kenji DM Tool" ^
    --add-data "ttrpg_game_engine.py;." ^
    kenji_gui.py

echo.
echo ============================================
echo   Build complete!
echo   Output: dist\Kenji DM Tool.exe
echo.
echo   Copy the exe next to kenji_state.json
echo   and ttrpg_game_engine.py to run it.
echo ============================================
pause
