from __future__ import annotations

import json
from pathlib import Path

import requests

from founder_dashboard.config import Settings


def save_local_report(settings: Settings, markdown_report: str, filename: str) -> Path:
    reports_dir = Path(settings.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    target = reports_dir / filename
    target.write_text(markdown_report, encoding="utf-8")
    return target


def send_to_terminal(markdown_report: str) -> None:
    print(markdown_report)


def create_notion_page(settings: Settings, title: str, markdown_report: str) -> str | None:
    """Create a Notion page under the configured parent page."""
    if not settings.notion_token or not settings.notion_parent_page_id:
        return None

    # Minimal conversion: preserve readability in a single paragraph block payload.
    # Scrappy by design; easy to swap with richer markdown-to-block conversion later.
    lines = markdown_report.splitlines()
    blocks = []
    for line in lines:
        if not line.strip():
            continue
        blocks.append(
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": line[:1800]}}],
                },
            }
        )

    payload = {
        "parent": {"type": "page_id", "page_id": settings.notion_parent_page_id},
        "properties": {
            "title": {
                "title": [{"type": "text", "text": {"content": title[:200]}}],
            }
        },
        "children": blocks[:100],
    }
    headers = {
        "Authorization": f"Bearer {settings.notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        data=json.dumps(payload),
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("url")


def send_to_slack(settings: Settings, markdown_report: str) -> bool:
    if not settings.slack_bot_token or not settings.slack_channel:
        return False
    headers = {
        "Authorization": f"Bearer {settings.slack_bot_token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    payload = {"channel": settings.slack_channel, "text": markdown_report[:35000]}
    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers=headers,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return bool(data.get("ok"))
