$ErrorActionPreference = "Stop"

$ConfigPath = if ($env:NGROK_CONFIG) {
    $env:NGROK_CONFIG
} else {
    Join-Path $PSScriptRoot "..\ngrok.yml"
}

$Ngrok = Get-Command ngrok -ErrorAction SilentlyContinue
if (-not $Ngrok) {
    throw "ngrok was not found. Install it from https://ngrok.com/download and run ngrok config add-authtoken first."
}

if (-not (Test-Path $ConfigPath)) {
    throw "Missing ngrok config at $ConfigPath. Copy ngrok.example.yml to ngrok.yml and set your authtoken."
}

& $Ngrok.Source start --config $ConfigPath cop-mcp thief-mcp
