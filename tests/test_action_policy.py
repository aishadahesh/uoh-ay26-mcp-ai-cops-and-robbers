from cops_robbers_ai.action_policy import sanitize_action
from cops_robbers_ai.models import Action, GameState, Move, Position


def test_sanitize_replaces_stay_with_legal_movement() -> None:
    state = GameState(5, 5, Position(2, 2), Position(4, 4))
    action = sanitize_action(state, Action("cop", Move.STAY, "I will wait."))

    assert action.move != Move.STAY
    assert action.move in {Move.SE, Move.E, Move.S}


def test_sanitize_blocks_thief_barrier() -> None:
    state = GameState(5, 5, Position(0, 0), Position(2, 2))
    action = sanitize_action(state, Action("thief", Move.BARRIER, "I place a barrier."))

    assert action.move != Move.BARRIER
    assert action.move != Move.STAY
