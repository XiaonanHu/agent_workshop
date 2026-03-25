from __future__ import annotations

from dotenv import load_dotenv

from founder_dashboard.agent import run_daily_dashboard
from founder_dashboard.config import load_settings


def main() -> None:
    """Entry point intended for cron/systemd invocation."""
    load_dotenv()
    settings = load_settings()
    result = run_daily_dashboard(settings=settings)
    print(f"Saved report: {result.report_path}")
    if result.notion_url:
        print(f"Notion page: {result.notion_url}")
    if result.slack_sent:
        print("Slack: sent")
    for warning in result.warnings:
        print(f"Warning: {warning}")


if __name__ == "__main__":
    main()
