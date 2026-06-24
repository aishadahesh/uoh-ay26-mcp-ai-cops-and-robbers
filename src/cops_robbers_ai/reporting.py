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


def send_report_email(config: GameConfig, report: dict[str, object]) -> bool:
    if not config.email.enabled:
        return False
    from .gmail_client import send_json_email

    send_json_email(config.email.to, report, config.email.credentials_path, config.email.token_path)
    return True
