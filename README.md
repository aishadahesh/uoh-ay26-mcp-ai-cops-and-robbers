# ShadowGrid: Agent Chase Protocol

ShadowGrid is a multi-agent cops-and-robber orchestration project built for the University of Haifa
AI Agents Orchestration assignment. It demonstrates two independent roles, a cop and a robber,
operating in a partially observable grid world. Agents communicate through natural-language
messages, infer opponent state from limited observations, translate decisions into physical moves,
and produce the required InternalGameJSON report.

The current implementation is a complete non-bonus local submission package: playable GUI, saved
game replay export, movement JSON export, MCP server entry points, Gemini/OpenAI API support,
deterministic fallback agents, legality guards for AI actions, verified tests, lint-clean source
code, and professional submission documentation.

## Project Goals

- Demonstrate agent orchestration, not only game strategy.
- Separate game rules, agent reasoning, MCP tool exposure, reporting, GUI, and replay export.
- Support local execution without API keys, while allowing Gemini/OpenAI-backed agents when keys
  exist.
- Produce concrete evidence artifacts: JSON report, saved game video, and movement log.
- Match the assignment's non-bonus requirements and leave advanced bonus/cloud deployment as future
  work.

## Main Features

- Configurable grid, defaulting to 5x5.
- Six-sub-game CLI series with assignment scoring.
- Robber moves first, then cop.
- Eight-direction movement. `stay` is intentionally rejected by the action legality policy.
- Cop barrier placement, up to five barriers per sub-game.
- Partial observation through configurable visibility radius.
- Natural-language messages between agents.
- Shared action validation for CLI, MCP, and GUI execution paths.
- Separate MCP server modules for cop and robber.
- Gemini and OpenAI provider support with deterministic fallback.
- Centered GUI with four play modes:
  - Cop agent, robber user
  - Cop user, robber agent
  - Cop user, robber user
  - Cop OpenAI, robber Gemini
- Click-to-move on highlighted legal squares.
- Start curtain showing game start and player matchup.
- End overlay showing the winner.
- Timestamped `Save Game` export after game completion.

## Quick Start

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev,email]"
```

On systems where `python` is not available but the Windows launcher is installed:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev,email]"
```

Optional API keys:

```powershell
Copy-Item .env.example .env
notepad .env
```

`.env` format:

```env
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
```

If API keys are missing, the project uses deterministic fallback agents so the game still runs.

## Running The CLI Series

```powershell
.\scripts\run_local.ps1
```

This runs the full six-sub-game local series and writes:

```text
reports/internal_game_report.json
```

The report contains group metadata, students, GitHub URL, MCP URLs, timezone, all sub-games, move
traces, scores, and totals.

## Running The GUI

```powershell
.\scripts\run_gui.ps1
```

GUI controls:

- Click highlighted green squares to move.
- Use `QWE / AD / ZXC` for keyboard movement.
- Use `B` or right-click for cop barrier placement.
- Click `New Game` to restart.
- Click `Save Game` after the game ends.

## Results And Evidence

The project produces concrete evidence artifacts in `reports/`. These are intentionally kept as
submission material: the evaluator can inspect the six-sub-game JSON, watch saved GUI replays, and
cross-check each replay against its movement log.

| Artifact | Path | Description |
| --- | --- | --- |
| Internal game report | [`reports/internal_game_report.json`](reports/internal_game_report.json) | Required assignment JSON for the six-sub-game series |
| Reports index | [`reports/README.md`](reports/README.md) | Human-readable catalog of saved reports, videos, and movement logs |
| Current implementation audit | [`docs/CURRENT_IMPLEMENTATION.md`](docs/CURRENT_IMPLEMENTATION.md) | Snapshot of what is implemented, verified, and still deferred |
| Assignment compliance review | [`docs/ASSIGNMENT_REVIEW.md`](docs/ASSIGNMENT_REVIEW.md) | Mapping from reference PDF requirements to implementation status |

Current CLI result:

| Metric | Value |
| --- | --- |
| Generated at | `2026-06-24T13:10:37.050200+03:00` |
| Sub-games | `6` |
| Results | `6 cop wins, 0 robber wins` |
| Totals | `cop=120`, `thief=30` |
| Validation | no `stay` moves, no robber barriers, no sub-game above 25 move pairs |

Saved GUI replay evidence:

| Video | Movement JSON | Mode | Result | Moves |
| --- | --- | --- | --- | --- |
| [`shadowgrid_replay_20260622_230818.mp4`](reports/shadowgrid_replay_20260622_230818.mp4) | [`shadowgrid_replay_20260622_230818_movements.json`](reports/shadowgrid_replay_20260622_230818_movements.json) | Cop agent, robber user | Cop wins | 6 |
| [`shadowgrid_replay_20260622_230957.mp4`](reports/shadowgrid_replay_20260622_230957.mp4) | [`shadowgrid_replay_20260622_230957_movements.json`](reports/shadowgrid_replay_20260622_230957_movements.json) | Cop OpenAI, robber Gemini | Robber wins | 50 |
| [`shadowgrid_replay_20260622_231534.mp4`](reports/shadowgrid_replay_20260622_231534.mp4) | [`shadowgrid_replay_20260622_231534_movements.json`](reports/shadowgrid_replay_20260622_231534_movements.json) | Cop OpenAI, robber Gemini | Cop wins | 6 |
| [`shadowgrid_replay_20260622_231701.mp4`](reports/shadowgrid_replay_20260622_231701.mp4) | [`shadowgrid_replay_20260622_231701_movements.json`](reports/shadowgrid_replay_20260622_231701_movements.json) | Cop agent, robber user | Robber wins | 50 |
| [`shadowgrid_replay_20260624_134355.mp4`](reports/shadowgrid_replay_20260624_134355.mp4) | [`shadowgrid_replay_20260624_134355_movements.json`](reports/shadowgrid_replay_20260624_134355_movements.json) | Cop OpenAI, robber Gemini | Cop wins | 6 |
| [`shadowgrid_replay_20260624_134450.mp4`](reports/shadowgrid_replay_20260624_134450.mp4) | [`shadowgrid_replay_20260624_134450_movements.json`](reports/shadowgrid_replay_20260624_134450_movements.json) | Cop agent, robber user | Cop wins | 14 |
| [`shadowgrid_replay_20260624_134504.mp4`](reports/shadowgrid_replay_20260624_134504.mp4) | [`shadowgrid_replay_20260624_134504_movements.json`](reports/shadowgrid_replay_20260624_134504_movements.json) | Cop user, robber agent | Cop wins | 6 |

The saved replay includes the start presentation, player matchup, board states, and final winner
frame. The movement JSON allows the replay to be audited programmatically.

## Architecture

ShadowGrid is split into focused modules:

- `engine.py`: grid rules, movement, barriers, capture, scoring.
- `models.py`: shared domain types such as `Position`, `Move`, `Action`, and `GameState`.
- `action_policy.py`: legality guard that converts invalid agent choices into valid movement.
- `strategy.py`: deterministic fallback agent behavior and natural-language hint parsing.
- `llm_agent.py`: Gemini/OpenAI provider calls with fallback behavior.
- `orchestrator.py`: local six-sub-game series runner.
- `mcp_common.py`: shared FastMCP tool server construction.
- `cop_server.py` and `thief_server.py`: separate MCP server entry points.
- `reporting.py`: InternalGameJSON creation and report writing.
- `gmail_client.py`: optional Gmail JSON sender.
- `gui.py`: playable GUI and replay capture.
- `video_export.py`: MP4/GIF replay rendering.

## Formal Model

The game is modeled as a Dec-POMDP:

```text
<n, S, {A_i}, P, R, {Omega_i}, O, gamma>
```

- `n`: two agents, cop and robber.
- `S`: full board state: cop position, robber position, barriers, remaining barriers, and turn
  index.
- `{A_i}`: eight movement actions for both roles; barrier action for the cop. `stay` exists only as
  a defensive internal value and is sanitized away before valid turns are recorded.
- `P`: deterministic transition function constrained by grid bounds and barriers.
- `R`: assignment scoring table.
- `{Omega_i}`: partial observations available to each role.
- `O`: observation function implemented by `GameState.visible_to`.
- `gamma`: reserved for future reinforcement-learning extensions.

## MCP Design

The project follows the assignment distinction between MCP server and MCP client:

- MCP servers expose tools.
- The orchestrator/client manages the dialogue, LLM calls, and turn sequence.
- LLMs are not embedded as long-running server state.

Available MCP tools:

- `reset_game`
- `receive_message`
- `choose_action`

Run the servers in separate terminals:

```powershell
$env:PYTHONPATH="src"; python -m cops_robbers_ai.cop_server
```

```powershell
$env:PYTHONPATH="src"; python -m cops_robbers_ai.thief_server
```

## Tools And Technologies Used

- Python 3.11+
- FastMCP / MCP Python package
- Tkinter for GUI
- Gemini API through `google-genai`
- OpenAI API through `openai`
- Pillow and ImageIO for replay rendering
- Google API client libraries for optional Gmail delivery
- Pytest for tests
- Ruff for linting
- JSON configuration and `.env` secret management

## Challenges And Decisions

**Partial observability:** Agents cannot always see the opponent. The project handles this through a
visibility radius and natural-language hints.

**Provider reliability:** API keys, quotas, and network availability can fail. The system therefore
includes deterministic fallback agents.

**Action legality:** LLMs can ask for impossible moves. The shared action policy makes sure reports
contain valid assignment actions.

**MCP/client separation:** The assignment requires MCP servers to expose tools while the
client/orchestrator owns reasoning. The code keeps this separation.

**GUI replay evidence:** A normal GUI is hard to submit as evidence. The replay exporter creates a
video/GIF and a movement JSON log.

**Windows timezone support:** `Asia/Jerusalem` requires `tzdata` in some Windows/Python
environments, so it is included as a dependency.

**Video encoding portability:** MP4 export may fail on some systems. The exporter falls back to GIF.

## Documentation Map

- `docs/CURRENT_IMPLEMENTATION.md`: verified implementation snapshot.
- `docs/PRD.md`: product requirements and acceptance criteria.
- `docs/PRD_GAME_ENGINE.md`: game-engine-specific requirements.
- `docs/PRD_AGENT_ORCHESTRATION.md`: agent/MCP/provider requirements.
- `docs/PRD_GUI_REPLAY.md`: GUI and replay-export requirements.
- `docs/PLAN.md`: staged implementation plan.
- `docs/REQUIREMENTS.md`: assignment and runtime requirements.
- `docs/ARCHITECTURE.md`: system architecture and Dec-POMDP explanation.
- `docs/RUNBOOK.md`: setup, running, MCP, GUI, and Gmail instructions.
- `docs/ASSIGNMENT_REVIEW.md`: reference-PDF compliance review.
- `docs/PROMPT_LOG.md`: AI-assisted development prompt log.
- `docs/TODO.md`: 900-item professional backlog.
- `reports/README.md`: generated evidence index.

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check src tests
```

Verified checks:

- Capture behavior.
- Barrier blocking.
- Report shape.
- Agent action sanitization.
- No-stay fallback behavior.
- GUI and video exporter imports.
- Ruff linting across `src` and `tests`.

## Gmail Report Delivery

Gmail sending is disabled by default. To enable:

1. Follow `ref/main-google-api-installtion-guid.pdf`.
2. Place `credentials.json` in the repository root.
3. Set `email.enabled` to `true` in `config.json`.
4. Run the local series.

The email body is JSON only, matching the assignment's automated-processing requirement.
