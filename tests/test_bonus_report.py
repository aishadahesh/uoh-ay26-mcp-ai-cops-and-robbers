from cops_robbers_ai.config import load_config
from cops_robbers_ai.reporting import build_bonus_report


def test_bonus_report_maps_role_scores_to_groups() -> None:
    config = load_config("config.json")
    bonus_config = {
        "group_1": "Team-A",
        "group_2": "Team-B",
        "github_repo_group_1": "https://example.com/a",
        "github_repo_group_2": "https://example.com/b",
        "mcp_url_group_1_cop": "https://a-cop.ngrok-free.app/mcp",
        "mcp_url_group_1_thief": "https://a-thief.ngrok-free.app/mcp",
        "mcp_url_group_2_cop": "https://b-cop.ngrok-free.app/mcp",
        "mcp_url_group_2_thief": "https://b-thief.ngrok-free.app/mcp",
    }
    sub_games = [
        {
            "sub_game_id": 1,
            "group_scores": {"Team-A": 20, "Team-B": 5},
        },
        {
            "sub_game_id": 2,
            "group_scores": {"Team-A": 5, "Team-B": 10},
        },
    ]

    report = build_bonus_report(config, bonus_config, sub_games)

    assert report["report_type"] == "bonus_game"
    assert report["mcp_url_group_1_cop"] == "https://a-cop.ngrok-free.app/mcp"
    assert report["mcp_url_group_2_thief"] == "https://b-thief.ngrok-free.app/mcp"
    assert report["totals_by_group"] == {"Team-A": 25, "Team-B": 15}
    assert report["bonus_claim"] == {"Team-A": 10, "Team-B": 7}
    assert report["mutual_agreement"] is True
