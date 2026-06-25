from __future__ import annotations

import random
from dataclasses import asdict

from .config import GameConfig
from .models import Action, GameState, Move, Position


class GameEngine:
    def __init__(self, config: GameConfig, seed_offset: int = 0) -> None:
        self.config = config
        self.rng = random.Random(config.random_seed + seed_offset)

    def new_state(self) -> GameState:
        width, height = self.config.grid_size
        cop = self._random_position(width, height, set())
        thief = self._random_position(width, height, {cop})
        return GameState(width, height, cop, thief, set(), self.config.max_barriers)

    def apply(self, state: GameState, action: Action) -> None:
        if state.captured:
            return
        if action.role == "cop" and action.move == Move.BARRIER:
            self._place_barrier(state)
        elif action.move in Move:
            self._move_agent(state, action)
        state.turn_index += 1
        state.captured = state.cop == state.thief

    def result_for(self, state: GameState) -> str | None:
        if state.captured:
            return "cop_wins"
        if state.turn_index >= self.config.max_moves * 2:
            return "thief_wins"
        return None

    def score(self, result: str) -> dict[str, int]:
        if result == "cop_wins":
            return {"cop": self.config.scoring.cop_win, "thief": self.config.scoring.thief_loss}
        return {"cop": self.config.scoring.cop_loss, "thief": self.config.scoring.thief_win}

    def snapshot(self, state: GameState) -> dict[str, object]:
        return {
            "cop": asdict(state.cop),
            "thief": asdict(state.thief),
            "barriers": [asdict(p) for p in sorted(state.barriers, key=lambda p: (p.y, p.x))],
            "cop_barriers_left": state.cop_barriers_left,
            "turn_index": state.turn_index,
            "captured": state.captured,
        }

    def _place_barrier(self, state: GameState) -> None:
        if state.cop_barriers_left <= 0 or state.cop == state.thief or state.cop in state.barriers:
            return
        state.barriers.add(state.cop)
        state.cop_barriers_left -= 1

    def _move_agent(self, state: GameState, action: Action) -> None:
        current = state.cop if action.role == "cop" else state.thief
        candidate = current.moved(action.move)
        if not self._is_open(candidate, state):
            candidate = current
        if action.role == "cop":
            state.cop = candidate
        else:
            state.thief = candidate

    def _is_open(self, pos: Position, state: GameState) -> bool:
        in_bounds = 0 <= pos.x < state.width and 0 <= pos.y < state.height
        return in_bounds and pos not in state.barriers

    def _random_position(self, width: int, height: int, blocked: set[Position]) -> Position:
        while True:
            pos = Position(self.rng.randrange(width), self.rng.randrange(height))
            if pos not in blocked:
                return pos
