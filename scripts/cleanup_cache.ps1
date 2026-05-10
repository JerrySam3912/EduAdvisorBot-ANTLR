$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$targets = @(
    Join-Path $Root '.pytest_cache',
    Join-Path $Root 'apps\backend-api\.pytest_cache'
)

foreach ($target in $targets) {
    if (Test-Path $target) {
        Remove-Item $target -Recurse -Force
        Write-Host "Removed $target"
    }
}
