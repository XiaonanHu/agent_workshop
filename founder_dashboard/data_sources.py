from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import redis
import requests

from founder_dashboard.config import Settings
from founder_dashboard.models import LinearTicket


LINEAR_GRAPHQL_URL = "https://api.linear.app/graphql"


def fetch_linear_tickets(settings: Settings) -> list[LinearTicket]:
    """Fetch open Linear issues for a team, sorted by urgency-ish signal."""
    if not settings.linear_api_key:
        return []

    if settings.linear_team_id:
        query = """
        query TeamIssues($teamId: String!, $first: Int!) {
          issues(
            first: $first,
            filter: {
              team: { id: { eq: $teamId } }
              state: { type: { neq: "completed" } }
            },
            orderBy: updatedAt
          ) {
            nodes {
              id
              identifier
              title
              priority
              updatedAt
              url
              state { name }
            }
          }
        }
        """
        variables = {"teamId": settings.linear_team_id, "first": settings.linear_limit}
    else:
        query = """
        query WorkspaceIssues($first: Int!) {
          issues(
            first: $first,
            filter: {
              state: { type: { neq: "completed" } }
            },
            orderBy: updatedAt
          ) {
            nodes {
              id
              identifier
              title
              priority
              updatedAt
              url
              state { name }
            }
          }
        }
        """
        variables = {"first": settings.linear_limit}
    headers = {
        "Authorization": settings.linear_api_key,
        "Content-Type": "application/json",
    }

    response = requests.post(
        LINEAR_GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if "errors" in payload:
        raise RuntimeError(f"Linear API error: {payload['errors']}")

    nodes = payload.get("data", {}).get("issues", {}).get("nodes", [])
    tickets: list[LinearTicket] = []
    for node in nodes:
        tickets.append(
            LinearTicket(
                id=node.get("id", ""),
                identifier=node.get("identifier", ""),
                title=node.get("title", ""),
                priority=node.get("priority"),
                state=(node.get("state") or {}).get("name"),
                updated_at=node.get("updatedAt"),
                url=node.get("url"),
            )
        )
    return _sort_tickets_for_brief(tickets)


def _sort_tickets_for_brief(tickets: list[LinearTicket]) -> list[LinearTicket]:
    def score(ticket: LinearTicket) -> tuple[int, float]:
        priority_rank = 99 if ticket.priority is None else ticket.priority
        # Linear priority: 1 urgent, 2 high, ... so smaller is stronger.
        priority_component = priority_rank
        recency_component = 0.0
        if ticket.updated_at:
            try:
                dt = datetime.fromisoformat(ticket.updated_at.replace("Z", "+00:00"))
                recency_component = -dt.timestamp()
            except ValueError:
                recency_component = 0.0
        return priority_component, recency_component

    return sorted(tickets, key=score)


def fetch_yesterday_conversations(settings: Settings) -> str:
    """Get conversation summary blob from Redis first, fallback to local file."""
    redis_blob = _fetch_yesterday_conversations_from_redis(settings)
    if redis_blob:
        return redis_blob

    file_path = Path(settings.logs_file_path)
    if not file_path.exists():
        return ""
    return file_path.read_text(encoding="utf-8")


def _fetch_yesterday_conversations_from_redis(settings: Settings) -> str:
    if not settings.redis_url:
        return ""
    client = redis.from_url(settings.redis_url, decode_responses=True)

    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat()
    chunks: list[str] = []
    cursor = 0
    while True:
        cursor, keys = client.scan(cursor=cursor, match=settings.redis_key_pattern, count=200)
        for key in keys:
            value = client.get(key)
            if not value:
                continue
            if yesterday in key or yesterday in value:
                chunks.append(_normalize_redis_value(value))
        if cursor == 0:
            break
    return "\n".join(chunks).strip()


def _normalize_redis_value(value: str) -> str:
    try:
        parsed: Any = json.loads(value)
    except json.JSONDecodeError:
        return value
    return json.dumps(parsed, ensure_ascii=False)


def load_latest_founder_notes(settings: Settings) -> str:
    notes_dir = Path(settings.notes_dir)
    notes_dir.mkdir(parents=True, exist_ok=True)
    note_files = sorted(notes_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not note_files:
        return ""
    return note_files[0].read_text(encoding="utf-8")

