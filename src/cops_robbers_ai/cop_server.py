from __future__ import annotations

from .mcp_common import build_fastmcp_server, run_fastmcp_server

mcp = build_fastmcp_server("cop-agent", "cop")


if __name__ == "__main__":
    run_fastmcp_server(mcp)
