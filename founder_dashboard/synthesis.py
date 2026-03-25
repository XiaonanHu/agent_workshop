from __future__ import annotations

import json
from dataclasses import asdict

import requests

from founder_dashboard.config import Settings
from founder_dashboard.models import DashboardBrief, LinearTicket


SYSTEM_PROMPT = """You are a founder operator coach.
Your output must be brutally concise and practical.
Given tickets, convo snippets, and founder notes, produce:
1) top_3_priorities (exactly 3 bullets)
2) biggest_product_issue (single sentence)
3) one_growth_action (single sentence, specific)
4) one_thing_to_ignore (single sentence)
5) rationale (short paragraph)

Return STRICT JSON with keys:
top_3_priorities, biggest_product_issue, one_growth_action, one_thing_to_ignore, rationale
"""


def build_dashboard_brief(
    settings: Settings,
    tickets: list[LinearTicket],
    conversation_blob: str,
    founder_notes: str,
) -> DashboardBrief:
    if settings.llm_api_key:
        return _call_llm(settings, tickets, conversation_blob, founder_notes)
    return _fallback_brief(tickets, conversation_blob, founder_notes)


def _call_llm(
    settings: Settings,
    tickets: list[LinearTicket],
    conversation_blob: str,
    founder_notes: str,
) -> DashboardBrief:
    provider = settings.llm_provider.strip().lower()
    if provider not in {"openai"}:
        # Keep scrappy: support one integration now, deterministic fallback otherwise.
        return _fallback_brief(tickets, conversation_blob, founder_notes)

    user_payload = {
        "linear_tickets": [asdict(t) for t in tickets[:20]],
        "yesterday_conversations": conversation_blob[:12000],
        "founder_notes": founder_notes[:8000],
    }
    body = {
        "model": settings.llm_model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ],
    }
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=body,
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    content = payload["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    return DashboardBrief(
        top_3_priorities=list(parsed.get("top_3_priorities", []))[:3],
        biggest_product_issue=str(parsed.get("biggest_product_issue", "")).strip(),
        one_growth_action=str(parsed.get("one_growth_action", "")).strip(),
        one_thing_to_ignore=str(parsed.get("one_thing_to_ignore", "")).strip(),
        rationale=str(parsed.get("rationale", "")).strip(),
    )


def _fallback_brief(
    tickets: list[LinearTicket],
    conversation_blob: str,
    founder_notes: str,
) -> DashboardBrief:
    priorities = []
    for ticket in tickets[:3]:
        priorities.append(f"{ticket.identifier}: {ticket.title}".strip(": "))

    while len(priorities) < 3:
        priorities.append("No high-signal ticket found - define one concrete objective now.")

    product_issue = "No clear product issue in logs; review top repeated complaint from yesterday."
    if conversation_blob:
        product_issue = (
            "Users signaled friction yesterday; inspect the most repeated blocker from conversation logs."
        )

    growth_action = "Reach out to 3 power users today and ask for one blocked workflow + willingness to demo."
    if founder_notes:
        growth_action = "Post one concrete product update and CTA tied to your latest founder notes."

    return DashboardBrief(
        top_3_priorities=priorities,
        biggest_product_issue=product_issue,
        one_growth_action=growth_action,
        one_thing_to_ignore="Low-leverage polish work that does not unblock users or distribution.",
        rationale="Filtered for immediate leverage across product risk, user signal, and distribution motion.",
    )
