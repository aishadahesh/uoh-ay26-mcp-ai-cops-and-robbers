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

## Runtime Flow

The local and bonus modes follow the same control pattern. The orchestrator creates a fresh
`GameState`, decides whose turn it is from `turn_index`, asks that role for an action, sanitizes the
action, applies it through `GameEngine`, and appends the resulting snapshot to the report. This
keeps the game deterministic and auditable: agents can propose actions, but they do not own the
truth of the board.

For local games, `LocalOrchestrator` calls the in-process `GeminiAgent` instances directly. For
bonus games, `BonusMcpOrchestrator` calls remote MCP tools. In both cases the final report shape is
the same kind of evidence: a list of sub-games, turns, messages, states, and scores.

```text
config.json
   -> orchestrator
      -> observation/message
         -> agent or remote MCP tool
            -> proposed action
               -> action_policy.sanitize_action
                  -> GameEngine.apply
                     -> JSON report
```

## Turn Lifecycle

1. The thief moves first, as required by the assignment.
2. The active role receives a partial observation.
3. The active role also receives the last natural-language message sent by the opponent.
4. The role chooses a move or, for the cop, possibly a barrier action.
5. The action policy rejects illegal final actions such as `stay`, off-board moves, thief barriers,
   or blocked moves.
6. The game engine applies the legal action and checks capture or survival.
7. The orchestrator records the message, move, state snapshot, and score-relevant outcome.

The important engineering decision is that every path, including GUI, local CLI, and remote MCP,
passes through the same rule engine. This prevents the demo and the submitted report from drifting
into different games.

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

The six bonus games are split exactly as the PDF describes:

- games 1-3: `uoh-ay26` cop against `yanell11` thief;
- games 4-6: `yanell11` cop against `uoh-ay26` thief.

The orchestrator sends `update_state`, `receive_message`, and `choose_action` calls to each remote
agent. Tokens are configured locally and ignored by Git. The committed repository contains the
example config and final JSON evidence, but not the private tokens.

## Failure Handling

LLM and network calls are the least deterministic parts of the project. The implementation reduces
that risk in four ways:

- provider calls fall back to deterministic behavior when API keys or quotas fail;
- remote MCP output is sanitized before it becomes part of the official game;
- reports store all turns, making questionable behavior visible rather than hidden;
- private operational files such as OAuth tokens, `.env`, `bonus_config.json`, and `ngrok.yml` are
  ignored by Git.

## Evidence Artifacts

- `reports/internal_game_report.json`: required six-sub-game InternalGameJSON.
- `reports/bonus_game_report.json`: six-game inter-group MCP bonus report.
- `reports/shadowgrid_replay_<timestamp>.mp4`: saved GUI replay.
- `reports/shadowgrid_replay_<timestamp>_movements.json`: replay audit trail.
- `reports/README.md`: index of all saved report/video artifacts.
