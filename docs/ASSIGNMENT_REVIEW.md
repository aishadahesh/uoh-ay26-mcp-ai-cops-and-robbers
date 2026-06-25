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
- Bonus Gmail attachment sender from both group accounts.
- `.env.example` and `.gitignore` for secrets.
- README and `reports/README.md` now list the actual saved MP4 and movement JSON evidence files.
- Shared action legality policy for CLI/MCP paths:
  - no `stay` actions are accepted into reports;
  - thief barrier attempts are replaced with a legal movement;
  - illegal off-board or blocked moves are replaced with a legal role-aware move.

## Verified On 2026-06-26

- Re-read `ref/ex06-Dual AI agent race via MCP servers.pdf`.
- Verified the README requirements on PDF pages 13-14: GitHub source, `README.md`, formal
  Dec-POMDP tuple, orchestration challenge analysis, visualization, Q-table/strategy discussion,
  CLI logs, and MCP evidence.
- Verified the bonus requirements on PDF pages 14-15: two groups, 6 games, role swap after the
  first 3 games, matching JSON agreement, and winner/loser bonus scoring.
- Ran `python -m pytest`: 13 tests passed.
- Ran `ruff check src tests`: all checks passed.
- Ran `python -m cops_robbers_ai.cli --print-report`.
- Ran `python -m cops_robbers_ai.cli --bonus-config bonus_config.json --print-report`.
- Confirmed the generated `reports/internal_game_report.json` contains:
  - 6 sub-games;
  - thief-first alternating turns;
  - no `stay` moves;
  - no thief barrier moves;
  - no sub-game above the 25 move-pair limit;
  - assignment-shaped `InternalGameJSON` metadata and totals.
- Confirmed the generated `reports/bonus_game_report.json` contains:
  - 6 inter-group remote MCP sub-games;
  - 3 games with `uoh-ay26` cop vs `yanell11` thief;
  - 3 games with `yanell11` cop vs `uoh-ay26` thief;
  - final win count `uoh-ay26=5`, `yanell11=1`;
  - final score totals `uoh-ay26=85`, `yanell11=45`;
  - agreed bonus claim `uoh-ay26=10`, `yanell11=7`;
  - `mutual_agreement=true`.
- Confirmed every `.py` file in `src/` is at or below 150 lines.
- Confirmed `mcp_common.py` was split into smaller focused modules:
  `mcp_common.py`, `mcp_agent_state.py`, and `mcp_auth.py`.

## Partially Implemented

- Video evidence can be generated from GUI games, but screenshots are not committed by default.
- Tests exist for core logic, but coverage target is not yet measured at 85%.

## Deferred By User Request

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

## Requirement Interpretation

The PDF distinguishes the MCP server from the MCP client. This project interprets that as follows:
MCP servers expose tools and role-specific behavior, while the orchestrator owns the conversation,
turn sequence, legality, scoring, and report generation. This is why `cop_server.py` and
`thief_server.py` are intentionally small entry points and the richer match logic lives in the
orchestrator layer.

The README requirement asks for a scientific report, not only run instructions. The final README
therefore includes the formal tuple, partial observation definition, strategy discussion, visual
evidence, tools, challenges, results, self-scoring, and bonus agreement. The screenshots and GIFs
are supporting evidence, while the JSON reports are the authoritative audit trail.

## Evidence Quality

The strongest evidence files are:

- `reports/internal_game_report.json`: proves the mandatory local series.
- `reports/bonus_game_report.json`: proves the six-game inter-group bonus.
- `reports/*_movements.json`: proves replay-level GUI movement history.
- `assets/email_sent.png`: shows the bonus JSON attachment was sent by Gmail.
- `README.md`: ties the artifacts into a human-readable scientific report.

Known limitations are documented openly. The project does not claim a trained Q-table policy; it
uses a transparent heuristic plus optional LLM reasoning. This matches the development-priority
table in the assignment, where heuristic or Q-table strategy are both acceptable paths.

## Recommended Final Submission Steps

1. Fill `students` and `github_repo` in `config.json`.
2. Confirm the four bonus MCP URLs and two group tokens in `bonus_config.json`.
3. Run `.\scripts\run_local.ps1`.
4. Run `python -m cops_robbers_ai.cli --bonus-config bonus_config.json --print-report`.
5. Play one GUI game and click `Save Game`.
6. Confirm `reports/internal_game_report.json`, `reports/bonus_game_report.json`, and replay files exist.
