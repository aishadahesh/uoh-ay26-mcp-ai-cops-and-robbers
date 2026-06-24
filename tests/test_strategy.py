from cops_robbers_ai.models import Move
from cops_robbers_ai.strategy import AgentBrain


def test_cop_does_not_stay_when_hint_equals_own_position() -> None:
    brain = AgentBrain("cop")
    action = brain.choose(
        {"position": {"x": 1, "y": 1}, "opponent": None, "turn_index": 0},
        "I suspect the other agent is around (1,1).",
    )

    assert action.move != Move.STAY


def test_cop_moves_toward_visible_robber() -> None:
    brain = AgentBrain("cop")
    action = brain.choose(
        {"position": {"x": 0, "y": 0}, "opponent": {"x": 2, "y": 2}, "turn_index": 0},
        "",
    )

    assert action.move == Move.SE


def test_thief_does_not_stay_when_hint_equals_own_position() -> None:
    brain = AgentBrain("thief")
    action = brain.choose(
        {"position": {"x": 2, "y": 2}, "opponent": None, "turn_index": 0},
        "I suspect the other agent is around (2,2).",
    )

    assert action.move != Move.STAY
