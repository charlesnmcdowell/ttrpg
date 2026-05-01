@echo off
REM Build Kenji DM Tool as a standalone .exe
REM Requires Python 3.10+ on Windows
REM Auto-installs: customtkinter, pyinstaller

echo ============================================
echo   Building Kenji DM Tool — standalone .exe
echo ============================================

echo.
echo Installing build dependencies...
pip install customtkinter pyinstaller anthropic

REM To DEBUG silent crashes: change "--noconsole" below to "--console"
REM (a console window will appear behind the GUI showing all errors).
REM For production builds, keep "--noconsole" to hide the console window.

echo.
echo Bundling all engine modules + tools + lore docs...
pyinstaller --onefile --noconsole ^
    --name "Kenji DM Tool" ^
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
echo   Build complete!
echo   Output:  dist\Kenji DM Tool.exe
echo.
echo   The .exe is fully self-contained — Python is NOT
echo   required on the target machine.
echo.
echo   To run:
echo     1. Copy "Kenji DM Tool.exe" to a folder
echo     2. Place your campaign folders alongside it
echo        (Cookie\, Amaris\, your-character\, etc.)
echo     3. Place realm_lore_registry.json +
echo        shared_world_continuity.md + templates\
echo        in the parent of the .exe
echo     4. Double-click the .exe — GUI dashboard launches
echo.
echo   For CLI / new-character wizard mode, run from
echo   command line:
echo     "Kenji DM Tool.exe" --campaign "Cookie\Game init files"
echo ============================================
pause
