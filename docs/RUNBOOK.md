# Runbook

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev,email]"
```

For API-backed agents, copy the example environment file and add your keys:

```powershell
Copy-Item .env.example .env
notepad .env
```

## Local Game Series

```powershell
.\scripts\run_local.ps1
```

This writes `reports/internal_game_report.json`.

If no API key is configured, the agents use the deterministic fallback policy.

The current verified report contains 6 sub-games and no final `stay` moves. Re-running this command
updates the report with a fresh timestamp.

## Playable GUI

```powershell
.\scripts\run_gui.ps1
```

Choose one of four modes: cop agent vs robber user, cop user vs robber agent, two local users, or
OpenAI cop vs Gemini robber. The current human player can click highlighted cells to move. For the
dual-agent mode, add both `OPENAI_API_KEY` and `GEMINI_API_KEY` to `.env`; otherwise missing agents
fall back to the deterministic strategy.

Use `Save Game` after a game ends to export the replay under `reports/`. Each save uses a timestamped
filename, so previous games are not overwritten. The exported video stops on the final board. The
exporter tries MP4 first and falls back to GIF if the MP4 encoder is unavailable. The same action also
writes a matching `*_movements.json` file with every move, message, board state, final result, and
replay path.

See `reports/README.md` for the catalog of saved videos and movement JSON logs.

## MCP Servers

Open two terminals:

```powershell
$env:PYTHONPATH="src"; python -m cops_robbers_ai.cop_server
```

```powershell
$env:PYTHONPATH="src"; python -m cops_robbers_ai.thief_server
```

The local orchestrator uses the same agent interface in-process for repeatable tests. The server
modules are ready for the course MCP deployment step.

## Gmail Report

Set `email.enabled` to `true` in `config.json`, place Google OAuth `credentials.json` in the repo
root, and run the local series. The email body is exactly the JSON report, as required.
