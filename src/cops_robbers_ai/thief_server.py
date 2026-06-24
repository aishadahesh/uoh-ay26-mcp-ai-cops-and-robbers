from __future__ import annotations

from .mcp_common import build_fastmcp_server

mcp = build_fastmcp_server("thief-agent", "thief")


if __name__ == "__main__":
    mcp.run()
