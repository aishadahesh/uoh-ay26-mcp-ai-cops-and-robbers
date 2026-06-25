$ErrorActionPreference = "Stop"
$env:PYTHONPATH = Join-Path $PSScriptRoot "..\src"
$env:MCP_TRANSPORT = "sse"
$env:MCP_HOST = if ($env:MCP_HOST) { $env:MCP_HOST } else { "0.0.0.0" }
$env:MCP_PORT = if ($env:MCP_PORT) { $env:MCP_PORT } else { "8001" }
$env:MCP_PUBLIC_URL = if ($env:MCP_PUBLIC_URL) {
    $env:MCP_PUBLIC_URL
} else {
    "http://127.0.0.1:$($env:MCP_PORT)"
}

$Python = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $Python) {
    $Python = (Get-Command py -ErrorAction SilentlyContinue)
}
if (-not $Python) {
    throw "Python was not found. Install Python 3.11+ or activate your virtual environment."
}

& $Python.Source -m cops_robbers_ai.cop_server
