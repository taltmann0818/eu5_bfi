param(
    [string]$Game = $env:EU5_GAME_ROOT,
    [string]$Cmf = $env:EU5_CMF_ROOT,
    [string]$Output = 'tests/results/local',
    [int]$TimeoutSeconds = 1200,
    [switch]$Graphics,
    [ValidateSet('accounts', 'm0', 'm1', 'm2', 'm3', 'm4', 'm5', 'm5market', 'm5pricing', 'm6', 'm6traditions', 'm6discovery', 'm6absolutism', 'm6policy', 'm7', 'm7traditions', 'm7later', 'm7company', 'm7authority', 'm8', 'm8traditions', 'm8renaissance', 'm8absolutism', 'm9')][string]$Suite = 'accounts'
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
if (-not $Game) { $Game = 'C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V' }
if (-not $Cmf) { $Cmf = 'C:\Program Files (x86)\Steam\steamapps\workshop\content\3450310\3692202776' }
$exe = Join-Path $Game 'binaries/eu5.exe'
if (-not (Test-Path -LiteralPath $exe)) { throw "Licensed EUV installation missing: $exe" }
if (-not (Test-Path -LiteralPath (Join-Path $Cmf '.metadata/metadata.json'))) { throw 'CMF installation missing' }
if ($TimeoutSeconds -lt 30 -or $TimeoutSeconds -gt 7200) { throw 'Timeout must be 30–7200 seconds' }
Push-Location -LiteralPath $repo
try {
    python tools/audit_native.py --game (Join-Path $Game 'game') --cmf $Cmf --compare
    if ($LASTEXITCODE -ne 0) { throw 'Native/CMF version pin changed; review before running.' }
    $runId = [guid]::NewGuid().ToString('N')
    $runRoot = Join-Path $repo "dist/campaign-$runId"
    $userDir = Join-Path $runRoot 'user'
    New-Item -ItemType Directory -Path $userDir -Force | Out-Null
    $suiteScript = switch ($Suite) {
        'm0' { 'tools/m0_probe_suite.py' }
        'm1' { 'tools/m1_charter_suite.py' }
        'm2' { 'tools/m2_company_suite.py' }
        'm3' { 'tools/m3_credit_suite.py' }
        'm4' { 'tools/m4_treasury_suite.py' }
        'm5' { 'tools/m5_ownership_suite.py' }
        'm5market' { 'tools/m5_market_suite.py' }
        'm5pricing' { 'tools/m5_pricing_suite.py' }
        'm6' { 'tools/m6_goods_suite.py' }
        'm6policy' { 'tools/m6_policy_suite.py' }
        'm6traditions' { 'tools/m6_traditions_suite.py' }
        'm6discovery' { 'tools/m6_discovery_suite.py' }
        'm6absolutism' { 'tools/m6_absolutism_suite.py' }
        'm7' { 'tools/m7_commenda_suite.py' }
        'm7traditions' { 'tools/m7_traditions_suite.py' }
        'm7later' { 'tools/m7_later_suite.py' }
        'm7company' { 'tools/m7_company_suite.py' }
        'm7authority' { 'tools/m7_authority_suite.py' }
        'm9' { 'tools/m9_resolution_suite.py' }
        'm8' { 'tools/m8_monetary_suite.py' }
        'm8traditions' { 'tools/m8_traditions_suite.py' }
        'm8renaissance' { 'tools/m8_renaissance_suite.py' }
        'm8absolutism' { 'tools/m8_absolutism_suite.py' }
        default { 'tools/campaign_suite.py' }
    }
    python $suiteScript prepare --userdir $userDir --token $runId
    if ($LASTEXITCODE -ne 0) { throw 'Fixture preparation failed' }
    $bfi = Join-Path $userDir 'mod/bfi'
    Copy-Item -LiteralPath (Join-Path $repo 'mod/bfl') -Destination $bfi -Recurse
    $overlay = Join-Path $userDir 'mod/bfi_campaign_checks'
    $mods = @($Cmf, $bfi, $overlay) | ForEach-Object {
        @{path = ($_.Replace('\','/') + '/'); isEnabled = $true}
    }
    @{file_version = '1.0.0'; playsets = @(@{
        name = 'BFI_CI_DISPOSABLE'; isActive = $true; isAutomaticallySorted = $false;
        orderedListMods = $mods; DLC = @()
    })} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $userDir 'playsets.json') -Encoding utf8
    $arguments = @('-debug_mode', '-play=FLO', '-handsoff', '-timed_handsoff=15', "-userdir=`"$userDir`"")
    if ($Suite -eq 'm2') { $arguments = @('-debug_mode', '-play=FLO', '-handsoff', '-timed_handsoff=122', "-userdir=`"$userDir`"") }
    if ($Suite -eq 'm8') { $arguments = @('-debug_mode', '-play=FLO', '-handsoff', '-timed_handsoff=30', "-userdir=`"$userDir`"") }
    if ($Suite -eq 'm7company') { $arguments = @('-debug_mode', '-play=FLO', '-handsoff', '-timed_handsoff=240', "-userdir=`"$userDir`"") }
    # Activity assertions finish after three months, followed by a full annual
    # autosave interval. Native timed handsoff counts months, not years.
    if ($Suite -in @('m7', 'm7traditions', 'm7later')) { $arguments = @('-debug_mode', '-play=FLO', '-handsoff', '-timed_handsoff=30', "-userdir=`"$userDir`"") }
    if ($Suite -eq 'm5market') { $arguments = @('-debug_mode', '-play=FLO', '-handsoff', '-timed_handsoff=30', "-userdir=`"$userDir`"") }
    if ($Suite -eq 'm5pricing') { $arguments = @('-debug_mode', '-play=FLO', '-handsoff', '-timed_handsoff=90', "-userdir=`"$userDir`"") }
    if (-not $Graphics) { $arguments += '-nographics' }
    $outPath = [System.IO.Path]::GetFullPath((Join-Path $repo $Output))
    New-Item -ItemType Directory -Path $outPath -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $userDir 'bfi_campaign_manifest.json') -Destination (Join-Path $outPath 'manifest.json') -Force
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    $debugPath = Join-Path $userDir 'logs/debug.log'
    function Invoke-BfiEngine([string[]]$LaunchArguments, [string]$StopMarker) {
        # Preserve old logs before launch so a retry cannot see a prior completion marker.
        foreach ($oldLog in (Get-ChildItem -LiteralPath (Join-Path $userDir 'logs') -File -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -match '^(debug|error)(\.\d+)?\.log$' })) {
            Move-Item -LiteralPath $oldLog.FullName -Destination (Join-Path $runRoot ("previous-$([guid]::NewGuid().ToString('N'))-$($oldLog.Name)"))
        }
        $proc = Start-Process -FilePath $exe -ArgumentList $LaunchArguments -WorkingDirectory (Join-Path $Game 'binaries') -WindowStyle Hidden -PassThru
        Write-Output "EUV campaign process $($proc.Id); isolated user directory: $userDir"
        try {
            while (-not $proc.HasExited -and [DateTime]::UtcNow -lt $deadline) {
                if (Test-Path -LiteralPath $debugPath) {
                    # An autosave can append hundreds of lines between polls;
                    # the completed fixture marker must not fall out of a tail.
                    if (Select-String -LiteralPath $debugPath -Pattern $StopMarker -SimpleMatch -Quiet -ErrorAction SilentlyContinue) { break }
                }
                Start-Sleep -Seconds 5
                $proc.Refresh()
            }
        } finally {
            # Only terminate the exact process created here. Never stop a player's EUV process.
            $proc.Refresh()
            if (-not $proc.HasExited) {
                try { $proc.Kill() }
                catch {
                    # Native timed handsoff can exit between Refresh and Kill.
                    # Ignore only a confirmed exit of this exact owned process.
                    $proc.Refresh()
                    if (-not $proc.HasExited) { throw }
                }
                $proc.WaitForExit()
            }
        }
    }
    $runtimeFingerprint=(Get-Content -LiteralPath (Join-Path $userDir 'bfi_campaign_manifest.json') -Raw | ConvertFrom-Json).runtime_sha256
    Invoke-BfiEngine $arguments "BFI_TEST|$runId|END|$runtimeFingerprint"
    if (-not (Test-Path -LiteralPath $debugPath)) { throw 'EUV did not create isolated logs; campaign did not run.' }
    $priorLog = Join-Path $runRoot 'campaign-debug.log'
    $priorErrors = Join-Path $runRoot 'campaign-errors.log'
    Copy-Item -LiteralPath $debugPath -Destination $priorLog
    python -c "import sys;sys.path.insert(0,'tools');from pathlib import Path;from campaign_suite import engine_errors;Path(sys.argv[2]).write_text(engine_errors(sys.argv[1]),encoding='utf-8')" (Join-Path $userDir 'logs') $priorErrors
    if ($LASTEXITCODE -ne 0) { throw 'Could not preserve engine diagnostics' }
    $save = Get-ChildItem -LiteralPath (Join-Path $userDir 'save games') -Filter '*.eu5' -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $save) { throw 'Campaign produced no autosave for the persistence checks.' }
    python $suiteScript prepare-reload --userdir $userDir
    if ($LASTEXITCODE -ne 0) { throw 'Reload fixture preparation failed' }
    # EUV resolves this option under the isolated 'save games' directory and appends .eu5.
    $reloadArgs = @('-debug_mode', "-loadsavehandsoff=$($save.BaseName)", '-timed_handsoff=3', "-userdir=`"$userDir`"")
    if (-not $Graphics) { $reloadArgs += '-nographics' }
    Invoke-BfiEngine $reloadArgs "BFI_TEST|$runId|RELOAD_END|$runtimeFingerprint"
    python $suiteScript report --userdir $userDir --output $outPath --prior-log $priorLog --prior-errors $priorErrors
    if ($LASTEXITCODE -ne 0) { throw 'Campaign assertions failed or execution was incomplete; see campaign.json.' }
    Write-Output "PASS: real Florence campaign; report $outPath"
} finally { Pop-Location }
