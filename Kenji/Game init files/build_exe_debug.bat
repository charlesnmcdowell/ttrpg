@echo off
REM DEBUG build of Kenji DM Tool — keeps the console window visible
REM so any silent crash / error / traceback is captured.
REM Output: dist\Kenji DM Tool DEBUG.exe
REM
REM Use this when "Kenji DM Tool.exe" runs but does nothing visible.
REM Run the DEBUG .exe and the console window behind the GUI will show
REM all stderr/stdout including Python tracebacks.

echo ============================================
echo   Building Kenji DM Tool — DEBUG build
echo   (console window visible, errors readable)
echo ============================================

echo.
echo Installing build dependencies...
pip install customtkinter pyinstaller anthropic

echo.
echo Bundling for debug...
pyinstaller --onefile --console ^
    --name "Kenji DM Tool DEBUG" ^
    --add-data "ttrpg_game_engine.py;." ^
    --add-data "gamemode.py;." ^
    --add-data "_dm_turn.py;." ^
    --add-data "continuity_engine.py;." ^
    --add-data "trigger_engine.py;." ^
    --add-data "chapter_close.py;." ^
    --add-data "generate_starter_campaign.py;." ^
    --add-data "engine_v2.py;." ^
    --add-data "run_arc_pointer.py;." ^
    --add-data "_strip_dm_notes.py;." ^
    --add-data "prose_state_extractor.py;." ^
    --add-data "play_engine.py;." ^
    --collect-all anthropic ^
    --add-data "character_tracker.md;." ^
    --add-data "dm_rules_tracking.md;." ^
    --add-data "DM_TURN_PROTOCOL.md;." ^
    --add-data "SESSION_MEMORY.md;." ^
    --add-data "tracking_rules.md;." ^
    --add-data "npc_name_bank.md;." ^
    --add-data "world_calendar_lore.md;." ^
    --add-data "AI_CONTEXT.md;." ^
    --add-data "manifests;manifests" ^
    kenji_gui.py

echo.
echo ============================================
echo   DEBUG build complete!
echo   Output: dist\Kenji DM Tool DEBUG.exe
echo.
echo   Run from PowerShell:
echo     ^& ".\Kenji DM Tool DEBUG.exe" --campaign "..\Cookie\Game init files"
echo.
echo   The console window will stay open behind the GUI
echo   and show any errors / tracebacks. Copy any visible
echo   error and share it for debugging.
echo ============================================
pause
