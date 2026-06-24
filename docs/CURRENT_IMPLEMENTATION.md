# Current Implementation Snapshot

This document describes the current non-bonus ShadowGrid implementation as verified on
2026-06-24.

## Executive Summary

ShadowGrid is now a working local assignment submission package. It includes the core game engine,
two agent roles, natural-language message passing, partial observability, separate MCP server entry
points, Gemini/OpenAI provider support, deterministic fallback agents, a playable GUI, video replay
export, movement JSON export, and the required six-sub-game InternalGameJSON report.

The implementation is designed to be demonstrable even without API keys. When API keys are absent
or a provider call fails, the deterministic strategy keeps the game moving and preserves the
assignment pipeline.

## Verified Build State

Commands verified from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check src tests
.\.venv\Scripts\python.exe -m cops_robbers_ai.cli --print-report
```

Verification result:

| Check | Result |
| --- | --- |
| Unit tests | 8 passed |
| Ruff lint | All checks passed |
| CLI report generation | Completed |
| Generated sub-games | 6 |
| Invalid `stay` actions in report | 0 |
| Robber barrier actions in report | 0 |
| Max observed sub-game length | 8 turns in the latest CLI run |

## Implemented Flow

1. `config.json` loads the board, scoring, visibility, provider, and reporting settings.
2. `LocalOrchestrator` starts six sub-games.
3. Each sub-game alternates robber then cop.
4. Each role receives a partial observation from `GameState.visible_to`.
5. The agent chooses a move and sends a natural-language message.
6. `action_policy.sanitize_action` rejects invalid final actions.
7. `GameEngine` applies the action, checks capture, and scores the result.
8. `reporting.py` writes `reports/internal_game_report.json`.
9. If Gmail is enabled, the same JSON object can be sent as the email body.

## Agent Behavior

The agents are intentionally orchestration-focused rather than optimized game solvers. They:

- parse soft location hints from messages such as `I am at (x,y)`;
- reason from visible opponent state when the opponent is inside the visibility radius;
- move toward the robber as cop;
- move away from the cop as robber;
- use deterministic fallback behavior when no provider key is available;
- never record `stay` as a final legal move.

## GUI And Evidence

The GUI is the demonstration surface. It includes:

- centered Tkinter window;
- colorful ShadowGrid visual identity;
- four play modes;
- mouse click movement on highlighted legal cells;
- keyboard movement;
- cop barrier placement;
- animated game-start curtain;
- winner overlay;
- timestamped `Save Game`;
- matching MP4 and movement JSON exports.

Each saved GUI replay can be paired with its `*_movements.json` file in `reports/`.

## MCP Scope

The project includes separate MCP server modules:

- `cops_robbers_ai.cop_server`
- `cops_robbers_ai.thief_server`

They expose shared FastMCP tools for reset, message receiving, and action choice. The current
submission is local-first, matching the non-bonus stage. Public deployment URLs and token
authentication remain a later deployment task.

## Deferred Items

- Public cloud MCP deployment.
- Token-authenticated public endpoints.
- Automatic Gmail sending with real OAuth credentials.
- Bonus inter-group competition.
- Q-learning or other advanced learned policy.

These are intentionally documented as future work so the local non-bonus implementation remains
stable, reproducible, and easy to evaluate.
