param([string]$Destination, [string]$ReleaseVersion)
$ErrorActionPreference = 'Stop'
$source = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\mod\bfl'))
$metadata = Get-Content -LiteralPath (Join-Path $source '.metadata/metadata.json') -Raw | ConvertFrom-Json
if ($ReleaseVersion) {
    if ($ReleaseVersion -notmatch '^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?$') { throw 'Release version must be a semantic version or v-prefixed release tag.' }
    $metadata.version = $ReleaseVersion -replace '^v', ''
}
if (-not $Destination) { $Destination = Join-Path $PSScriptRoot "../dist/bfi-$($metadata.version)" }
$target = [IO.Path]::GetFullPath($Destination)
if ($target -eq $source -or $source.StartsWith($target + [IO.Path]::DirectorySeparatorChar)) { throw 'Destination cannot contain the source tree.' }
if (Test-Path -LiteralPath $target) { throw 'Choose an empty staging path; existing releases are never deleted or overwritten.' }
& python (Join-Path $PSScriptRoot 'validate_sources.py')
if ($LASTEXITCODE -ne 0) { throw 'Source validation failed.' }
New-Item -ItemType Directory -Path $target -Force | Out-Null
foreach ($entry in @('.metadata','in_game','main_menu','thumbnail.png')) {
    Copy-Item -LiteralPath (Join-Path $source $entry) -Destination $target -Recurse
}
$metadata | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $target '.metadata/metadata.json') -Encoding utf8
$manifest = Get-ChildItem -LiteralPath $target -Recurse -File -Force | ForEach-Object {
    [PSCustomObject]@{ path = [IO.Path]::GetRelativePath($target, $_.FullName).Replace('\','/'); sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant() }
}
$manifest | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath ($target + '.manifest.json') -Encoding utf8
Compress-Archive -LiteralPath $target -DestinationPath ($target + '.zip')
Write-Output "Staged $target with $($manifest.Count) files. No probes, source assets or tools are packaged."
