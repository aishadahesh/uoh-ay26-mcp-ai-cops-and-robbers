from __future__ import annotations

import re
from dataclasses import dataclass

from .models import Action, Move, Position, Role

MOVE_WORDS: dict[str, Move] = {
    "north": Move.N,
    "northeast": Move.NE,
    "east": Move.E,
    "southeast": Move.SE,
    "south": Move.S,
    "southwest": Move.SW,
    "west": Move.W,
    "northwest": Move.NW,
    "hold": Move.STAY,
    "stay": Move.STAY,
}


@dataclass(slots=True)
class AgentBrain:
    role: Role
    last_opponent_hint: Position | None = None

    def observe_message(self, message: str) -> None:
        match = re.search(r"I am at \((\d+)\s*,\s*(\d+)\)", message)
        if not match:
            match = re.search(r"around \((\d+)\s*,\s*(\d+)\)", message)
        if not match:
            match = re.search(r"\((\d+)\s*,\s*(\d+)\)", message)
        if match:
            self.last_opponent_hint = Position(int(match.group(1)), int(match.group(2)))

    def choose(self, observation: dict[str, object], inbound_message: str) -> Action:
        self.observe_message(inbound_message)
        me = _position_from_dict(observation["position"])
        visible = observation.get("opponent") is not None
        target = (
            _position_from_dict(observation["opponent"])
            if visible
            else self.last_opponent_hint
        )
        if self.role == "cop":
            move = self._cop_move(me, target, int(observation["turn_index"]))
        else:
            move = self._thief_move(me, target)
        message = self._natural_message(me, target, visible, move)
        return Action(self.role, move, message)

    def _cop_move(self, me: Position, target: Position | None, turn_index: int) -> Move:
        if target == me:
            return [Move.E, Move.S, Move.W, Move.N][turn_index % 4]
        if target and me.chebyshev(target) <= 1:
            return _step_toward(me, target)
        if target:
            return _step_toward(me, target)
        if turn_index % 7 == 5:
            return Move.BARRIER
        return [Move.E, Move.S, Move.W, Move.N][turn_index % 4]

    def _thief_move(self, me: Position, target: Position | None) -> Move:
        if target == me:
            return [Move.NW, Move.SE, Move.NE, Move.SW][(me.x + me.y) % 4]
        if target:
            return _step_away(me, target)
        return [Move.NW, Move.SE, Move.NE, Move.SW][(me.x + me.y) % 4]

    def _natural_message(
        self, me: Position, target: Position | None, visible: bool, move: Move
    ) -> str:
        if visible and target:
            return (
                f"I can see pressure near ({target.x},{target.y}); "
                f"I am at ({me.x},{me.y}) moving {move.value}."
            )
        if target:
            return (
                f"I suspect the other agent is around ({target.x},{target.y}); "
                f"I will move {move.value}."
            )
        return (
            f"My local view is quiet from ({me.x},{me.y}); "
            f"I choose {move.value} and keep scouting."
        )


def _position_from_dict(value: object) -> Position:
    data = value if isinstance(value, dict) else {"x": 0, "y": 0}
    return Position(int(data["x"]), int(data["y"]))


def _step_toward(start: Position, target: Position) -> Move:
    return _move_from_delta(_sign(target.x - start.x), _sign(target.y - start.y))


def _step_away(start: Position, target: Position) -> Move:
    return _move_from_delta(_sign(start.x - target.x), _sign(start.y - target.y))


def _move_from_delta(dx: int, dy: int) -> Move:
    for move, delta in {
        Move.N: (0, -1),
        Move.NE: (1, -1),
        Move.E: (1, 0),
        Move.SE: (1, 1),
        Move.S: (0, 1),
        Move.SW: (-1, 1),
        Move.W: (-1, 0),
        Move.NW: (-1, -1),
    }.items():
        if delta == (dx, dy):
            return move
    return Move.STAY


def _sign(value: int) -> int:
    return (value > 0) - (value < 0)
