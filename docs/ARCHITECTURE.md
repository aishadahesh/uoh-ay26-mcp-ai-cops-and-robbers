# Architecture

This project implements the required cops-and-robber assignment pipeline plus the inter-group MCP
bonus flow.

## Components

- `GameEngine` owns the grid, turns, movement, barriers, capture detection, and scoring.
- `action_policy.py` validates autonomous-agent actions before they enter CLI/MCP reports.
- `AgentBrain` represents a role-specific autonomous agent. It reads natural language messages,
  extracts soft position hints, and chooses a physical action.
- `LocalOrchestrator` acts as the MCP client/orchestrator. It runs six sub-games, alternates turns,
  passes messages between agents, and writes the InternalGameJSON report.
- `RemoteMcpOrchestrator` runs one group's deployed cop and thief MCP endpoints.
- `BonusMcpOrchestrator` runs the six-game inter-group bonus series, alternating which group owns
  the cop and thief roles.
- `mcp_common.py` builds and runs compact FastMCP server instances.
- `mcp_agent_state.py` owns per-role server state, observations, and action choice.
- `mcp_auth.py` owns bearer-token verification for public bonus endpoints.
- `cop_server.py` and `thief_server.py` expose separate FastMCP tool servers for reset, message
  receive, state update, and action choice.
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

## Bonus Scope

The bonus runner uses one authoritative orchestrator for board state, legality, barriers, scoring,
and reporting. Remote MCP servers only provide role decisions. The verified bonus report contains
six autonomous games against `yanell11`, with final totals `uoh-ay26=85` and `yanell11=45`.

## Evidence Artifacts

- `reports/internal_game_report.json`: required six-sub-game InternalGameJSON.
- `reports/bonus_game_report.json`: six-game inter-group MCP bonus report.
- `reports/shadowgrid_replay_<timestamp>.mp4`: saved GUI replay.
- `reports/shadowgrid_replay_<timestamp>_movements.json`: replay audit trail.
- `reports/README.md`: index of all saved report/video artifacts.
