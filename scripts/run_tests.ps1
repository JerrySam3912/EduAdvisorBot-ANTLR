$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root 'apps\backend-api'
$env:PYTHONPATH = $Backend

Push-Location $Backend
try {
    pytest 'tests/test_nlp_flow.py' -q
}
finally {
    Pop-Location
}
