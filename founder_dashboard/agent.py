from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from founder_dashboard.config import Settings
from founder_dashboard.data_sources import (
    fetch_linear_tickets,
    fetch_yesterday_conversations,
    load_latest_founder_notes,
)
from founder_dashboard.models import DashboardBrief, LinearTicket
from founder_dashboard.output_targets import create_notion_page, save_local_report, send_to_slack
from founder_dashboard.rendering import render_markdown_report
from founder_dashboard.synthesis import build_dashboard_brief


@dataclass
class RunResult:
    report_path: Path
    markdown: str
    brief: DashboardBrief
    tickets: list[LinearTicket]
    notion_url: str | None
    slack_sent: bool
    report_date: date
    warnings: list[str]


def run_daily_dashboard(settings: Settings, manual_notes: str | None = None) -> RunResult:
    tickets = fetch_linear_tickets(settings)
    conversation_blob = fetch_yesterday_conversations(settings)
    founder_notes = manual_notes if manual_notes is not None else load_latest_founder_notes(settings)

    brief = build_dashboard_brief(
        settings=settings,
        tickets=tickets,
        conversation_blob=conversation_blob,
        founder_notes=founder_notes,
    )
    report_date = settings.today
    markdown = render_markdown_report(
        report_date=report_date,
        brief=brief,
        tickets=tickets,
        founder_notes=founder_notes,
    )

    filename = f"founder_dashboard_{report_date.isoformat()}.md"
    report_path = save_local_report(settings, markdown, filename)

    notion_url: str | None = None
    slack_sent = False
    warnings: list[str] = []
    if not settings.dry_run:
        try:
            notion_url = create_notion_page(
                settings=settings,
                title=f"Daily Founder Dashboard - {report_date.isoformat()}",
                markdown_report=markdown,
            )
        except Exception as exc:  # pragma: no cover - network and credential dependent
            warnings.append(f"Notion publish failed: {exc}")
        try:
            slack_sent = send_to_slack(settings, markdown)
        except Exception as exc:  # pragma: no cover - network and credential dependent
            warnings.append(f"Slack publish failed: {exc}")

    return RunResult(
        report_path=report_path,
        markdown=markdown,
        brief=brief,
        tickets=tickets,
        notion_url=notion_url,
        slack_sent=slack_sent,
        report_date=report_date,
        warnings=warnings,
    )
