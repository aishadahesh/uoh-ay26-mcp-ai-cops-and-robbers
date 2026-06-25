# Product Requirements Document: ShadowGrid Agent Chase Protocol

## 1. Project Overview

ShadowGrid Agent Chase Protocol is a multi-agent cops-and-robber game built for the Orchestration of AI Agents course. The system demonstrates two autonomous agents that communicate in natural language, reason under partial observation, convert messages into physical moves on a grid, and report a complete six-sub-game series in the required InternalGameJSON format.

The project also includes an interactive GUI for demonstration, replay recording, optional
provider-backed agents using Gemini and OpenAI API keys, and a bonus runner for inter-group MCP
competition.

## 2. Problem Statement

The assignment requires more than a path-finding game. Its main goal is to prove orchestration: independent agents, MCP-style server boundaries, client-side decision flow, natural-language communication, partial observability, configuration-driven rules, reporting, and evidence of working execution.

## 3. Goals

- Run six valid cops-and-robber sub-games from configuration.
- Keep game rules configurable rather than hard-coded into orchestration logic.
- Expose separate cop and robber MCP server entry points.
- Support natural-language message exchange between agents.
- Support partial observation through a visibility radius.
- Produce InternalGameJSON for the assignment report.
- Provide a GUI demonstration with user/agent and agent/agent modes.
- Save a final game replay video after GUI game completion.
- Run the six-game inter-group bonus series through remote MCP URLs.
- Send the agreed bonus JSON attachment from both group Gmail accounts.
- Keep secrets out of source control through `.env` and `.env.example`.

## 4. Non-Goals

- Reinforcement learning is not mandatory and remains an extension path.

## 5. Personas

- Course evaluator: needs reproducible execution, clean docs, and evidence matching assignment rules.
- Student/developer: needs clear setup, configuration, testing, and extension instructions.
- Demo viewer: needs a visually understandable GUI that shows moves, legal choices, and winner.

## 6. Functional Requirements

- FR-001: The game shall use a configurable grid size, defaulting to 5x5.
- FR-002: The game shall run six sub-games per full local series.
- FR-003: The robber shall move before the cop in each turn cycle.
- FR-004: The cop shall win when it lands exactly on the robber square.
- FR-005: The robber shall win when it survives the configured maximum moves.
- FR-006: The cop shall be able to place up to five barriers per sub-game.
- FR-007: Barriers shall block both agents.
- FR-008: Agents shall communicate using natural-language messages.
- FR-009: Agents shall receive partial observations only.
- FR-010: The report shall include group metadata, GitHub URL, MCP URLs, sub-games, and totals.
- FR-011: GUI shall support cop-agent/robber-user mode.
- FR-012: GUI shall support cop-user/robber-agent mode.
- FR-013: GUI shall support cop-user/robber-user mode.
- FR-014: GUI shall support OpenAI-cop/Gemini-robber mode.
- FR-015: GUI shall allow click-to-move on highlighted legal squares.
- FR-016: GUI shall allow final replay export after game completion.
- FR-017: Bonus mode shall run three games per role pairing against a partner group.
- FR-018: Bonus mode shall write `reports/bonus_game_report.json`.
- FR-019: Bonus mode shall send the agreed JSON report as an attachment from both group accounts
  when Gmail OAuth tokens are configured.

## 7. Non-Functional Requirements

- NFR-001: Configuration values shall live in `config.json` or `.env`.
- NFR-002: API keys shall never be committed.
- NFR-003: Core modules should remain focused and small.
- NFR-004: The system should run locally without API keys by using deterministic fallback agents.
- NFR-005: GUI failure shall not prevent CLI execution.
- NFR-006: Replay export shall fall back from MP4 to GIF when MP4 encoding is unavailable.

## 8. Success Metrics

- Six sub-games complete without technical loss.
- InternalGameJSON is generated under `reports/internal_game_report.json`.
- GUI game can be completed and saved.
- Tests pass for capture, barrier blocking, and report shape.
- Documentation covers setup, execution, architecture, requirements, and compliance.
- Bonus report contains six completed inter-group MCP games and matching score agreement.

## 9. Acceptance Criteria

- AC-001: `python -m cops_robbers_ai.cli` writes a valid report.
- AC-002: `python -m cops_robbers_ai.gui` starts the GUI.
- AC-003: A user can play one complete GUI game.
- AC-004: `Save Game` is available after a game ends.
- AC-005: The saved replay stops on the final board.
- AC-006: `.env.example` includes Gemini and OpenAI key placeholders.
- AC-007: README contains setup, run commands, report evidence, and feature summary.
- AC-008: `python -m cops_robbers_ai.cli --bonus-config bonus_config.json --print-report`
  writes the agreed six-game bonus report.

## 10. Dependencies

- Python 3.11 or newer.
- `mcp` for FastMCP server interfaces.
- `google-genai` for Gemini agents.
- `openai` for OpenAI agents.
- `pillow`, `imageio`, and `imageio-ffmpeg` for replay export.
- Google OAuth packages for optional Gmail report sending.

## 11. Risks

- API quota or key problems can break provider-backed agents. Mitigation: deterministic fallback.
- MP4 encoding may fail on some systems. Mitigation: GIF fallback.
- GUI layout can vary across Windows display scaling. Mitigation: centered window and visible top controls.
- Remote MCP servers may be slow or asleep. Mitigation: use longer command timeouts and keep
  deterministic legality correction inside the orchestrator.

## 12. Future Extensions

- Add Q-learning strategy module.
- Add richer analytics and charts.
