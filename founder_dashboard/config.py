from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    # Core
    llm_provider: str
    llm_api_key: str | None
    llm_model: str

    # Linear
    linear_api_key: str | None
    linear_team_id: str | None
    linear_limit: int

    # Conversations (redis or file)
    redis_url: str | None
    redis_key_pattern: str
    logs_file_path: str

    # Notes
    notes_dir: str

    # Outputs
    reports_dir: str
    notion_token: str | None
    notion_parent_page_id: str | None
    slack_bot_token: str | None
    slack_channel: str | None

    # Behavior
    dry_run: bool

    @property
    def today(self) -> date:
        return date.today()


def load_settings() -> Settings:
    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER", "openai"),
        llm_api_key=os.getenv("LLM_API_KEY"),
        llm_model=os.getenv("LLM_MODEL", "gpt-4.1"),
        linear_api_key=os.getenv("LINEAR_API_KEY"),
        linear_team_id=os.getenv("LINEAR_TEAM_ID"),
        linear_limit=int(os.getenv("LINEAR_LIMIT", "25")),
        redis_url=os.getenv("REDIS_URL"),
        redis_key_pattern=os.getenv("REDIS_KEY_PATTERN", "conversation:*"),
        logs_file_path=os.getenv("LOGS_FILE_PATH", "data/conversations_yesterday.txt"),
        notes_dir=os.getenv("NOTES_DIR", "notes"),
        reports_dir=os.getenv("REPORTS_DIR", "reports"),
        notion_token=os.getenv("NOTION_TOKEN"),
        notion_parent_page_id=os.getenv("NOTION_PARENT_PAGE_ID"),
        slack_bot_token=os.getenv("SLACK_BOT_TOKEN"),
        slack_channel=os.getenv("SLACK_CHANNEL"),
        dry_run=_bool_env("DRY_RUN", default=False),
    )
