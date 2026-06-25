from __future__ import annotations

from .action_policy import sanitize_action
from .config import load_config
from .engine import GameEngine
from .env_loader import load_dotenv
from .llm_agent import GeminiAgent
from .models import GameState, Position, Role


class AgentServerState:
    def __init__(self, role: Role) -> None:
        self.role = role
        load_dotenv()
        self.config = load_config()
        self.engine = GameEngine(self.config)
        self.state: GameState | None = None
        self.brain = GeminiAgent(role, self.config.llm)
        self.last_message = ""

    def reset(self, cop_x: int, cop_y: int, thief_x: int, thief_y: int) -> str:
        width, height = self.config.grid_size
        self.state = GameState(width, height, Position(cop_x, cop_y), Position(thief_x, thief_y))
        self.last_message = ""
        return (
            f"{self.role} server reset with cop at ({cop_x},{cop_y}) "
            f"and thief at ({thief_x},{thief_y})."
        )

    def receive(self, message: str) -> str:
        self.last_message = message
        return f"{self.role} understood: {message}"

    def update_state(
        self,
        cop_x: int,
        cop_y: int,
        thief_x: int,
        thief_y: int,
        barriers: list[dict[str, int]] | None = None,
        cop_barriers_left: int = 5,
        turn_index: int = 0,
        captured: bool = False,
    ) -> str:
        width, height = self.config.grid_size
        self.state = GameState(
            width=width,
            height=height,
            cop=Position(cop_x, cop_y),
            thief=Position(thief_x, thief_y),
            barriers={
                Position(int(barrier["x"]), int(barrier["y"])) for barrier in (barriers or [])
            },
            cop_barriers_left=cop_barriers_left,
            turn_index=turn_index,
            captured=captured,
        )
        return f"{self.role} state updated for turn {turn_index}."

    def decide(self) -> dict[str, str]:
        if not self.state:
            self.state = self.engine.new_state()
        observation = self.state.visible_to(self.role, self.config.visibility_radius)
        action = self.brain.choose(observation, self.last_message)
        action = sanitize_action(self.state, action)
        return {"move": action.move.value, "message": action.message}
