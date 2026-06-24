# PRD: Agent Orchestration

## Purpose

Agent orchestration coordinates role decisions, partial observations, provider calls, natural-language messages, and MCP-facing behavior.

## Requirements

- The robber moves first.
- The cop moves second.
- Each role receives partial observation.
- Each role produces a natural-language message.
- Provider-backed agents shall support Gemini and OpenAI.
- Missing keys shall fall back to deterministic strategy.
- MCP servers shall expose tools but not own long-running game orchestration.

## Acceptance Criteria

- Agent decisions can run without API keys.
- OpenAI-vs-Gemini mode can be selected in GUI.
- Natural-language messages are logged.
- MCP server modules import and expose tool functions.
