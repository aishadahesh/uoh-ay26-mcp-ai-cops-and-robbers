from cops_robbers_ai.config import load_config
from cops_robbers_ai.orchestrator import LocalOrchestrator


def test_series_report_has_required_shape() -> None:
    config = load_config("config.json")
    report = LocalOrchestrator(config).run_series()

    assert report["group_name"] == config.group_name
    assert len(report["sub_games"]) == config.num_games
    assert set(report["totals"]) == {"cop", "thief"}
    assert all(game["result"] in {"cop_wins", "thief_wins"} for game in report["sub_games"])
