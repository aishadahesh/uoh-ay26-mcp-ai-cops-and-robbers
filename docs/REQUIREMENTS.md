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
| Professional docs | `docs/` | Done |
| Bonus inter-group play | `BonusMcpOrchestrator`, `bonus_config.json` | Done |
| Bonus email confirmation | `bonus_config.json`, Gmail OAuth token files | Done |
| Scientific README model | Dec-POMDP tuple, strategy analysis, evidence map | Done |
| Self-scoring section | README `Self-Scoring` | Done |
| Python file size limit | all `.py` files are at or below 150 lines | Done |

## Runtime Requirements

- Windows PowerShell or equivalent terminal.
- Python virtual environment under `.venv`.
- `pip install -e ".[dev,email]"`.
- Optional `GEMINI_API_KEY` and `OPENAI_API_KEY` in `.env`.
- `pypdf` is included for local assignment PDF review and verification.

## Agent Requirements

- Agents must produce natural-language messages, not only machine commands.
- Agents must work under partial observability; they cannot assume the opponent is always visible.
- Agents may use LLM providers, but the game must remain runnable without API keys.
- Agent actions must be validated by shared code before becoming report evidence.
- The cop may place barriers; the thief may not place barriers.

The implementation satisfies these requirements with `GeminiAgent`, deterministic fallback
strategy, and `action_policy.sanitize_action`.

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
- Bonus report path: `reports/bonus_game_report.json`.
- Bonus email sends the final JSON report as the only attachment from both group Gmail accounts.

The reports are considered authoritative. Videos and screenshots are explanatory evidence, but the
grader can validate the game from JSON alone: every turn includes role, move, message, and state.

## Configuration Requirements

- No API keys in source code.
- API keys only in `.env`.
- Rule settings only in `config.json`.
- Bonus partner URLs and tokens live in `bonus_config.json`.
- `credentials.json` and Gmail OAuth token files are ignored by git.

## Security Requirements

- `.env` files must stay local.
- Gmail OAuth files must stay local.
- `bonus_config.json` must stay local because it can contain partner tokens.
- `ngrok.yml` must stay local because it can contain tunnel or domain settings.
- Example files must contain placeholders only.

These rules are enforced in `.gitignore`. The committed `bonus_config.example.json` documents the
shape without exposing private values.
