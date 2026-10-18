param(
    [string]$Game = $env:EU5_GAME_ROOT,
    [string]$Cmf = $env:EU5_CMF_ROOT,
    [string]$SettingsFrom,
    [switch]$PrepareOnly,
    [switch]$NormalCharter,
    [switch]$Exchange
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
if (-not $Game) { $Game = 'C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V' }
if (-not $Cmf) { $Cmf = 'C:\Program Files (x86)\Steam\steamapps\workshop\content\3450310\3692202776' }
$exe = Join-Path $Game 'binaries/eu5.exe'
if (-not (Test-Path -LiteralPath $exe)) { throw "Licensed EUV installation missing: $exe" }
if (-not (Test-Path -LiteralPath (Join-Path $Cmf '.metadata/metadata.json'))) { throw 'CMF installation missing' }
Push-Location -LiteralPath $repo
try {
    python tools/audit_native.py --game (Join-Path $Game 'game') --cmf $Cmf --compare
    if ($LASTEXITCODE -ne 0) { throw 'Native/CMF source pin changed' }
    python tools/validate_sources.py
    if ($LASTEXITCODE -ne 0) { throw 'Mod source validation failed' }
    $token = [guid]::NewGuid().ToString('N')
    $userDir = Join-Path $repo "dist/interactive-$token/user"
    python tools/campaign_suite.py prepare --userdir $userDir --token $token
    if ($LASTEXITCODE -ne 0) { throw 'Test preparation failed' }
    if ($NormalCharter) {
        python tools/prepare_m0_ui.py --userdir $userDir
        if ($LASTEXITCODE -ne 0) { throw 'Normal charter UI fixture preparation failed' }
    }
    if ($Exchange) {
        python tools/prepare_m5_ui.py --userdir $userDir
        if ($LASTEXITCODE -ne 0) { throw 'Exchange UI fixture preparation failed' }
    }
    $bfi = Join-Path $userDir 'mod/bfi'
    Copy-Item -LiteralPath (Join-Path $repo 'mod/bfl') -Destination $bfi -Recurse
    if ($SettingsFrom) {
        Copy-Item -LiteralPath (Join-Path $SettingsFrom 'pdx_settings.json') -Destination $userDir
    }
    $mods = @($Cmf, $bfi, (Join-Path $userDir 'mod/bfi_campaign_checks')) | ForEach-Object {
        @{path = ($_.Replace('\','/') + '/'); isEnabled = $true}
    }
    @{file_version = '1.0.0'; playsets = @(@{
        name = 'BFI_INTERACTIVE_DISPOSABLE'; isActive = $true; isAutomaticallySorted = $false
        orderedListMods = $mods; DLC = @()
    })} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $userDir 'playsets.json') -Encoding utf8
    if (-not $PrepareOnly) {
        $arguments = @('-debug_mode', '-play=FLO', "-userdir=`"$userDir`"")
        $process = Start-Process -FilePath $exe -ArgumentList $arguments -WorkingDirectory (Join-Path $Game 'binaries') -WindowStyle Normal -PassThru
        $process.Id | Set-Content -LiteralPath (Join-Path $userDir '../owned-pid.txt')
        Write-Output "Fresh Florence test process: $($process.Id)"
    }
    Write-Output "Disposable test user directory: $userDir"
} finally { Pop-Location }
