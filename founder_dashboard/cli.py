from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from founder_dashboard.agent import run_daily_dashboard
from founder_dashboard.config import load_settings
from founder_dashboard.output_targets import send_to_terminal


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Daily Founder Dashboard agent")
    parser.add_argument(
        "--notes-file",
        type=str,
        default=None,
        help="Optional markdown file for today's founder notes",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        dest="print_report",
        help="Print report to terminal",
    )
    return parser


def main() -> None:
    load_dotenv()
    args = _build_parser().parse_args()
    settings = load_settings()

    manual_notes: str | None = None
    if args.notes_file:
        notes_path = Path(args.notes_file)
        manual_notes = notes_path.read_text(encoding="utf-8") if notes_path.exists() else ""

    result = run_daily_dashboard(settings, manual_notes=manual_notes)

    if args.print_report:
        send_to_terminal(result.markdown)

    print(f"Saved report: {result.report_path}")
    if result.notion_url:
        print(f"Notion page: {result.notion_url}")
    if result.slack_sent:
        print("Slack: sent")
    for warning in result.warnings:
        print(f"Warning: {warning}")


if __name__ == "__main__":
    main()
