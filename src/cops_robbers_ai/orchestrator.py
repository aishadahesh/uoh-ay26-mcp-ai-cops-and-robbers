from __future__ import annotations

from .action_policy import sanitize_action
from .config import GameConfig
from .engine import GameEngine
from .llm_agent import GeminiAgent
from .reporting import build_report, send_report_email, write_report


class LocalOrchestrator:
    def __init__(self, config: GameConfig) -> None:
        self.config = config

    def run_series(self) -> dict[str, object]:
        sub_games = [self._run_one(index) for index in range(1, self.config.num_games + 1)]
        report = build_report(self.config, sub_games)
        write_report(report)
        send_report_email(self.config, report)
        return report

    def _run_one(self, index: int) -> dict[str, object]:
        engine = GameEngine(self.config, seed_offset=index)
        state = engine.new_state()
        cop = GeminiAgent("cop", self.config.llm)
        thief = GeminiAgent("thief", self.config.llm)
        inbox = {"cop": "", "thief": ""}
        turns: list[dict[str, object]] = []

        while not engine.result_for(state):
            role = "thief" if state.turn_index % 2 == 0 else "cop"
            brain = thief if role == "thief" else cop
            observation = state.visible_to(role, self.config.visibility_radius)
            action = brain.choose(observation, inbox[role])
            action = sanitize_action(state, action)
            engine.apply(state, action)
            inbox["cop" if role == "thief" else "thief"] = action.message
            turns.append(
                {
                    "role": role,
                    "move": action.move.value,
                    "message": action.message,
                    "state": engine.snapshot(state),
                }
            )

        result = engine.result_for(state) or "technical_loss"
        return {
            "sub_game_id": index,
            "result": result,
            "moves": len(turns),
            "score": engine.score(result),
            "turns": turns,
        }
