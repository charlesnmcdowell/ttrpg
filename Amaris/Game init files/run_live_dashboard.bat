@echo off
REM Launches the shared Live Dashboard (Kenji repo) for this campaign save.
set "CAMPAIGN_DIR=%~dp0"
set "GUI_SCRIPT=%~dp0..\..\Kenji\Game init files\kenji_gui.py"
python "%GUI_SCRIPT%" --campaign "%CAMPAIGN_DIR%"
