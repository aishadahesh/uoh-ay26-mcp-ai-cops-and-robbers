from __future__ import annotations

import asyncio
import json

from .action_policy import sanitize_action
from .config import GameConfig
from .engine import GameEngine
from .llm_agent import GeminiAgent
from .models import Action, Move, Role
from .reporting import build_report, send_report_email, write_report


class LocalOrchestrator:
    def __init__(self, config: GameConfig) -> None:
        self.config = config

    def run_series(self) -> dict[str, object]:
        sub_games = [self._run_one(index) for index in range(1, self.config.num_games + 1)]
        report = build_report(self.config, sub_games)
        write_report(report)
        send_report_email(self.config, report)
        return report

    def _run_one(self, index: int) -> dict[str, object]:
        engine = GameEngine(self.config, seed_offset=index)
        state = engine.new_state()
        cop = GeminiAgent("cop", self.config.llm)
        thief = GeminiAgent("thief", self.config.llm)
        inbox = {"cop": "", "thief": ""}
        turns: list[dict[str, object]] = []

        while not engine.result_for(state):
            role = "thief" if state.turn_index % 2 == 0 else "cop"
            brain = thief if role == "thief" else cop
            observation = state.visible_to(role, self.config.visibility_radius)
            action = brain.choose(observation, inbox[role])
            action = sanitize_action(state, action)
            engine.apply(state, action)
            inbox["cop" if role == "thief" else "thief"] = action.message
            turns.append(
                {
                    "role": role,
                    "move": action.move.value,
                    "message": action.message,
                    "state": engine.snapshot(state),
                }
            )

        result = engine.result_for(state) or "technical_loss"
        return {
            "sub_game_id": index,
            "result": result,
            "moves": len(turns),
            "score": engine.score(result),
            "turns": turns,
        }


class RemoteMcpAgent:
    def __init__(self, role: Role, url: str, token: str = "") -> None:
        self.role = role
        self.url = url
        self.token = token
        self._session = None
        self._client_context = None
        self._session_context = None

    async def __aenter__(self) -> RemoteMcpAgent:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client

        headers = {"Authorization": f"Bearer {self.token}"} if self.token else None
        self._client_context = streamablehttp_client(self.url, headers=headers)
        read, write, _ = await self._client_context.__aenter__()
        self._session_context = ClientSession(read, write)
        self._session = await self._session_context.__aenter__()
        await self._session.initialize()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._session_context:
            await self._session_context.__aexit__(exc_type, exc, tb)
        if self._client_context:
            await self._client_context.__aexit__(exc_type, exc, tb)

    async def reset(self, cop_x: int, cop_y: int, thief_x: int, thief_y: int) -> None:
        await self._call(
            "reset_game",
            {"cop_x": cop_x, "cop_y": cop_y, "thief_x": thief_x, "thief_y": thief_y},
        )

    async def update_state(self, state) -> None:
        await self._call(
            "update_state",
            {
                "cop_x": state.cop.x,
                "cop_y": state.cop.y,
                "thief_x": state.thief.x,
                "thief_y": state.thief.y,
                "barriers": [{"x": p.x, "y": p.y} for p in state.barriers],
                "cop_barriers_left": state.cop_barriers_left,
                "turn_index": state.turn_index,
                "captured": state.captured,
            },
        )

    async def receive_message(self, message: str) -> None:
        await self._call("receive_message", {"message": message})

    async def choose_action(self) -> Action:
        result = await self._call("choose_action", {})
        data = self._result_data(result)
        move = Move(data.get("move", Move.STAY.value))
        return Action(self.role, move, str(data.get("message", "")))

    async def _call(self, tool_name: str, arguments: dict[str, object]):
        if self._session is None:
            raise RuntimeError("Remote MCP session is not initialized.")
        result = await self._session.call_tool(tool_name, arguments=arguments)
        if result.isError:
            raise RuntimeError(f"{self.role} MCP tool {tool_name} failed: {result.content}")
        return result

    @staticmethod
    def _result_data(result) -> dict[str, object]:
        if result.structuredContent:
            return result.structuredContent
        if not result.content:
            return {}
        first = result.content[0]
        text = getattr(first, "text", "")
        if not text:
            return {}
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}


class RemoteMcpOrchestrator:
    def __init__(
        self,
        config: GameConfig,
        cop_token: str = "",
        thief_token: str = "",
    ) -> None:
        self.config = config
        self.cop_token = cop_token
        self.thief_token = thief_token

    def run_series(self) -> dict[str, object]:
        return asyncio.run(self._run_series())

    async def _run_series(self) -> dict[str, object]:
        sub_games = [await self._run_one(index) for index in range(1, self.config.num_games + 1)]
        report = build_report(self.config, sub_games)
        write_report(report)
        send_report_email(self.config, report)
        return report

    async def _run_one(self, index: int) -> dict[str, object]:
        engine = GameEngine(self.config, seed_offset=index)
        state = engine.new_state()
        inbox = {"cop": "", "thief": ""}
        turns: list[dict[str, object]] = []

        async with (
            RemoteMcpAgent("cop", self.config.cop_mcp_url, self.cop_token) as cop,
            RemoteMcpAgent("thief", self.config.thief_mcp_url, self.thief_token) as thief,
        ):
            await cop.reset(state.cop.x, state.cop.y, state.thief.x, state.thief.y)
            await thief.reset(state.cop.x, state.cop.y, state.thief.x, state.thief.y)

            while not engine.result_for(state):
                role = "thief" if state.turn_index % 2 == 0 else "cop"
                agent = thief if role == "thief" else cop
                await agent.update_state(state)
                await agent.receive_message(inbox[role])
                action = await agent.choose_action()
                action = sanitize_action(state, action)
                engine.apply(state, action)
                inbox["cop" if role == "thief" else "thief"] = action.message
                turns.append(
                    {
                        "role": role,
                        "move": action.move.value,
                        "message": action.message,
                        "state": engine.snapshot(state),
                    }
                )

        result = engine.result_for(state) or "technical_loss"
        return {
            "sub_game_id": index,
            "result": result,
            "moves": len(turns),
            "score": engine.score(result),
            "turns": turns,
        }
