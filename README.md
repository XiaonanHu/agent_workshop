# Daily Founder Dashboard Agent

Scrappy daily agent that produces a founder dashboard every morning:

- Top 3 priorities (brutally filtered)
- Biggest product issue from yesterday's conversations
- One growth action
- One thing to ignore

Inputs:

- Linear (open tickets)
- Redis or local logs (yesterday conversations)
- Founder notes (manual input)

Outputs:

- Local markdown report (`reports/`)
- Optional Notion page
- Optional Slack post
- Terminal print

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Set your `.env` values:

- `LINEAR_API_KEY`, `LINEAR_TEAM_ID`
- `LLM_API_KEY` (+ optional `LLM_MODEL`)
- Optional: `REDIS_URL`, `NOTION_TOKEN`, `NOTION_PARENT_PAGE_ID`, `SLACK_BOT_TOKEN`, `SLACK_CHANNEL`

Then run:

```bash
founder-dashboard --print
```

This creates `reports/founder_dashboard_YYYY-MM-DD.md`.

## Notes input window (your thoughts/suggestions)

If you want a simple input window:

```bash
pip install -e ".[ui]"
streamlit run founder_dashboard/notes_ui.py
```

Use the textarea to capture your thoughts, then click **Generate dashboard now**.
It saves notes to `notes/` and generates today's dashboard.

## Scheduling (every morning)

Use cron (example 8:00 AM):

```bash
0 8 * * * cd /workspace && /workspace/.venv/bin/founder-dashboard-scheduled >> /workspace/reports/cron.log 2>&1
```

## Data contract details

- Linear:
  - Pulls non-completed issues for `LINEAR_TEAM_ID`
  - Sorts by priority + recency
- Conversations:
  - Tries Redis keys matching `REDIS_KEY_PATTERN`, filtered to yesterday
  - Falls back to `LOGS_FILE_PATH`
- LLM:
  - Single model call with strict JSON output schema
  - If no API key, deterministic fallback summary is generated

## Clarifications needed from you

To finalize this for your exact workflow, confirm:

1. Which output is primary each day: **Notion only**, or **Notion + Slack**?
2. Is your Linear scope one team (`LINEAR_TEAM_ID`) or multiple teams/projects?
3. What format are your conversation logs in Redis (key/value shape)?
4. Do you want the Notion output as:
   - a page under a parent page (current implementation), or
   - rows in a Notion database?
