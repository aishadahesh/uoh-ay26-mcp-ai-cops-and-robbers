# Requirements Specification

## Assignment Requirements Mapping

| Requirement | Implementation | Status |
| --- | --- | --- |
| 5x5 configurable grid | `config.json`, `GameConfig.grid_size` | Done |
| Six sub-games | `config.json`, `LocalOrchestrator.run_series` | Done |
| 25 moves max | `config.json`, `GameEngine.result_for` | Done |
| Cop and robber agents | `AgentBrain`, `GeminiAgent`, MCP entry points | Done |
| Separate MCP servers | `cop_server.py`, `thief_server.py` | Done locally |
| Natural-language communication | agent messages and parser | Done |
| Partial observation | `GameState.visible_to` | Done |
| Barriers | `GameEngine._place_barrier` | Done |
| No legal stay action | `action_policy.sanitize_action`, GUI legal moves | Done |
| InternalGameJSON | `reporting.py` | Done |
| Gmail JSON body only | `gmail_client.py`, disabled by default | Ready |
| GUI evidence | `gui.py` | Done |
| Config file | `config.json` | Done |
| `.env-example` | `.env.example` | Done |
| Secrets excluded | `.gitignore` | Done |
| Professional docs | `docs/` | In progress |
| Bonus inter-group play | Out of current scope | Deferred |

## Runtime Requirements

- Windows PowerShell or equivalent terminal.
- Python virtual environment under `.venv`.
- `pip install -e ".[dev,email]"`.
- Optional `GEMINI_API_KEY` and `OPENAI_API_KEY` in `.env`.

## GUI Requirements

- The GUI shall start centered.
- The GUI shall show game mode, current player, legal moves, move log, and controls.
- The GUI shall show a start presentation when a new game begins.
- The GUI shall show an end presentation naming the winner.
- The GUI shall record replay frames and export only completed games.

## Reporting Requirements

- CLI report path: `reports/internal_game_report.json`.
- GUI replay path: timestamped `reports/shadowgrid_replay_<timestamp>.mp4` or `.gif`.
- GUI movement path: matching `reports/shadowgrid_replay_<timestamp>_movements.json`.
- Reports index path: `reports/README.md`.
- Email body, when enabled, must be JSON only.

## Configuration Requirements

- No API keys in source code.
- API keys only in `.env`.
- Rule settings only in `config.json`.
- Report URLs are editable placeholders until deployment.
