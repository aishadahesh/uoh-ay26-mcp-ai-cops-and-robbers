# PRD: Game Engine

## Purpose

The game engine owns deterministic state transitions for the cops-and-robber grid. It is intentionally independent from GUI, LLM providers, and MCP transport.

## Requirements

- Maintain board size from configuration.
- Validate legal movement within grid bounds.
- Support eight-direction moves and stay.
- Support cop barrier placement.
- Prevent movement into barriers.
- Detect capture immediately after each action.
- Detect robber survival after maximum moves.
- Produce snapshots for reports, GUI, and replay export.

## Acceptance Criteria

- Capture occurs when cop and robber positions are equal.
- Barriers block both roles.
- Max moves creates a robber win.
- Score values come from configuration.
- Tests cover core transitions.
