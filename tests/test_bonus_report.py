from cops_robbers_ai import orchestrator
from cops_robbers_ai.config import load_config
from cops_robbers_ai.orchestrator import BonusMcpOrchestrator
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


def test_bonus_orchestrator_mirrors_seed_offsets_for_role_swap(monkeypatch) -> None:
    monkeypatch.setattr(orchestrator, "write_bonus_report", lambda report: "reports/bonus.json")
    monkeypatch.setattr(
        orchestrator,
        "send_bonus_report_emails",
        lambda bonus_config, report, attachment_path: [],
    )
    config = load_config("config.json")
    bonus_config = {
        "group_1": "Team-A",
        "group_2": "Team-B",
        "github_repo_group_1": "https://example.com/a",
        "github_repo_group_2": "https://example.com/b",
        "mcp_url_group_1_cop": "https://a-cop.example.com/mcp",
        "mcp_url_group_1_thief": "https://a-thief.example.com/mcp",
        "mcp_url_group_2_cop": "https://b-cop.example.com/mcp",
        "mcp_url_group_2_thief": "https://b-thief.example.com/mcp",
        "games_per_pairing": 3,
    }
    calls = []

    class RecordingBonusOrchestrator(BonusMcpOrchestrator):
        async def _run_one(self, **kwargs):
            calls.append(kwargs)
            return {
                "sub_game_id": kwargs["index"],
                "group_scores": {"Team-A": 0, "Team-B": 0},
            }

    RecordingBonusOrchestrator(config, bonus_config).run_series()

    assert [call["index"] for call in calls] == [1, 2, 3, 4, 5, 6]
    assert [call["seed_offset"] for call in calls] == [1, 2, 3, 1, 2, 3]
