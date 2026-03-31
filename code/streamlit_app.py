#!/usr/bin/env python3
"""Interactive Streamlit app for the Productivity Automation Agent.

Provides a standalone UI where users can:
  1. Select or upload workspace scenarios
  2. Watch the Bedrock agent analyse data in real-time
  3. Inspect detected patterns and cross-referenced insights
  4. Review ranked automation proposals
  5. Approve / reject proposals interactively
  6. Browse the full audit trail

Launch via Code Ocean Streamlit cloud workstation.
"""

from __future__ import annotations

import json
import sys
import time
from io import StringIO
from pathlib import Path

import streamlit as st

# Ensure /code is on the path so we can import our modules
sys.path.insert(0, "/code")

from bedrock_agent import AuditLog, run_agent  # noqa: E402
from scenarios import SCENARIOS, load_scenario  # noqa: E402

st.set_page_config(
    page_title="⚡ Productivity Automation Agent",
    page_icon="⚡",
    layout="wide",
)


def main() -> None:
    st.title("⚡ Productivity Automation Agent")
    st.markdown(
        "Agentic productivity analyser powered by **AWS Bedrock** (Anthropic Claude).  "
        "Select a scenario or upload your own data, then let the agent detect patterns "
        "and propose automations."
    )

    # ── Sidebar: data source ──────────────────────────────────────
    st.sidebar.header("📂 Data Source")
    source = st.sidebar.radio(
        "Choose input source",
        ["Built-in Scenario", "Upload Custom JSON"],
    )

    calendar: list[dict] = []
    emails: list[dict] = []
    scenario_label = ""

    if source == "Built-in Scenario":
        scenario_key = st.sidebar.selectbox(
            "Select scenario",
            list(SCENARIOS.keys()),
            format_func=lambda k: SCENARIOS[k]["name"],
        )
        scenario_label = SCENARIOS[scenario_key]["name"]
        st.sidebar.markdown(f"*{SCENARIOS[scenario_key]['description']}*")
        calendar, emails = load_scenario(scenario_key)
    else:
        cal_file = st.sidebar.file_uploader("Calendar Events JSON", type="json")
        email_file = st.sidebar.file_uploader("Email Threads JSON", type="json")
        if cal_file and email_file:
            calendar = json.load(StringIO(cal_file.read().decode()))
            emails = json.load(StringIO(email_file.read().decode()))
            scenario_label = "Custom Upload"

    if not calendar or not emails:
        st.info("👈 Select a scenario or upload data to begin.")
        return

    # ── Data preview ──────────────────────────────────────────────
    with st.expander(f"📊 Data Preview — {scenario_label}", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Calendar Events", len(calendar))
            st.json(calendar[:3])
        with col2:
            st.metric("Email Threads", len(emails))
            st.json(emails[:3])

    # ── Run agent ─────────────────────────────────────────────────
    st.divider()

    if st.button("🤖 Run Agent Analysis", type="primary", use_container_width=True):
        with st.spinner("Agent is analysing your workspace data..."):
            audit = AuditLog()
            t0 = time.time()
            output = run_agent(calendar, emails, audit)
            elapsed = round(time.time() - t0, 2)

        st.session_state["agent_output"] = output
        st.session_state["audit_log"] = audit.entries
        st.session_state["elapsed"] = elapsed
        st.session_state["approvals"] = {}

    if "agent_output" not in st.session_state:
        return

    output = st.session_state["agent_output"]
    audit_entries = st.session_state["audit_log"]
    elapsed = st.session_state["elapsed"]

    # ── Results ───────────────────────────────────────────────────
    st.success(f"Analysis complete in **{elapsed}s**")

    # Summary
    st.subheader("📋 Analysis Summary")
    st.markdown(output.get("analysis_summary", "No summary available."))

    # Patterns
    st.subheader("🔍 Detected Patterns")
    patterns = output.get("patterns_detected", [])
    if patterns:
        for i, p in enumerate(patterns):
            sev = p.get("severity", "info")
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(sev, "ℹ️")
            st.markdown(f"{icon} **{p.get('type', 'pattern')}** — {p.get('detail', '')}")
    else:
        st.info("No patterns detected.")

    # Proposals
    st.subheader("💡 Automation Proposals")
    proposals = output.get("proposals", [])

    if not proposals:
        st.info("No proposals generated.")
    else:
        for p in proposals:
            rank = p.get("rank", "")
            risk_color = {"low": "green", "medium": "orange", "high": "red"}.get(
                p.get("risk_level", ""), "gray"
            )
            with st.container():
                col_main, col_action = st.columns([4, 1])
                with col_main:
                    st.markdown(f"### #{rank}: {p.get('description', '')}")
                    st.markdown(f"**Rationale:** {p.get('rationale', '')}")
                    st.markdown(f"**Risk:** :{risk_color}[{p.get('risk_level', '?')}]  "
                                f"| **Time saved:** {p.get('estimated_time_saved_weekly', '?')}")
                    if p.get("data_used"):
                        st.caption(f"Data: {', '.join(p['data_used'])}")
                with col_action:
                    key = f"approve_{rank}"
                    current = st.session_state.get("approvals", {}).get(key, None)
                    if st.button("✅ Approve", key=f"btn_approve_{rank}"):
                        st.session_state.setdefault("approvals", {})[key] = "approved"
                        st.rerun()
                    if st.button("❌ Reject", key=f"btn_reject_{rank}"):
                        st.session_state.setdefault("approvals", {})[key] = "rejected"
                        st.rerun()
                    if current:
                        st.markdown(f"**Status:** {current}")
                st.divider()

    # Approval summary
    approvals = st.session_state.get("approvals", {})
    if approvals:
        st.subheader("📌 Approval Summary")
        for k, v in approvals.items():
            icon = "✅" if v == "approved" else "❌"
            st.markdown(f"{icon} Proposal {k.split('_')[-1]}: **{v}**")

    # Audit trail
    with st.expander("📜 Full Audit Trail", expanded=False):
        for entry in audit_entries:
            ts = entry.get("timestamp", "")[:19]
            st.text(f"[{ts}] {entry.get('step', '')}: {entry.get('detail', '')}")

    # Raw output
    with st.expander("🔧 Raw Agent Output (JSON)", expanded=False):
        st.json(output)


if __name__ == "__main__":
    main()
