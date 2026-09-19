param(
    [string]$GamePath = (Join-Path $env:USERPROFILE 'Downloads\funkin-windows-64bit')
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $projectRoot 'mods\energize'
$gameRoot = (Resolve-Path -LiteralPath $GamePath).Path
if (-not (Test-Path -LiteralPath (Join-Path $gameRoot 'Funkin.exe'))) {
    throw "Funkin.exe is missing from $gameRoot"
}
$modsRoot = Join-Path $gameRoot 'mods'
$target = Join-Path $modsRoot 'energize'
if (Test-Path -LiteralPath $target) {
    $manifest = Join-Path $target '_polymod_meta.json'
    if (-not (Test-Path -LiteralPath $manifest)) { throw 'An unrelated energize folder already exists.' }
    $existing = Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
    if ($existing.id -ne 'energize-volt') { throw 'An unrelated energize mod already exists.' }
    $backupRoot = Join-Path $projectRoot 'backups'
    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
    $backup = Join-Path $backupRoot ('energize-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
    Copy-Item -LiteralPath $target -Destination $backup -Recurse
}
New-Item -ItemType Directory -Path $target -Force | Out-Null
Get-ChildItem -LiteralPath $source -Force | Copy-Item -Destination $target -Recurse -Force
Write-Host "Installed ENERGIZE to $target"
Write-Host 'Restart FNF. Open Freeplay > Energize, or Story Mode > ENERGIZE: VS VOLT.'
