param([string]$Destination = (Join-Path $PSScriptRoot '..\dist\bfl-0.0.1_DEV'))
$ErrorActionPreference = 'Stop'
$source = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\mod\bfl'))
$target = [IO.Path]::GetFullPath($Destination)
if ($target -eq $source -or $source.StartsWith($target + [IO.Path]::DirectorySeparatorChar)) { throw 'Destination cannot contain the source tree.' }
if (Test-Path -LiteralPath $target) { throw 'Choose an empty staging path; existing releases are never deleted or overwritten.' }
& python (Join-Path $PSScriptRoot 'validate_sources.py')
if ($LASTEXITCODE -ne 0) { throw 'Source validation failed.' }
New-Item -ItemType Directory -Path $target -Force | Out-Null
foreach ($entry in @('.metadata','in_game','main_menu','thumbnail.png')) {
    Copy-Item -LiteralPath (Join-Path $source $entry) -Destination $target -Recurse
}
$manifest = Get-ChildItem -LiteralPath $target -Recurse -File -Force | ForEach-Object {
    [PSCustomObject]@{ path = [IO.Path]::GetRelativePath($target, $_.FullName).Replace('\','/'); sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant() }
}
$manifest | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath ($target + '.manifest.json') -Encoding utf8
Compress-Archive -LiteralPath $target -DestinationPath ($target + '.zip')
Write-Output "Staged $target with $($manifest.Count) files. No probes, source assets or tools are packaged."
