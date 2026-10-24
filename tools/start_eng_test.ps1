param([switch]$PrepareOnly)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$game = 'C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V'
$cmf = 'C:\Program Files (x86)\Steam\steamapps\workshop\content\3450310\3692202776'
Push-Location -LiteralPath $repo
try {
    python tools/audit_native.py --compare
    if ($LASTEXITCODE -ne 0) { throw 'Native compatibility audit failed.' }
    $runRoot = Join-Path $repo ('dist/eng-boe-' + [guid]::NewGuid().ToString('N'))
    $userDir = Join-Path $runRoot 'user'
    New-Item -ItemType Directory -Path (Join-Path $userDir 'mod') -Force | Out-Null
    $bfi = Join-Path $userDir 'mod/bfi'
    Copy-Item -LiteralPath (Join-Path $repo 'mod/bfl') -Destination $bfi -Recurse
    # -play can bypass the normal lobby startup callbacks. A temporary GUI
    # timer retries a guarded setup until ENG is the human player.
    # The country flag makes this safe across reloads and repeated UI creation.
    $eventToken = [guid]::NewGuid().ToString('N')
    New-Item -ItemType Directory -Path (Join-Path $userDir 'run') -Force | Out-Null
    $utf8Bom = New-Object System.Text.UTF8Encoding($true)
    $eventBackup = Join-Path $runRoot 'events-before-test'
    python tools/prepare_historical_test.py --mod $bfi --backup $eventBackup --script (Join-Path $userDir 'run/bfi_eng_event.txt') --token $eventToken
    if ($LASTEXITCODE -ne 0) { throw 'Historical test setup preparation failed.' }
    $eventScript = [IO.File]::ReadAllText((Join-Path $userDir 'run/bfi_eng_event.txt'))
    [IO.File]::WriteAllText((Join-Path $userDir 'bfi_eng_event.txt'), $eventScript, $utf8Bom)
    [IO.File]::WriteAllText((Join-Path $bfi 'in_game/common/scripted_effects/bfi_eng_campaign_setup.txt'), ('bfi_eng_campaign_setup = {' + $eventScript + '}'), $utf8Bom)
    $setupHook = 'on_game_started_after_lobby = { on_actions = { bfi_eng_campaign_start } } bfi_eng_campaign_start = { effect = { bfi_eng_campaign_setup = yes } }'
    [IO.File]::WriteAllText((Join-Path $bfi 'in_game/common/on_action/bfi_eng_campaign_setup.txt'), $setupHook, $utf8Bom)
    $setupEvent = 'namespace = bfi_campaign_launch bfi_campaign_launch.1 = { type = country_event hidden = yes title = empty_text desc = empty_text outcome = neutral immediate = { bfi_eng_campaign_setup = yes } }'
    [IO.File]::WriteAllText((Join-Path $bfi 'in_game/events/bfi_campaign_launch.txt'), $setupEvent, $utf8Bom)
    $economyPath = Join-Path $bfi 'in_game/gui/economy_lateralview.gui'
    $economyBackup = Join-Path $runRoot 'economy-before-event.gui'
    Copy-Item -LiteralPath $economyPath -Destination $economyBackup
    $economy = [IO.File]::ReadAllText($economyPath)
    $anchor = 'widgetid = "economy_lateralview"'
    if (-not $economy.Contains($anchor)) { throw 'Native Economy launcher anchor changed.' }
    $eventTimer = @'

    widget = {
        name = "bfi_eng_disposable_event_timer"
        visible = no
        state = { name = bfi_eng_timer_start trigger_on_create = yes next = bfi_eng_timer_fire }
        state = { name = bfi_eng_timer_fire duration = 2 next = bfi_eng_timer_fire
            on_finish = "[ExecuteConsoleCommand('event bfi_campaign_launch.1')]" }
    }
'@
    [IO.File]::WriteAllText($economyPath, $economy.Replace($anchor, $anchor + $eventTimer), $utf8Bom)
    $settings = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Paradox Interactive/Europa Universalis V/pdx_settings.json'
    if (Test-Path -LiteralPath $settings) { Copy-Item -LiteralPath $settings -Destination $userDir }
    $mods = @($cmf, $bfi) | ForEach-Object { @{path = ($_.Replace('\','/') + '/'); isEnabled = $true} }
    @{file_version = '1.0.0'; playsets = @(@{name = 'BFI_ENG_BANK_OF_ENGLAND'; isActive = $true; isAutomaticallySorted = $false; orderedListMods = $mods; DLC = @()})} |
        ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $userDir 'playsets.json') -Encoding utf8
    $manifest = @{run_root = $runRoot; userdir = $userDir; event_token = $eventToken; state = 'Prepared ENG; four native events resolve their founding options for historical owners'; test_grants = 'Founders topped up to 10000 gold; DHE date/trigger bypass in disposable profile; unique houses completed'}
    if (-not $PrepareOnly) {
        $arguments = @('-debug_mode', '-play=ENG', ('-userdir="' + $userDir + '"'))
        $process = Start-Process -FilePath (Join-Path $game 'binaries/eu5.exe') -ArgumentList $arguments -WorkingDirectory (Join-Path $game 'binaries') -WindowStyle Normal -PassThru
        $process.Id | Set-Content -LiteralPath (Join-Path $runRoot 'owned-pid.txt')
        $manifest.process_id = $process.Id
    }
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $runRoot 'manifest.json') -Encoding utf8
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $repo 'dist/latest-eng-test.json') -Encoding utf8
    Write-Output ($manifest | ConvertTo-Json -Depth 5)
    if (-not $PrepareOnly) {
        $deadline = [DateTime]::UtcNow.AddMinutes(10)
        $debugPath = Join-Path $userDir 'logs/debug.log'
        $eventSeen = $false
        while ([DateTime]::UtcNow -lt $deadline -and -not $process.HasExited) {
            if ((Test-Path -LiteralPath $debugPath) -and
                (Select-String -LiteralPath $debugPath -Pattern ('BFI_FOUR_BANKS_READY|' + $eventToken) -SimpleMatch -Quiet -ErrorAction SilentlyContinue)) {
                $eventSeen = $true
                break
            }
            Start-Sleep -Seconds 2
            $process.Refresh()
        }
        if ($eventSeen) {
            Copy-Item -LiteralPath $economyBackup -Destination $economyPath -Force
            foreach ($eventFile in Get-ChildItem -LiteralPath $eventBackup -Recurse -File) {
                $relative = [IO.Path]::GetRelativePath($eventBackup, $eventFile.FullName)
                Copy-Item -LiteralPath $eventFile.FullName -Destination (Join-Path $bfi $relative) -Force
            }
            $manifest.state = 'Four historical banks founded for ENG, HOL, SWE and the owner of Milan; event adapters and timer restored to production'
            $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $runRoot 'manifest.json') -Encoding utf8
            $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $repo 'dist/latest-eng-test.json') -Encoding utf8
            Write-Output 'All four historical banks founded; native production event definitions restored.'
        } else {
            Write-Warning 'Automatic event launch has not been confirmed. The game remains available for inspection.'
        }
    }
} finally { Pop-Location }
