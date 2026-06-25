from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .config import load_config
from .env_loader import load_dotenv
from .orchestrator import BonusMcpOrchestrator, LocalOrchestrator, RemoteMcpOrchestrator


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AI cops and robber game series.")
    parser.add_argument("--config", default="config.json", help="Path to the JSON configuration.")
    parser.add_argument("--print-report", action="store_true", help="Print the final JSON report.")
    parser.add_argument(
        "--remote-mcp",
        action="store_true",
        help="Run against cop_mcp_url and thief_mcp_url from the config.",
    )
    parser.add_argument(
        "--bonus-config",
        help="Run the inter-group bonus series from this JSON config.",
    )
    args = parser.parse_args()

    load_dotenv()
    config = load_config(args.config)
    if args.bonus_config:
        bonus_config = json.loads(Path(args.bonus_config).read_text(encoding="utf-8"))
        report = BonusMcpOrchestrator(config, bonus_config).run_series()
        report_path = Path("reports/bonus_game_report.json").resolve()
    elif args.remote_mcp:
        shared_token = os.environ.get("MCP_AUTH_TOKEN", "")
        report = RemoteMcpOrchestrator(
            config,
            cop_token=os.environ.get("COP_MCP_AUTH_TOKEN", shared_token),
            thief_token=os.environ.get("THIEF_MCP_AUTH_TOKEN", shared_token),
        ).run_series()
        report_path = Path("reports/internal_game_report.json").resolve()
    else:
        report = LocalOrchestrator(config).run_series()
        report_path = Path("reports/internal_game_report.json").resolve()
    if args.print_report:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Report written to {report_path}")


if __name__ == "__main__":
    main()
