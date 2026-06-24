from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal

Role = Literal["cop", "thief"]


class Move(StrEnum):
    STAY = "stay"
    N = "n"
    NE = "ne"
    E = "e"
    SE = "se"
    S = "s"
    SW = "sw"
    W = "w"
    NW = "nw"
    BARRIER = "barrier"


DELTAS: dict[Move, tuple[int, int]] = {
    Move.STAY: (0, 0),
    Move.N: (0, -1),
    Move.NE: (1, -1),
    Move.E: (1, 0),
    Move.SE: (1, 1),
    Move.S: (0, 1),
    Move.SW: (-1, 1),
    Move.W: (-1, 0),
    Move.NW: (-1, -1),
}


@dataclass(frozen=True, slots=True)
class Position:
    x: int
    y: int

    def moved(self, move: Move) -> Position:
        dx, dy = DELTAS.get(move, (0, 0))
        return Position(self.x + dx, self.y + dy)

    def chebyshev(self, other: Position) -> int:
        return max(abs(self.x - other.x), abs(self.y - other.y))


@dataclass(frozen=True, slots=True)
class Action:
    role: Role
    move: Move
    message: str


@dataclass(slots=True)
class GameState:
    width: int
    height: int
    cop: Position
    thief: Position
    barriers: set[Position] = field(default_factory=set)
    cop_barriers_left: int = 5
    turn_index: int = 0
    captured: bool = False

    def visible_to(self, role: Role, radius: int) -> dict[str, object]:
        me = self.cop if role == "cop" else self.thief
        opponent = self.thief if role == "cop" else self.cop
        can_see = me.chebyshev(opponent) <= radius
        nearby = [p for p in self.barriers if me.chebyshev(p) <= radius]
        return {
            "role": role,
            "position": {"x": me.x, "y": me.y},
            "opponent_visible": can_see,
            "opponent": {"x": opponent.x, "y": opponent.y} if can_see else None,
            "nearby_barriers": [
                {"x": p.x, "y": p.y} for p in sorted(nearby, key=lambda p: (p.y, p.x))
            ],
            "turn_index": self.turn_index,
        }
