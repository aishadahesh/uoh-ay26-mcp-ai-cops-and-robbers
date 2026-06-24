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
        self.brain.observe_message(message)
        return f"{self.role} understood: {message}"

    def decide(self) -> dict[str, str]:
        if not self.state:
            self.state = self.engine.new_state()
        observation = self.state.visible_to(self.role, self.config.visibility_radius)
        action = self.brain.choose(observation, self.last_message)
        action = sanitize_action(self.state, action)
        return {"move": action.move.value, "message": action.message}


def build_fastmcp_server(name: str, role: Role):
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError("Install project dependencies before starting MCP servers.") from exc

    server_state = AgentServerState(role)
    mcp = FastMCP(name)

    @mcp.tool()
    def reset_game(cop_x: int, cop_y: int, thief_x: int, thief_y: int) -> str:
        return server_state.reset(cop_x, cop_y, thief_x, thief_y)

    @mcp.tool()
    def receive_message(message: str) -> str:
        return server_state.receive(message)

    @mcp.tool()
    def choose_action() -> dict[str, str]:
        return server_state.decide()

    return mcp
