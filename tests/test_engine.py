from cops_robbers_ai.config import load_config
from cops_robbers_ai.engine import GameEngine
from cops_robbers_ai.models import Action, Move, Position


def test_cop_captures_thief() -> None:
    config = load_config("config.json")
    engine = GameEngine(config)
    state = engine.new_state()
    state.cop = Position(0, 0)
    state.thief = Position(1, 0)

    engine.apply(state, Action("cop", Move.E, "closing in"))

    assert state.captured
    assert engine.result_for(state) == "cop_wins"


def test_barrier_blocks_future_motion() -> None:
    config = load_config("config.json")
    engine = GameEngine(config)
    state = engine.new_state()
    state.cop = Position(1, 1)
    state.thief = Position(0, 0)

    engine.apply(state, Action("cop", Move.BARRIER, "blocking this square"))
    state.thief = Position(1, 0)
    engine.apply(state, Action("thief", Move.S, "trying south"))

    assert state.thief == Position(1, 0)
    assert Position(1, 1) in state.barriers
