from __future__ import annotations

from datetime import date

from founder_dashboard.models import DashboardBrief, LinearTicket


def render_markdown_report(
    report_date: date,
    brief: DashboardBrief,
    tickets: list[LinearTicket],
    founder_notes: str,
) -> str:
    lines: list[str] = []
    lines.append(f"# Daily Founder Dashboard - {report_date.isoformat()}")
    lines.append("")
    lines.append("## Top 3 Priorities (Brutally Filtered)")
    for item in brief.top_3_priorities[:3]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Biggest Product Issue (From Yesterday)")
    lines.append(brief.biggest_product_issue)
    lines.append("")
    lines.append("## One Growth Action")
    lines.append(f"- {brief.one_growth_action}")
    lines.append("")
    lines.append("## One Thing to Ignore")
    lines.append(f"- {brief.one_thing_to_ignore}")
    lines.append("")
    lines.append("## Why This Stack of Priorities")
    lines.append(brief.rationale)
    lines.append("")
    lines.append("## Highest Priority Linear Tickets")
    if tickets:
        for t in tickets[:10]:
            parts = [
                t.identifier,
                t.title,
                f"(priority={t.priority})" if t.priority is not None else "",
                f"state={t.state}" if t.state else "",
            ]
            ticket_line = " ".join(part for part in parts if part).strip()
            if t.url:
                ticket_line = f"{ticket_line} - {t.url}"
            lines.append(f"- {ticket_line}")
    else:
        lines.append("- No tickets available (missing Linear config or no open issues).")
    lines.append("")
    lines.append("## Founder Notes Input")
    lines.append(founder_notes.strip() if founder_notes.strip() else "_No notes provided yet._")
    lines.append("")
    return "\n".join(lines)
