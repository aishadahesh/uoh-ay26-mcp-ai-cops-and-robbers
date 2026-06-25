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


def test_state_starts_with_configured_barrier_budget() -> None:
    config = load_config("config.json")
    engine = GameEngine(config)
    state = engine.new_state()

    assert state.cop_barriers_left == config.max_barriers
    assert engine.snapshot(state)["cop_barriers_left"] == config.max_barriers


def test_cop_cannot_place_more_than_max_barriers() -> None:
    config = load_config("config.json")
    engine = GameEngine(config)
    state = engine.new_state()
    state.thief = Position(4, 4)

    barrier_positions = [
        Position(0, 0),
        Position(1, 0),
        Position(2, 0),
        Position(3, 0),
        Position(4, 0),
        Position(4, 1),
    ]

    for pos in barrier_positions:
        state.cop = pos
        engine.apply(state, Action("cop", Move.BARRIER, "placing barrier"))

    assert len(state.barriers) == config.max_barriers
    assert state.cop_barriers_left == 0
    assert Position(4, 1) not in state.barriers


def test_duplicate_barrier_does_not_consume_budget() -> None:
    config = load_config("config.json")
    engine = GameEngine(config)
    state = engine.new_state()
    state.cop = Position(2, 2)
    state.thief = Position(4, 4)

    engine.apply(state, Action("cop", Move.BARRIER, "first barrier"))
    left_after_first = state.cop_barriers_left
    engine.apply(state, Action("cop", Move.BARRIER, "duplicate barrier"))

    assert len(state.barriers) == 1
    assert state.cop_barriers_left == left_after_first