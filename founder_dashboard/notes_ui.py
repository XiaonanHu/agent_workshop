from __future__ import annotations

from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from founder_dashboard.agent import run_daily_dashboard
from founder_dashboard.config import load_settings


def _save_note(notes_dir: str, content: str) -> Path:
    base = Path(notes_dir)
    base.mkdir(parents=True, exist_ok=True)
    name = datetime.now().strftime("%Y-%m-%d_%H%M%S_founder_note.md")
    target = base / name
    target.write_text(content.strip() + "\n", encoding="utf-8")
    return target


def main() -> None:
    load_dotenv()
    settings = load_settings()

    st.set_page_config(page_title="Founder Dashboard Agent", layout="wide")
    st.title("Daily Founder Dashboard Agent")
    st.caption("CEO coach + product lead + growth advisor, scrappy mode.")

    notes = st.text_area(
        "Input your thoughts / suggestions for today's run",
        height=240,
        placeholder="Write raw thoughts, user feedback, concerns, or focus areas...",
    )

    col1, col2 = st.columns(2)
    with col1:
        save_note = st.button("Save note only", use_container_width=True)
    with col2:
        run_agent = st.button("Generate dashboard now", type="primary", use_container_width=True)

    if save_note:
        path = _save_note(settings.notes_dir, notes)
        st.success(f"Saved note: {path}")

    if run_agent:
        path = _save_note(settings.notes_dir, notes)
        result = run_daily_dashboard(settings=settings, manual_notes=notes)
        st.success(f"Report generated: {result.report_path}")
        if result.notion_url:
            st.info(f"Notion page: {result.notion_url}")
        if result.slack_sent:
            st.info("Slack message sent.")
        for warning in result.warnings:
            st.warning(warning)
        st.markdown("---")
        st.markdown(result.markdown)
        st.caption(f"Notes captured in: {path}")


if __name__ == "__main__":
    main()
