from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ScoringConfig:
    cop_win: int = 20
    thief_win: int = 10
    cop_loss: int = 5
    thief_loss: int = 5


@dataclass(frozen=True, slots=True)
class EmailConfig:
    enabled: bool = False
    to: str = "rmisegal+uoh26b@gmail.com"
    credentials_path: str = "credentials.json"
    token_path: str = "token.json"


@dataclass(frozen=True, slots=True)
class LlmConfig:
    provider: str = "heuristic"
    model: str = "gemini-1.5-flash"
    gemini_model: str = "gemini-1.5-flash"
    openai_model: str = "gpt-4o-mini"
    temperature: float = 0.2
    fallback_to_heuristic: bool = True


@dataclass(frozen=True, slots=True)
class GameConfig:
    group_name: str
    students: list[str]
    github_repo: str
    cop_mcp_url: str
    thief_mcp_url: str
    timezone: str
    grid_size: tuple[int, int]
    max_moves: int
    num_games: int
    max_barriers: int
    visibility_radius: int
    random_seed: int
    llm: LlmConfig
    scoring: ScoringConfig
    email: EmailConfig


def load_config(path: str | Path = "config.json") -> GameConfig:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    scoring = ScoringConfig(**data.get("scoring", {}))
    email = EmailConfig(**data.get("email", {}))
    llm = LlmConfig(**data.get("llm", {}))
    return GameConfig(
        group_name=data["group_name"],
        students=list(data.get("students", [])),
        github_repo=data["github_repo"],
        cop_mcp_url=data["cop_mcp_url"],
        thief_mcp_url=data["thief_mcp_url"],
        timezone=data.get("timezone", "Asia/Jerusalem"),
        grid_size=tuple(data.get("grid_size", [5, 5])),
        max_moves=int(data.get("max_moves", 25)),
        num_games=int(data.get("num_games", 6)),
        max_barriers=int(data.get("max_barriers", 5)),
        visibility_radius=int(data.get("visibility_radius", 2)),
        random_seed=int(data.get("random_seed", 26)),
        llm=llm,
        scoring=scoring,
        email=email,
    )
