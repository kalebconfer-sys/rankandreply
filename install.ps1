# Rank and Reply: puts the whole project on this Windows computer.
#
# Paste this one line into PowerShell (Start menu > type PowerShell > Enter):
#   irm https://raw.githubusercontent.com/kalebconfer-sys/rankandreply/refs/heads/claude/ai-automated-business-plan-ptu9y7/install.ps1 | iex
#
# What it does:
#   1. Downloads every project file into Documents\RankAndReply
#   2. Pins that folder to Quick access (the left side of File Explorer)
#   3. Puts a "Rank and Reply" shortcut on the Desktop
#   4. Creates the command  rankandreply  : type it in any terminal to open Claude on the project
# Running it again updates the files. It never touches your private files
# (business\tools\.env, business\data\, .venv), because those aren't in the download.

& {  # runs in its own scope, so nothing changes in your PowerShell session
$ErrorActionPreference = 'Stop'
$branch = 'claude/ai-automated-business-plan-ptu9y7'
$zipUrl = "https://github.com/kalebconfer-sys/rankandreply/archive/refs/heads/$branch.zip"
$dest = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'RankAndReply'
$tmp = Join-Path $env:TEMP ('rankandreply-' + [guid]::NewGuid().ToString('N'))

Write-Host ''
Write-Host '  Rank and Reply: getting the project onto this computer' -ForegroundColor Cyan
Write-Host ''

try {
    New-Item -ItemType Directory -Path $tmp -Force | Out-Null
    Write-Host '  1/4 Downloading the latest files...'
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $zipUrl -OutFile (Join-Path $tmp 'project.zip') -UseBasicParsing
    Expand-Archive -Path (Join-Path $tmp 'project.zip') -DestinationPath $tmp -Force
    $src = Get-ChildItem -Path $tmp -Directory | Select-Object -First 1
    if (-not $src) { throw 'The download was empty.' }

    $updating = Test-Path $dest
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
    # Copy over the top: new and changed files replace old ones; private files stay untouched.
    Copy-Item -Path (Join-Path $src.FullName '*') -Destination $dest -Recurse -Force
    if ($updating) { Write-Host "      Updated $dest" } else { Write-Host "      Saved to $dest" }
}
finally {
    if (Test-Path $tmp) { Remove-Item -Path $tmp -Recurse -Force -ErrorAction SilentlyContinue }
}

Write-Host '  2/4 Pinning the folder in File Explorer...'
try {
    $shell = New-Object -ComObject Shell.Application
    $quick = $shell.Namespace('shell:::{679f85cb-0220-4080-b29b-5540cc05aab6}')
    $pinned = $false
    if ($quick) { foreach ($item in $quick.Items()) { if ($item.Path -eq $dest) { $pinned = $true } } }
    if (-not $pinned) { $shell.Namespace($dest).Self.InvokeVerb('pintohome') }
} catch {
    Write-Host '      (Could not pin automatically. Right-click the folder > Pin to Quick access.)'
}

Write-Host '  3/4 Adding a Desktop shortcut...'
try {
    $desktop = [Environment]::GetFolderPath('Desktop')
    $wsh = New-Object -ComObject WScript.Shell
    $link = $wsh.CreateShortcut((Join-Path $desktop 'Rank and Reply.lnk'))
    $link.TargetPath = $dest
    $link.Save()
} catch {
    Write-Host '      (Could not create the shortcut. The folder is in Documents\RankAndReply.)'
}

Write-Host '  4/4 Creating the command: rankandreply'
# This folder is on every Windows 10/11 user's PATH, so a file here works as a command in any terminal.
$cmdDir = Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps'
$cmd = @"
@echo off
cd /d "$dest"
where claude >nul 2>nul
if errorlevel 1 (
  echo.
  echo  Opening the Rank and Reply folder.
  echo  To work with Claude here: open the Claude desktop app, choose Code, and pick this folder,
  echo  or install Claude Code so that typing  rankandreply  opens Claude right in the project.
  start "" explorer "$dest"
) else (
  claude
)
"@
try {
    New-Item -ItemType Directory -Path $cmdDir -Force | Out-Null
    Set-Content -Path (Join-Path $cmdDir 'rankandreply.cmd') -Value $cmd -Encoding Ascii
} catch {
    Write-Host '      (Could not create the command. Open the folder from the Desktop shortcut instead.)'
}

Write-Host ''
Write-Host '  Done.' -ForegroundColor Green
Write-Host "  - Your project: $dest (pinned in File Explorer, and on the Desktop)"
Write-Host '  - From now on, type  rankandreply  in any terminal (open a NEW one first) to open Claude on it.'
Write-Host '  - First time only: open business\tools and double-click setup.bat (see business\SETUP.md).'
Write-Host '  - To get the newest version later, paste the same line again.'
Write-Host ''
Start-Process explorer.exe $dest
}
