# KenjiDMTool_Launcher.ps1
#
# Clickable launcher for the TTRPG dashboard.
# Flow: stop running instance -> chapter-close last-active character if
# enough activity -> show character picker -> launch selected character.
#
# Run from PowerShell, or double-click the companion KenjiDMTool_Launcher.bat
# (which bypasses execution-policy friction).
#
# NOTE: ASCII-only. Windows PowerShell 5.1 reads scripts as ANSI by default,
# which corrupts UTF-8 multi-byte characters and breaks string parsing.

$ErrorActionPreference = "Continue"
$base = Split-Path -Parent $MyInvocation.MyCommand.Path
$exe  = Join-Path $base "dist\Kenji DM Tool.exe"
$manifestsDir = Join-Path $base "manifests"
$lastCharFile = Join-Path $base ".last_character"
$closePy = Join-Path $base "_chapter_close_check.py"
$ttrpgRoot = Split-Path -Parent (Split-Path -Parent $base)

Write-Host "=================================================================="
Write-Host "  Kenji DM Tool - Launcher"
Write-Host "=================================================================="
Write-Host "Base:        $base"
Write-Host "Exe:         $exe"
Write-Host "Manifests:   $manifestsDir"
Write-Host "TTRPG root:  $ttrpgRoot"
Write-Host ""

# Sanity: the exe must exist before we do anything.
if (-not (Test-Path $exe)) {
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show(
        "Dashboard executable not found:`n$exe`n`nBuild it first via build_exe.bat, or run from source.",
        "Kenji DM Tool - Launcher Error")
    exit 1
}

# 1. Stop any running dashboard.
Write-Host "[1/4] Stopping any running dashboard instance..."
Stop-Process -Name "Kenji DM Tool*" -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 500

# Pick a Python launcher: prefer 'py' (Windows Python launcher), fall back
# to 'python', then 'python3'. None present = skip chapter-close.
$pythonCmd = $null
foreach ($candidate in @("py", "python", "python3")) {
    try {
        $null = & $candidate --version 2>&1
        if ($LASTEXITCODE -eq 0) { $pythonCmd = $candidate; break }
    } catch {}
}
if (-not $pythonCmd) {
    Write-Host "  WARNING: No Python launcher found on PATH (tried py, python, python3)."
    Write-Host "  Chapter-close check will be skipped."
}

# 2. Chapter-close last-active character if it has 5+ paragraphs of activity.
Write-Host "[2/4] Checking chapter-close eligibility for last-active character..."
$lastChar = ""
if ((Test-Path $lastCharFile) -and $pythonCmd) {
    $lastChar = (Get-Content $lastCharFile -Raw).Trim().ToLower()
    if ($lastChar) {
        $manifestPath = Join-Path $manifestsDir "$lastChar.json"
        if (Test-Path $manifestPath) {
            try {
                $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
                $stateFile = Join-Path $ttrpgRoot $manifest.state_file
                if (Test-Path $stateFile) {
                    Write-Host "  Last-active: $lastChar"
                    Write-Host "  State:       $stateFile"
                    & $pythonCmd $closePy $stateFile
                } else {
                    Write-Host "  Skipped - state file not found: $stateFile"
                }
            } catch {
                $msg = $_.Exception.Message
                Write-Host "  Skipped - error reading manifest: $msg"
            }
        } else {
            Write-Host "  Skipped - no manifest for '$lastChar' at $manifestPath"
        }
    } else {
        Write-Host "  Skipped - .last_character file is empty."
    }
} else {
    if (-not (Test-Path $lastCharFile)) {
        Write-Host "  Skipped - no .last_character file (first launch?)"
    }
}

# 3. Discover available characters from manifests folder.
Write-Host "[3/4] Building character list..."
$manifests = Get-ChildItem -Path $manifestsDir -Filter "*.json" -ErrorAction SilentlyContinue
if (-not $manifests) {
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show(
        "No character manifests found in:`n$manifestsDir",
        "Kenji DM Tool")
    exit 1
}

$choices = @()
foreach ($m in $manifests) {
    $charId = [System.IO.Path]::GetFileNameWithoutExtension($m.Name)
    $display = (Get-Culture).TextInfo.ToTitleCase($charId.Replace("_", " "))
    $status = ""
    try {
        $mf = Get-Content $m.FullName -Raw | ConvertFrom-Json
        $sf = Join-Path $ttrpgRoot $mf.state_file
        if (Test-Path $sf) {
            $st = Get-Content $sf -Raw | ConvertFrom-Json
            $ch = $st._chapter
            $cs = $st._chapter_status
            if ($ch) { $status = "  [Ch.$ch $cs]" }
        }
    } catch {}
    $choices += [PSCustomObject]@{ Id = $charId; Display = "$display$status" }
}
Write-Host "  Found $($choices.Count) character(s)."

# 4. Picker dialog.
Write-Host "[4/4] Showing picker..."
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$form = New-Object System.Windows.Forms.Form
$form.Text = "Kenji DM Tool - Pick Character"
$form.Size = New-Object System.Drawing.Size(460, 380)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false
$form.MinimizeBox = $false
$form.BackColor = [System.Drawing.Color]::FromArgb(28, 32, 40)
$form.ForeColor = [System.Drawing.Color]::FromArgb(220, 220, 220)

$lbl = New-Object System.Windows.Forms.Label
$lbl.Text = "Pick a character to play. Previous character's chapter saved if it had enough activity."
$lbl.Location = New-Object System.Drawing.Point(20, 14)
$lbl.Size = New-Object System.Drawing.Size(420, 36)
$lbl.ForeColor = [System.Drawing.Color]::FromArgb(200, 180, 100)
$form.Controls.Add($lbl)

$listBox = New-Object System.Windows.Forms.ListBox
$listBox.Location = New-Object System.Drawing.Point(20, 54)
$listBox.Size = New-Object System.Drawing.Size(420, 220)
$listBox.Font = New-Object System.Drawing.Font("Consolas", 11)
$listBox.BackColor = [System.Drawing.Color]::FromArgb(40, 44, 52)
$listBox.ForeColor = [System.Drawing.Color]::FromArgb(220, 220, 220)
foreach ($c in $choices) { [void]$listBox.Items.Add($c.Display) }
if ($listBox.Items.Count -gt 0) { $listBox.SelectedIndex = 0 }
$form.Controls.Add($listBox)

# Pre-select the last-active character if available.
if ($lastChar) {
    for ($i = 0; $i -lt $choices.Count; $i++) {
        if ($choices[$i].Id -eq $lastChar) { $listBox.SelectedIndex = $i; break }
    }
}

$btnLaunch = New-Object System.Windows.Forms.Button
$btnLaunch.Text = "Launch"
$btnLaunch.Location = New-Object System.Drawing.Point(20, 290)
$btnLaunch.Size = New-Object System.Drawing.Size(200, 38)
$btnLaunch.BackColor = [System.Drawing.Color]::FromArgb(180, 140, 60)
$btnLaunch.ForeColor = [System.Drawing.Color]::White
$btnLaunch.FlatStyle = "Flat"
$btnLaunch.Add_Click({
    if ($listBox.SelectedIndex -ge 0) {
        $form.Tag = $choices[$listBox.SelectedIndex].Id
        $form.Close()
    }
})
$form.Controls.Add($btnLaunch)
$form.AcceptButton = $btnLaunch

$btnCancel = New-Object System.Windows.Forms.Button
$btnCancel.Text = "Cancel"
$btnCancel.Location = New-Object System.Drawing.Point(240, 290)
$btnCancel.Size = New-Object System.Drawing.Size(200, 38)
$btnCancel.BackColor = [System.Drawing.Color]::FromArgb(60, 64, 72)
$btnCancel.ForeColor = [System.Drawing.Color]::White
$btnCancel.FlatStyle = "Flat"
$btnCancel.Add_Click({ $form.Close() })
$form.Controls.Add($btnCancel)

[void]$form.ShowDialog()
$selected = $form.Tag
if (-not $selected) {
    Write-Host "Cancelled - no character selected."
    exit 0
}

# 5. Launch the dashboard with the selected character.
Write-Host "Launching: $selected"
Start-Process -FilePath $exe -ArgumentList "--character", $selected
Write-Host "Done."
