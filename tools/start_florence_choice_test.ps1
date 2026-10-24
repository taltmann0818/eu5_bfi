param([switch]$PrepareOnly)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$game = 'C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V'
$cmf = 'C:\Program Files (x86)\Steam\steamapps\workshop\content\3450310\3692202776'
Push-Location -LiteralPath $repo
try {
    python tools/audit_native.py --compare
    if ($LASTEXITCODE -ne 0) { throw 'Native compatibility audit failed.' }
    $runRoot = Join-Path $repo ('dist/florence-choice-' + [guid]::NewGuid().ToString('N'))
    $userDir = Join-Path $runRoot 'user'
    New-Item -ItemType Directory -Path (Join-Path $userDir 'mod') -Force | Out-Null
    $bfi = Join-Path $userDir 'mod/bfi'
    Copy-Item -LiteralPath (Join-Path $repo 'mod/bfl') -Destination $bfi -Recurse
    $token = [guid]::NewGuid().ToString('N')
    $utf8Bom = New-Object System.Text.UTF8Encoding($true)
    $setup = @"
bfi_florence_choice_setup = {
    if = { limit = { c:FLO = { is_ai = no NOT = { has_variable = bfi_florence_choice_opened } } }
        c:FLO = {
            set_variable = bfi_florence_choice_opened
            set_gold = 10000
        }
        location:florence = {
            if = { limit = { NOT = { any_buildings_in_location = { building_type = building_type:banking_office building_level > 0 owner = c:BRD } } }
                change_building_level_in_location = { building = building_type:banking_office value = 1 owner = c:BRD } }
            if = { limit = { NOT = { any_buildings_in_location = { building_type = building_type:banking_office building_level > 0 owner = c:PRZ } } }
                change_building_level_in_location = { building = building_type:banking_office value = 1 owner = c:PRZ } }
        }
        c:FLO = { trigger_event_non_silently = bfl_flavor_flo.1 }
        debug_log = "BFI_FLO_CHOICE_OPEN|$token"
    }
}
"@
    [IO.File]::WriteAllText((Join-Path $bfi 'in_game/common/scripted_effects/bfi_florence_choice_setup.txt'), $setup, $utf8Bom)
    $eventBackup = Join-Path $runRoot 'production-events'
    python tools/prepare_florence_catalogue.py --mod $bfi --backup $eventBackup --token $token
    if ($LASTEXITCODE -ne 0) { throw 'Historical catalogue staging failed.' }
    $hook = 'on_game_started_after_lobby = { on_actions = { bfi_florence_choice_start } } bfi_florence_choice_start = { effect = { bfi_florence_choice_setup = yes } }'
    [IO.File]::WriteAllText((Join-Path $bfi 'in_game/common/on_action/bfi_florence_choice_setup.txt'), $hook, $utf8Bom)
    $launchEvent = 'namespace = bfi_florence_launch bfi_florence_launch.1 = { type = country_event hidden = yes title = empty_text desc = empty_text outcome = neutral immediate = { bfi_florence_choice_setup = yes } }'
    [IO.File]::WriteAllText((Join-Path $bfi 'in_game/events/bfi_florence_launch.txt'), $launchEvent, $utf8Bom)
    $economyPath = Join-Path $bfi 'in_game/gui/economy_lateralview.gui'
    $economyBackup = Join-Path $runRoot 'economy-before-event.gui'
    Copy-Item -LiteralPath $economyPath -Destination $economyBackup
    $economy = [IO.File]::ReadAllText($economyPath)
    $anchor = 'widgetid = "economy_lateralview"'
    if (-not $economy.Contains($anchor)) { throw 'Native Economy launcher anchor changed.' }
    $timer = @'

    widget = {
        name = "bfi_florence_disposable_timer" visible = no
        state = { name = bfi_flo_start trigger_on_create = yes next = bfi_flo_fire }
        state = { name = bfi_flo_fire duration = 2 next = bfi_flo_fire
            on_finish = "[ExecuteConsoleCommand('event bfi_florence_launch.1')]" }
    }
'@
    [IO.File]::WriteAllText($economyPath, $economy.Replace($anchor, $anchor + $timer), $utf8Bom)
    $settings = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Paradox Interactive/Europa Universalis V/pdx_settings.json'
    if (Test-Path -LiteralPath $settings) { Copy-Item -LiteralPath $settings -Destination $userDir }
    $mods = @($cmf, $bfi) | ForEach-Object { @{path = ($_.Replace('\','/') + '/'); isEnabled = $true} }
    @{file_version = '1.0.0'; playsets = @(@{name = 'BFI_FLO_CHOICE_OF_BANKS'; isActive = $true; isAutomaticallySorted = $false; orderedListMods = $mods; DLC = @()})} |
        ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $userDir 'playsets.json') -Encoding utf8
    $manifest = @{run_root = $runRoot; userdir = $userDir; event_token = $token; state = 'Prepared fresh FLO with unanswered A Choice of Banks'; test_grants = '10000 state gold; Bardi, Peruzzi and Acciaioli Florence branches completed; 16 historical events resolved for their hosts outside date/institution windows. Berenberg and Saint George are Hamburg/Genoa state charters; Hamburger and the three other Genoese banks remain ordinary. Hamburg Central Bank is completed for catalogue inspection. Future ruler birth dates normalized only in this disposable scene.'}
    if (-not $PrepareOnly) {
        $process = Start-Process -FilePath (Join-Path $game 'binaries/eu5.exe') -ArgumentList @('-debug_mode', '-play=FLO', ('-userdir="' + $userDir + '"')) -WorkingDirectory (Join-Path $game 'binaries') -WindowStyle Normal -PassThru
        $manifest.process_id = $process.Id
    }
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $runRoot 'manifest.json') -Encoding utf8
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $repo 'dist/latest-florence-test.json') -Encoding utf8
    Write-Output ($manifest | ConvertTo-Json -Depth 5)
    if (-not $PrepareOnly) {
        $deadline = [DateTime]::UtcNow.AddMinutes(10)
        $debugPath = Join-Path $userDir 'logs/debug.log'
        while ([DateTime]::UtcNow -lt $deadline -and -not $process.HasExited) {
            if ((Test-Path -LiteralPath $debugPath) -and (Select-String -LiteralPath $debugPath -Pattern ('BFI_FLO_CHOICE_OPEN|' + $token) -SimpleMatch -Quiet -ErrorAction SilentlyContinue)) {
                Copy-Item -LiteralPath $economyBackup -Destination $economyPath -Force
                foreach ($originalEvent in (Get-ChildItem -LiteralPath $eventBackup -File -Recurse)) {
                    $relative = $originalEvent.FullName.Substring($eventBackup.Length + 1)
                    Copy-Item -LiteralPath $originalEvent.FullName -Destination (Join-Path $bfi $relative) -Force
                }
                $manifest.state = 'A Choice of Banks fired for human FLO; no option selected; temporary GUI timer removed'
                $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $runRoot 'manifest.json') -Encoding utf8
                $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $repo 'dist/latest-florence-test.json') -Encoding utf8
                Write-Output 'Florence event fired; all founding/cash options remain unanswered.'
                break
            }
            Start-Sleep -Seconds 2
            $process.Refresh()
        }
    }
} finally { Pop-Location }
