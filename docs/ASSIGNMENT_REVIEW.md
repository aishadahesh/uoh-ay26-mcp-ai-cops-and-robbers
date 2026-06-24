# Assignment Compliance Review

This review is based on the reference PDFs in `ref/`.

## Implemented

- Local end-to-end game pipeline.
- Two agent roles and separate MCP server modules.
- Natural-language messages between agents.
- Partial observability model.
- Configurable grid and scoring.
- InternalGameJSON report.
- GUI demonstration.
- Optional Gemini/OpenAI API-backed agents.
- Optional Gmail JSON sender.
- `.env.example` and `.gitignore` for secrets.
- README and `reports/README.md` now list the actual saved MP4 and movement JSON evidence files.
- Shared action legality policy for CLI/MCP paths:
  - no `stay` actions are accepted into reports;
  - thief barrier attempts are replaced with a legal movement;
  - illegal off-board or blocked moves are replaced with a legal role-aware move.

## Verified On 2026-06-24

- Re-read `ref/ex06-Dual AI agent race via MCP servers.pdf`.
- Ran `python -m pytest`: 8 tests passed.
- Ran `ruff check src tests`: all checks passed.
- Ran `python -m cops_robbers_ai.cli --print-report`.
- Confirmed the generated `reports/internal_game_report.json` contains:
  - 6 sub-games;
  - thief-first alternating turns;
  - no `stay` moves;
  - no thief barrier moves;
  - no sub-game above the 25 move-pair limit;
  - assignment-shaped `InternalGameJSON` metadata and totals.

## Partially Implemented

- MCP servers are present and runnable locally, but cloud deployment URLs remain placeholders.
- Gmail sender is implemented but disabled until OAuth credentials are configured.
- Video evidence can be generated from GUI games, but screenshots are not committed by default.
- Tests exist for core logic, but coverage target is not yet measured at 85%.

## Deferred By User Request

- Bonus inter-group competition.
- Public cloud deployment.
- Token-authenticated public MCP endpoints.
- Q-learning.

## Important Reference Notes

- The assignment emphasizes orchestration over perfect strategy.
- LLM calls belong in the client/orchestrator side, not inside the MCP server itself.
- JSON report email must contain JSON only.
- Technical-loss games should be rerun rather than counted.
- The software-guidelines PDF expects professional README, docs, PRD, TODO, config hygiene, tests, and visual evidence.
- The scoring section has an apparent ambiguity: the PDF requires 6 sub-games and the config
  table requires `cop_win=20`, so six cop wins total 120. One nearby text line appears to
  mention 90 as a maximum. This implementation follows the explicit config table.

## Recommended Final Submission Steps

1. Fill `students` and `github_repo` in `config.json`.
2. Add real deployed MCP URLs if cloud deployment is required by the evaluator.
3. Run `.\scripts\run_local.ps1`.
4. Play one GUI game and click `Save Game`.
5. Confirm `reports/internal_game_report.json` and replay file exist.
6. Optionally enable Gmail and send the JSON report.
