# Create_Chapter_TTS_Shortcut.ps1 - one-shot installer that adds a
# "Chapter TTS" shortcut to the user's Desktop, pointing at the
# Run_Chapter_TTS.bat launcher in this folder.
#
# Run this once via Create_Chapter_TTS_Shortcut.bat (which handles
# PowerShell's execution policy). After it succeeds, the shortcut on
# your Desktop will work forever - re-run only if you ever move the
# Game init files folder.

$ErrorActionPreference = 'Stop'

Write-Host ""
Write-Host "============================================================"
Write-Host "  Chapter TTS - Desktop Shortcut Installer"
Write-Host "============================================================"
Write-Host ""

# Locate this script's folder (.../Kenji/Game init files/)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$targetBat = Join-Path $scriptDir 'Run_Chapter_TTS.bat'

if (-not (Test-Path $targetBat)) {
    Write-Host "ERROR: Run_Chapter_TTS.bat not found at:" -ForegroundColor Red
    Write-Host "  $targetBat"
    Write-Host ""
    Write-Host "Make sure this installer .ps1 lives next to Run_Chapter_TTS.bat."
    Read-Host "Press Enter to close"
    exit 1
}

# Resolve the user's Desktop. GetFolderPath('Desktop') correctly handles
# OneDrive-redirected Desktops (when "Back up your folders" is enabled in
# OneDrive, the Desktop lives under OneDrive instead of the user profile).
$desktop = [Environment]::GetFolderPath('Desktop')
if (-not (Test-Path $desktop)) {
    Write-Host "ERROR: Could not resolve Desktop folder." -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

$shortcutName = 'Chapter TTS.lnk'
$shortcutPath = Join-Path $desktop $shortcutName

# Warn before clobbering an existing shortcut
if (Test-Path $shortcutPath) {
    Write-Host "A shortcut already exists at:" -ForegroundColor Yellow
    Write-Host "  $shortcutPath"
    $ans = Read-Host "Overwrite it? (y/n)"
    if ($ans -notmatch '^[Yy]') {
        Write-Host "Cancelled. Existing shortcut left untouched."
        Read-Host "Press Enter to close"
        exit 0
    }
}

# Create the .lnk via the standard WScript.Shell COM object
try {
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath       = $targetBat
    $shortcut.WorkingDirectory = $scriptDir
    $shortcut.Description      = 'Generate audiobook narration from chapter markdown files via Claude + ElevenLabs.'
    # Speaker/audio icon from Windows' bundled imageres.dll. If you want a
    # different icon, right-click the shortcut > Properties > Change Icon.
    $shortcut.IconLocation     = "$env:SystemRoot\System32\imageres.dll,-122"
    $shortcut.Save()
} catch {
    Write-Host "ERROR: Could not create shortcut:" -ForegroundColor Red
    Write-Host "  $_"
    Read-Host "Press Enter to close"
    exit 1
}

Write-Host ""
Write-Host "Shortcut created successfully." -ForegroundColor Green
Write-Host ""
Write-Host "  Name:    Chapter TTS"
Write-Host "  Path:    $shortcutPath"
Write-Host "  Target:  $targetBat"
Write-Host ""
Write-Host "Double-click 'Chapter TTS' on your Desktop to launch the tool."
Write-Host ""
Read-Host "Press Enter to close"
