# Implementation Plan

## Phase 1: Local Correctness

- Implement configurable grid rules.
- Implement movement, capture, barriers, and scoring.
- Add deterministic agents for offline validation.
- Generate InternalGameJSON.
- Add unit tests for game rules and report shape.

## Phase 2: Agent Orchestration

- Add separate cop and robber MCP server entry points.
- Keep LLM reasoning in the client/orchestrator layer.
- Add natural-language message parsing.
- Add Gemini and OpenAI provider support.
- Keep deterministic fallback for missing keys or API failures.

## Phase 3: Demonstration Layer

- Add playable GUI.
- Add click-to-move and legal-move highlighting.
- Add user/agent and agent/agent modes.
- Add start and end presentation overlays.
- Add saved game replay export.

## Phase 4: Submission Hardening

- Upgrade README and documentation.
- Add PRD, requirements, assignment review, prompt log, and TODO backlog.
- Verify `.env.example`, `.gitignore`, and config hygiene.
- Produce report and replay evidence.

## Phase 5: Future Advanced Work

- Deploy MCP servers publicly.
- Add token authentication.
- Enable Gmail report sending.
- Add Q-learning or another adaptive strategy.
- Add inter-group bonus match orchestration.
