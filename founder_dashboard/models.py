from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LinearTicket:
    id: str
    identifier: str
    title: str
    priority: int | None
    state: str | None
    updated_at: str | None
    url: str | None


@dataclass
class DashboardBrief:
    top_3_priorities: list[str]
    biggest_product_issue: str
    one_growth_action: str
    one_thing_to_ignore: str
    rationale: str

