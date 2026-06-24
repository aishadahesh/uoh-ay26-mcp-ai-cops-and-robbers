# Architecture

This project implements the required non-bonus pipeline for the cops and robber assignment.

## Components

- `GameEngine` owns the grid, turns, movement, barriers, capture detection, and scoring.
- `action_policy.py` validates autonomous-agent actions before they enter CLI/MCP reports.
- `AgentBrain` represents a role-specific autonomous agent. It reads natural language messages,
  extracts soft position hints, and chooses a physical action.
- `LocalOrchestrator` acts as the MCP client/orchestrator. It runs six sub-games, alternates turns,
  passes messages between agents, and writes the InternalGameJSON report.
- `cop_server.py` and `thief_server.py` expose separate FastMCP tool servers for reset, message
  receive, and action choice.
- `gui.py` provides the playable visual demonstration, game-start curtain, winner overlay, replay
  capture, and timestamped save flow.
- `video_export.py` renders saved GUI frames into MP4, with GIF fallback when needed.

## Dec-POMDP Model

The game is modeled as `<n, S, {A_i}, P, R, {Omega_i}, O, gamma>`.

- `n = 2`: cop and thief.
- `S`: cop position, thief position, barrier set, remaining barriers, and turn index.
- `A_i`: eight-direction movement for both agents; the cop also has a barrier action. `stay` is
  retained only as a defensive internal enum value and is sanitized away before valid turns are
  recorded.
- `P`: deterministic transition function constrained by grid bounds and barriers.
- `R`: assignment scoring table from `config.json`.
- `Omega_i`: each agent sees its own position, nearby barriers, and the opponent only within a
  configurable visibility radius.
- `O`: the partial-observation function implemented by `GameState.visible_to`.
- `gamma`: not learned in this baseline; the heuristic policy is replaceable by Q-learning later.

## Non-Bonus Scope

The project intentionally stops before inter-group bonus play. Cloud deployment URLs and Gmail
credentials are configuration fields, and the code contains extension points for enabling them after
the local pipeline is accepted.

## Evidence Artifacts

- `reports/internal_game_report.json`: required six-sub-game InternalGameJSON.
- `reports/shadowgrid_replay_<timestamp>.mp4`: saved GUI replay.
- `reports/shadowgrid_replay_<timestamp>_movements.json`: replay audit trail.
- `reports/README.md`: index of all saved report/video artifacts.
