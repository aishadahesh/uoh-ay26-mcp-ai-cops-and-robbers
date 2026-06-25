# Prompt Engineering Log

## Purpose

This document records the AI-assisted development process and major prompt goals, as requested by the professional software submission guidelines.

## Development Prompts

1. Build a cops-and-robber multi-agent project based on the reference PDFs, then extend it with
   the requested inter-group bonus flow.
2. Add Gemini API support through `.env`.
3. Build a playable GUI with click movement and multiple play modes.
4. Add OpenAI-vs-Gemini agent mode.
5. Improve GUI presentation while keeping the working code stable.
6. Add replay export as a saved game video.
7. Upgrade docs to match course guidelines and assignment expectations.

## Lessons Applied

- Kept API keys in `.env`.
- Kept configuration in `config.json`.
- Added deterministic fallback for unreliable or missing API providers.
- Split game logic, agents, reporting, GUI, and export modules.
- Added bonus scope after the user requested inter-group competition support.
