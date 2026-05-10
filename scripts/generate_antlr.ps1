$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$Jar = Join-Path $Root 'tools\antlr\antlr4-4.9.2-complete.jar'
$Grammar = Join-Path $Root 'apps\backend-api\app\grammar\CourseQuery.g4'
$Output = Join-Path $Root 'apps\backend-api\app\generated'

if (-not (Test-Path $Jar)) {
    throw "ANTLR jar not found: $Jar"
}

if (-not (Test-Path $Grammar)) {
    throw "Grammar file not found: $Grammar"
}

if (-not (Test-Path $Output)) {
    New-Item -ItemType Directory -Path $Output | Out-Null
}

java -jar $Jar -Dlanguage=Python3 -visitor -o $Output $Grammar
