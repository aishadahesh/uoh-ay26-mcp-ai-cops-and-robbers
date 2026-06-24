$ErrorActionPreference = "Stop"
$env:PYTHONPATH = Join-Path $PSScriptRoot "..\src"
$Python = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $Python) {
    $Python = (Get-Command py -ErrorAction SilentlyContinue)
}
if (-not $Python) {
    throw "Python was not found. Install Python 3.11+ or activate your virtual environment."
}
& $Python.Source -m cops_robbers_ai.cli --print-report
