from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import GameConfig


def build_report(config: GameConfig, sub_games: list[dict[str, object]]) -> dict[str, object]:
    totals = {"cop": 0, "thief": 0}
    for game in sub_games:
        score = game["score"]
        totals["cop"] += int(score["cop"])
        totals["thief"] += int(score["thief"])
    return {
        "group_name": config.group_name,
        "students": config.students,
        "github_repo": config.github_repo,
        "cop_mcp_url": config.cop_mcp_url,
        "thief_mcp_url": config.thief_mcp_url,
        "timezone": config.timezone,
        "generated_at": datetime.now(ZoneInfo(config.timezone)).isoformat(),
        "sub_games": sub_games,
        "totals": totals,
    }


def write_report(report: dict[str, object], output_dir: str | Path = "reports") -> Path:
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "internal_game_report.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def build_bonus_report(
    config: GameConfig,
    bonus_config: dict[str, object],
    sub_games: list[dict[str, object]],
) -> dict[str, object]:
    group_1 = str(bonus_config["group_1"])
    group_2 = str(bonus_config["group_2"])
    totals_by_group = {group_1: 0, group_2: 0}

    for game in sub_games:
        group_scores = game["group_scores"]
        totals_by_group[group_1] += int(group_scores[group_1])
        totals_by_group[group_2] += int(group_scores[group_2])

    if totals_by_group[group_1] > totals_by_group[group_2]:
        bonus_claim = {group_1: 10, group_2: 7}
    elif totals_by_group[group_2] > totals_by_group[group_1]:
        bonus_claim = {group_1: 7, group_2: 10}
    else:
        bonus_claim = {group_1: 5, group_2: 5}

    return {
        "report_type": "bonus_game",
        "groups": {
            "group_1": group_1,
            "group_2": group_2,
        },
        "github_repo_group_1": str(bonus_config["github_repo_group_1"]),
        "github_repo_group_2": str(bonus_config["github_repo_group_2"]),
        "mcp_url_group_1_cop": str(bonus_config["mcp_url_group_1_cop"]),
        "mcp_url_group_1_thief": str(bonus_config["mcp_url_group_1_thief"]),
        "mcp_url_group_2_cop": str(bonus_config["mcp_url_group_2_cop"]),
        "mcp_url_group_2_thief": str(bonus_config["mcp_url_group_2_thief"]),
        "timezone": config.timezone,
        "generated_at": datetime.now(ZoneInfo(config.timezone)).isoformat(),
        "students_group_1": list(bonus_config.get("students_group_1", config.students)),
        "students_group_2": list(bonus_config.get("students_group_2", [])),
        "sub_games": sub_games,
        "totals_by_group": totals_by_group,
        "bonus_claim": bonus_claim,
        "mutual_agreement": bool(bonus_config.get("mutual_agreement", True)),
    }


def write_bonus_report(report: dict[str, object], output_dir: str | Path = "reports") -> Path:
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "bonus_game_report.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def send_report_email(config: GameConfig, report: dict[str, object]) -> bool:
    if not config.email.enabled:
        return False
    from .gmail_client import send_json_email

    send_json_email(config.email.to, report, config.email.credentials_path, config.email.token_path)
    return True
