from __future__ import annotations

from .models import Action, GameState, Move, Position, Role

MOVEMENT_MOVES = (Move.N, Move.NE, Move.E, Move.SE, Move.S, Move.SW, Move.W, Move.NW)


def sanitize_action(state: GameState, action: Action) -> Action:
    """Return a legal, non-stay action for the current role."""
    if action.role == "cop" and action.move == Move.BARRIER and _can_place_barrier(state):
        return action
    if action.move in _legal_movement_moves(state, action.role):
        return action

    replacement = _best_movement(state, action.role)
    return Action(
        action.role,
        replacement,
        f"{action.message} Adjusted to legal move {replacement.value}.",
    )


def _legal_movement_moves(state: GameState, role: Role) -> list[Move]:
    current = state.cop if role == "cop" else state.thief
    return [move for move in MOVEMENT_MOVES if _is_open(current.moved(move), state)]


def _best_movement(state: GameState, role: Role) -> Move:
    legal = _legal_movement_moves(state, role)
    if not legal:
        return Move.N
    current = state.cop if role == "cop" else state.thief
    opponent = state.thief if role == "cop" else state.cop

    def score(move: Move) -> tuple[int, int]:
        candidate = current.moved(move)
        distance = candidate.chebyshev(opponent)
        edge_bonus = int(candidate.x in {0, state.width - 1}) + int(
            candidate.y in {0, state.height - 1}
        )
        if role == "cop":
            return (-distance, edge_bonus)
        return (distance, edge_bonus)

    return max(legal, key=score)


def _is_open(pos: Position, state: GameState) -> bool:
    return 0 <= pos.x < state.width and 0 <= pos.y < state.height and pos not in state.barriers


def _can_place_barrier(state: GameState) -> bool:
    return (
        state.cop_barriers_left > 0
        and state.cop != state.thief
        and state.cop not in state.barriers
    )
