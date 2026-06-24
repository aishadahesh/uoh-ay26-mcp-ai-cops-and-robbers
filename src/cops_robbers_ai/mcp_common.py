from __future__ import annotations

import os
import time

from .action_policy import sanitize_action
from .config import load_config
from .engine import GameEngine
from .env_loader import load_dotenv
from .llm_agent import GeminiAgent
from .models import GameState, Position, Role


class StaticBearerTokenVerifier:
    def __init__(self, expected_token: str) -> None:
        self.expected_token = expected_token

    async def verify_token(self, token: str):
        if token != self.expected_token:
            return None

        from mcp.server.auth.provider import AccessToken

        return AccessToken(
            token=token,
            client_id="bonus-game-client",
            scopes=["mcp"],
            expires_at=int(time.time()) + 3600,
        )


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


def build_fastmcp_server(name: str, role: Role):
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError("Install project dependencies before starting MCP servers.") from exc

    load_dotenv()
    host = os.environ.get("MCP_HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", os.environ.get("MCP_PORT", "8000")))
    auth_token = os.environ.get("MCP_AUTH_TOKEN", "").strip()
    public_url = os.environ.get("MCP_PUBLIC_URL", f"http://{host}:{port}").strip()
    mcp_kwargs = {"host": host, "port": port}
    if auth_token:
        from mcp.server.auth.settings import AuthSettings

        mcp_kwargs["auth"] = AuthSettings(
            issuer_url=public_url,
            resource_server_url=public_url,
            required_scopes=["mcp"],
        )
        mcp_kwargs["token_verifier"] = StaticBearerTokenVerifier(auth_token)

    server_state = AgentServerState(role)
    mcp = FastMCP(name, **mcp_kwargs)

    @mcp.tool()
    def reset_game(cop_x: int, cop_y: int, thief_x: int, thief_y: int) -> str:
        return server_state.reset(cop_x, cop_y, thief_x, thief_y)

    @mcp.tool()
    def receive_message(message: str) -> str:
        return server_state.receive(message)

    @mcp.tool()
    def update_state(
        cop_x: int,
        cop_y: int,
        thief_x: int,
        thief_y: int,
        barriers: list[dict[str, int]] | None = None,
        cop_barriers_left: int = 5,
        turn_index: int = 0,
        captured: bool = False,
    ) -> str:
        return server_state.update_state(
            cop_x,
            cop_y,
            thief_x,
            thief_y,
            barriers,
            cop_barriers_left,
            turn_index,
            captured,
        )

    @mcp.tool()
    def choose_action() -> dict[str, str]:
        return server_state.decide()

    return mcp


def run_fastmcp_server(mcp) -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    mount_path = os.environ.get("MCP_MOUNT_PATH")
    if mount_path:
        mcp.run(transport=transport, mount_path=mount_path)
    else:
        mcp.run(transport=transport)
