from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import load_config
from .env_loader import load_dotenv
from .orchestrator import LocalOrchestrator


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AI cops and robber game series.")
    parser.add_argument("--config", default="config.json", help="Path to the JSON configuration.")
    parser.add_argument("--print-report", action="store_true", help="Print the final JSON report.")
    args = parser.parse_args()

    load_dotenv()
    config = load_config(args.config)
    report = LocalOrchestrator(config).run_series()
    report_path = Path("reports/internal_game_report.json").resolve()
    if args.print_report:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Report written to {report_path}")


if __name__ == "__main__":
    main()
