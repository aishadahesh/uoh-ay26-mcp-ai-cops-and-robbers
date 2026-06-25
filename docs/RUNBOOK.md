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

Do not commit `.env`. The project is designed to run without API keys, so missing keys are not a
setup failure; they simply activate deterministic fallback agents.

## Local Game Series

```powershell
.\scripts\run_local.ps1
```

This writes `reports/internal_game_report.json`.

If no API key is configured, the agents use the deterministic fallback policy.

The current verified report contains 6 sub-games and no final `stay` moves. Re-running this command
updates the report with a fresh timestamp.

Latest verified local run:

```text
generated_at: 2026-06-26T01:46:06.327007+03:00
totals: cop=120, thief=30
```

## Bonus Series

```powershell
python -m cops_robbers_ai.cli --config config.json --bonus-config bonus_config.json --print-report
```

This runs the six-game inter-group bonus series and writes `reports/bonus_game_report.json`.
With the current Gmail OAuth tokens in place, the same command sends the updated JSON attachment
from both group accounts.

Before running the bonus series, confirm these local-only files exist:

```text
bonus_config.json
credentials.json
token_group_1_aisha.json
token_group_2_yanal.json
```

Only `bonus_config.example.json` should be committed. The real `bonus_config.json` contains partner
URLs and tokens and is intentionally ignored.

Latest verified bonus run:

```text
generated_at: 2026-06-26T01:38:11.804738+03:00
score: uoh-ay26=85, yanell11=45
win count: uoh-ay26=5, yanell11=1
bonus claim: uoh-ay26=10, yanell11=7
```

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

The local orchestrator uses the same agent interface in-process for repeatable tests. The bonus
orchestrator connects to the deployed MCP URLs in `bonus_config.json`.

For local HTTP testing, set:

```powershell
$env:MCP_TRANSPORT="streamable-http"
$env:MCP_HOST="127.0.0.1"
$env:MCP_PORT="8001"
$env:MCP_AUTH_TOKEN="local-test-token"
python -m cops_robbers_ai.cop_server
```

Use a different port for the thief server. In cloud mode, use HTTPS URLs and keep the bearer token
private.

## Gmail Report

Set `email.enabled` to `true` in `config.json`, place Google OAuth `credentials.json` in the repo
root, and run the local series. The email body is exactly the JSON report, as required.

For the bonus flow, email is configured in `bonus_config.json`. It attaches only
`bonus_game_report.json` and sends one email from `aishadahesh11@gmail.com` and one from
`yanalserhan3@gmail.com`.

If Gmail OAuth blocks the app, add both sender accounts as test users in the Google Cloud OAuth
consent screen. The generated token files are sensitive and ignored by Git.

## Final Verification Checklist

Run these before submission:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check src tests
git status --short --ignored
```

Expected result:

- tests pass;
- Ruff reports no issues;
- `.env`, OAuth tokens, `bonus_config.json`, and `ngrok.yml` appear only as ignored files;
- `README.md`, `reports/README.md`, and the two JSON reports are committed.
