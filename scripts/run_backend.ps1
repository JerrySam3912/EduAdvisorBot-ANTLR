$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root 'apps\backend-api'

Push-Location $Backend
try {
    uvicorn app.main:app --reload --port 8000
}
finally {
    Pop-Location
}
