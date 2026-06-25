from __future__ import annotations

import time


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
