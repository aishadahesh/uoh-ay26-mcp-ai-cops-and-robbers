from __future__ import annotations

import json
import os

from .config import LlmConfig
from .models import Action, Move, Role
from .strategy import AgentBrain


class GeminiAgent:
    def __init__(self, role: Role, config: LlmConfig, provider: str | None = None) -> None:
        self.role = role
        self.config = config
        self.provider = (provider or config.provider).lower()
        self.fallback = AgentBrain(role)

    def choose(self, observation: dict[str, object], inbound_message: str) -> Action:
        if self.provider == "heuristic":
            return self.fallback.choose(observation, inbound_message)
        try:
            if self.provider == "gemini":
                return self._choose_with_gemini(observation, inbound_message)
            if self.provider == "openai":
                return self._choose_with_openai(observation, inbound_message)
            return self.fallback.choose(observation, inbound_message)
        except Exception:
            if self.config.fallback_to_heuristic:
                return self.fallback.choose(observation, inbound_message)
            raise

    def _choose_with_gemini(self, observation: dict[str, object], inbound_message: str) -> Action:
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("Set GEMINI_API_KEY or GOOGLE_API_KEY to use Gemini agents.")
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        prompt = self._prompt(observation, inbound_message)
        response = client.models.generate_content(
            model=self.config.gemini_model or self.config.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=self.config.temperature,
                response_mime_type="application/json",
            ),
        )
        payload = json.loads(response.text or "{}")
        return self._action_from_payload(payload)

    def _choose_with_openai(self, observation: dict[str, object], inbound_message: str) -> Action:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Set OPENAI_API_KEY to use OpenAI agents.")
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=self.config.openai_model,
            messages=[
                {"role": "system", "content": "Return only valid JSON with keys: move, message."},
                {"role": "user", "content": self._prompt(observation, inbound_message)},
            ],
            temperature=self.config.temperature,
            response_format={"type": "json_object"},
        )
        payload = json.loads(response.choices[0].message.content or "{}")
        return self._action_from_payload(payload)

    def _action_from_payload(self, payload: dict[str, object]) -> Action:
        move = Move(str(payload.get("move", "stay")).lower())
        message = str(payload.get("message", "")).strip() or f"{self.role} chooses {move.value}."
        return Action(self.role, move, message)

    def _prompt(self, observation: dict[str, object], inbound_message: str) -> str:
        moves = [move.value for move in Move if move != Move.STAY]
        return (
            f"You are the {self.role} agent in a partially observable cops-and-robber grid game.\n"
            f"Valid moves: {moves}. Do not choose 'stay'. Only the cop may use 'barrier'.\n"
            "Return only JSON with keys: move, message.\n"
            "The message must be natural language for the other agent and may include your own "
            "position, intent, or a strategic hint. Keep it one sentence.\n"
            f"Observation: {json.dumps(observation, ensure_ascii=False)}\n"
            f"Incoming message: {inbound_message!r}\n"
        )
