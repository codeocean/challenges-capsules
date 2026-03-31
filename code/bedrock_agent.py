#!/usr/bin/env python3
"""Agentic productivity analyser powered by AWS Bedrock (Anthropic Claude).

Implements a genuine tool-use agent loop:
  1. Agent receives workspace data + tool definitions
  2. Agent autonomously decides which tool to invoke and in what order
  3. Tool executes (pure-Python heuristics in tools.py)
  4. Agent receives tool output and decides next action
  5. Repeat until agent produces its final structured output

All LLM calls go through boto3 bedrock-runtime invoke_model.
Falls back to a deterministic heuristic pipeline when Bedrock is
unavailable (no AWS credentials / network issues).
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import tools as tool_module

# ── Configuration ────────────────────────────────────────────────────────

MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID",
    "us.anthropic.claude-sonnet-4-20250514-v1:0",
)
AWS_REGION = os.environ.get(
    "AWS_REGION",
    os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
)
MAX_AGENT_TURNS = 12  # safety limit


# ── Bedrock tool definitions ────────────────────────────────────────────

TOOL_DEFS = [
    {
        "name": "scan_calendar_load",
        "description": (
            "Analyse calendar events and compute per-day meeting-load "
            "statistics. Returns overloaded days (>5 h), daily totals, "
            "and overall average. Input: the literal string 'calendar'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": "Must be 'calendar'",
                }
            },
            "required": ["target"],
        },
    },
    {
        "name": "scan_calendar_back_to_back",
        "description": (
            "Identify back-to-back meetings with no gap between them. "
            "Input: the literal string 'calendar'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Must be 'calendar'"}
            },
            "required": ["target"],
        },
    },
    {
        "name": "scan_calendar_recurring",
        "description": (
            "Find recurring meetings with high decline/tentative rates. "
            "Input: the literal string 'calendar'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Must be 'calendar'"}
            },
            "required": ["target"],
        },
    },
    {
        "name": "scan_calendar_focus_time",
        "description": (
            "Estimate available focus-block time (>=2 h uninterrupted). "
            "Input: the literal string 'calendar'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Must be 'calendar'"}
            },
            "required": ["target"],
        },
    },
    {
        "name": "scan_email_stale",
        "description": (
            "Find email threads awaiting reply for >7 days. "
            "Input: the literal string 'emails'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Must be 'emails'"}
            },
            "required": ["target"],
        },
    },
    {
        "name": "scan_email_long_chains",
        "description": (
            "Find email threads with >10 messages (FYI chains). "
            "Input: the literal string 'emails'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Must be 'emails'"}
            },
            "required": ["target"],
        },
    },
    {
        "name": "scan_email_volume",
        "description": (
            "Summarise email volume: total threads, awaiting-reply count, "
            "priority breakdown. Input: the literal string 'emails'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Must be 'emails'"}
            },
            "required": ["target"],
        },
    },
    {
        "name": "cross_reference",
        "description": (
            "Synthesise insights across ALL previously collected calendar "
            "and email analysis results. Call this AFTER running the other "
            "tools. Input: the literal string 'all'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Must be 'all'"}
            },
            "required": ["target"],
        },
    },
]

SYSTEM_PROMPT = """\
You are an expert productivity analyst agent. You have access to tools that
analyse calendar events and email threads from a user's workspace.

Your task:
1. Use the available tools to thoroughly analyse the workspace data.
   Call each relevant tool to gather a complete picture.
2. After gathering all data, call the cross_reference tool to synthesise.
3. Finally, produce your output as a JSON object with this structure:

{
  "analysis_summary": "2-3 sentence overall assessment",
  "patterns_detected": [
    {"type": "...", "severity": "high|medium|low", "detail": "..."}
  ],
  "proposals": [
    {
      "rank": 1,
      "description": "Concrete, actionable automation proposal",
      "rationale": "Why this matters, grounded in detected patterns",
      "data_used": ["which tool results support this"],
      "risk_level": "low|medium|high",
      "estimated_time_saved_weekly": "e.g. 3 hours"
    }
  ]
}

Generate 3-5 proposals, ranked by impact. Be specific and grounded in the data.
Do NOT invent patterns not found by the tools. Cite the tool outputs.
"""


# ── Audit logger ────────────────────────────────────────────────────────

class AuditLog:
    """Append-only JSONL audit log."""

    def __init__(self) -> None:
        self._entries: list[dict] = []

    def log(self, step: str, detail: str, data: dict | None = None) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "step": step,
            "detail": detail,
        }
        if data:
            entry["data"] = data
        self._entries.append(entry)
        print(f"  [audit] {step}: {detail}")

    @property
    def entries(self) -> list[dict]:
        return list(self._entries)

    def flush(self, path: Path) -> None:
        with open(path, "w") as f:
            for e in self._entries:
                f.write(json.dumps(e) + "\n")


# ── Bedrock invocation ──────────────────────────────────────────────────

def _get_bedrock_client():
    """Return a boto3 bedrock-runtime client."""
    import boto3
    return boto3.client("bedrock-runtime", region_name=AWS_REGION)


def _invoke_bedrock(client, messages: list[dict], system: str,
                    tool_defs: list[dict]) -> dict:
    """Single invoke_model call using Anthropic Messages API on Bedrock."""
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "system": system,
        "messages": messages,
        "tools": tool_defs,
    }
    resp = client.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )
    return json.loads(resp["body"].read())


# ── Tool execution ──────────────────────────────────────────────────────

def _execute_tool(
    name: str,
    tool_input: dict,
    calendar: list[dict],
    emails: list[dict],
    collected: dict[str, Any],
) -> Any:
    """Run the named tool and return its result dict."""
    if name == "scan_calendar_load":
        result = tool_module.scan_calendar_load(calendar)
    elif name == "scan_calendar_back_to_back":
        result = tool_module.scan_calendar_back_to_back(calendar)
    elif name == "scan_calendar_recurring":
        result = tool_module.scan_calendar_recurring(calendar)
    elif name == "scan_calendar_focus_time":
        result = tool_module.scan_calendar_focus_time(calendar)
    elif name == "scan_email_stale":
        result = tool_module.scan_email_stale(emails)
    elif name == "scan_email_long_chains":
        result = tool_module.scan_email_long_chains(emails)
    elif name == "scan_email_volume":
        result = tool_module.scan_email_volume(emails)
    elif name == "cross_reference":
        result = tool_module.cross_reference(
            collected.get("scan_calendar_load", {}),
            collected.get("scan_calendar_back_to_back", {}),
            collected.get("scan_calendar_recurring", {}),
            collected.get("scan_calendar_focus_time", {}),
            collected.get("scan_email_stale", {}),
            collected.get("scan_email_long_chains", {}),
            collected.get("scan_email_volume", {}),
        )
    else:
        result = {"error": f"Unknown tool: {name}"}
    return result


# ── Agent loop (Bedrock) ────────────────────────────────────────────────

def run_agent_bedrock(
    calendar: list[dict],
    emails: list[dict],
    audit: AuditLog,
) -> dict:
    """Run the agentic loop using Bedrock tool-use. Returns final output."""
    client = _get_bedrock_client()

    user_message = (
        f"Analyse this workspace data and generate productivity automation "
        f"proposals.\n\n"
        f"Calendar events ({len(calendar)} events):\n"
        f"{json.dumps(calendar[:5])}... (truncated, use tools to scan all)\n\n"
        f"Email threads ({len(emails)} threads):\n"
        f"{json.dumps(emails[:3])}... (truncated, use tools to scan all)\n\n"
        f"Use ALL available tools to analyse the full dataset, then cross-reference, "
        f"then produce your final JSON output."
    )

    messages: list[dict] = [{"role": "user", "content": user_message}]
    collected: dict[str, Any] = {}

    audit.log("agent_start", f"Starting Bedrock agent loop (model={MODEL_ID})")

    for turn in range(1, MAX_AGENT_TURNS + 1):
        audit.log("agent_turn", f"Turn {turn}: calling Bedrock")
        t0 = time.time()
        result = _invoke_bedrock(client, messages, SYSTEM_PROMPT, TOOL_DEFS)
        elapsed = round(time.time() - t0, 2)

        stop_reason = result.get("stop_reason", "")
        content_blocks = result.get("content", [])
        audit.log("bedrock_response", f"stop_reason={stop_reason}, latency={elapsed}s",
                  {"turn": turn, "stop_reason": stop_reason})

        # Build assistant message from content blocks
        assistant_content = []
        tool_uses: list[dict] = []
        final_text = ""

        for block in content_blocks:
            if block.get("type") == "text":
                final_text += block["text"]
                assistant_content.append(block)
            elif block.get("type") == "tool_use":
                tool_uses.append(block)
                assistant_content.append(block)

        messages.append({"role": "assistant", "content": assistant_content})

        if stop_reason == "end_turn" or not tool_uses:
            audit.log("agent_done", f"Agent finished after {turn} turns")
            output = _parse_final_output(final_text, audit)
            output["tool_results"] = collected
            output["agent_turns"] = turn
            return output

        # Execute each tool call
        tool_results_content = []
        for tu in tool_uses:
            t_name = tu["name"]
            t_id = tu["id"]
            t_input = tu.get("input", {})

            audit.log("tool_call", f"Agent called: {t_name}", {"input": t_input})
            tool_result = _execute_tool(t_name, t_input, calendar, emails, collected)
            collected[t_name] = tool_result
            audit.log("tool_result", f"{t_name} returned {len(json.dumps(tool_result))} chars")

            tool_results_content.append({
                "type": "tool_result",
                "tool_use_id": t_id,
                "content": json.dumps(tool_result),
            })

        messages.append({"role": "user", "content": tool_results_content})

    audit.log("agent_max_turns", "Agent hit max turn limit")
    output = _parse_final_output(final_text, audit)
    output["tool_results"] = collected
    output["agent_turns"] = MAX_AGENT_TURNS
    return output


def _parse_final_output(text: str, audit: AuditLog) -> dict:
    """Extract the JSON output from the agent's final response."""
    # Try to find a JSON block
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            parsed = json.loads(text[start:end])
            audit.log("parse_output", "Successfully parsed agent JSON output")
            return parsed
        except json.JSONDecodeError:
            pass

    audit.log("parse_fallback", "Could not parse JSON from agent — returning raw text")
    return {
        "analysis_summary": text[:500],
        "patterns_detected": [],
        "proposals": [],
    }


# ── Heuristic fallback (no LLM) ────────────────────────────────────────

def run_agent_heuristic(
    calendar: list[dict],
    emails: list[dict],
    audit: AuditLog,
) -> dict:
    """Deterministic fallback when Bedrock is unavailable."""
    audit.log("fallback_start", "Running heuristic analysis (no LLM)")

    cal_load = tool_module.scan_calendar_load(calendar)
    audit.log("tool_call", "scan_calendar_load (heuristic)")
    cal_b2b = tool_module.scan_calendar_back_to_back(calendar)
    audit.log("tool_call", "scan_calendar_back_to_back (heuristic)")
    cal_rec = tool_module.scan_calendar_recurring(calendar)
    audit.log("tool_call", "scan_calendar_recurring (heuristic)")
    cal_focus = tool_module.scan_calendar_focus_time(calendar)
    audit.log("tool_call", "scan_calendar_focus_time (heuristic)")
    em_stale = tool_module.scan_email_stale(emails)
    audit.log("tool_call", "scan_email_stale (heuristic)")
    em_chains = tool_module.scan_email_long_chains(emails)
    audit.log("tool_call", "scan_email_long_chains (heuristic)")
    em_vol = tool_module.scan_email_volume(emails)
    audit.log("tool_call", "scan_email_volume (heuristic)")
    xref = tool_module.cross_reference(cal_load, cal_b2b, cal_rec, cal_focus,
                                        em_stale, em_chains, em_vol)
    audit.log("tool_call", "cross_reference (heuristic)")

    # Build patterns list
    patterns: list[dict] = []
    for day in cal_load.get("overloaded_days", []):
        patterns.append({"type": "overloaded_day", "severity": "high",
                         "detail": f"{day['date']}: {day['total_hours']}h meetings"})
    for pair in cal_b2b.get("back_to_back_pairs", []):
        patterns.append({"type": "back_to_back", "severity": "medium",
                         "detail": f"{pair['date']}: {pair['meeting_a']} → {pair['meeting_b']}"})
    for m in cal_rec.get("flagged_recurring_meetings", []):
        patterns.append({"type": "declined_recurring", "severity": "medium",
                         "detail": f"'{m['title']}' skipped {m['declined']}/{m['total']}"})
    for d in cal_focus.get("days_with_no_focus_block", []):
        patterns.append({"type": "no_focus_block", "severity": "high",
                         "detail": f"{d}: no 2-hour focus block available"})
    for t in em_stale.get("stale_threads", []):
        patterns.append({"type": "stale_email", "severity": "high",
                         "detail": f"'{t['subject']}' awaiting reply for {t['age_days']}d"})
    for c in em_chains.get("long_chains", []):
        patterns.append({"type": "fyi_chain", "severity": "low",
                         "detail": f"'{c['subject']}' has {c['message_count']} messages"})

    # Build proposals from patterns
    proposals: list[dict] = []
    rank = 0

    if cal_load.get("overloaded_days"):
        rank += 1
        proposals.append({
            "rank": rank,
            "description": "Auto-block 2-hour focus time on days with >5h of meetings",
            "rationale": (f"{len(cal_load['overloaded_days'])} days exceed 5h meetings, "
                          f"avg focus time {cal_focus.get('average_focus_hours_per_day', 0)}h/day"),
            "data_used": ["scan_calendar_load", "scan_calendar_focus_time"],
            "risk_level": "low",
            "estimated_time_saved_weekly": "4 hours",
        })

    if cal_b2b.get("count", 0) > 0:
        rank += 1
        proposals.append({
            "rank": rank,
            "description": "Insert 15-min buffer between back-to-back meetings",
            "rationale": f"{cal_b2b['count']} back-to-back pairs cause context-switching fatigue",
            "data_used": ["scan_calendar_back_to_back"],
            "risk_level": "low",
            "estimated_time_saved_weekly": "2 hours (mental recovery)",
        })

    if cal_rec.get("count", 0) > 0:
        rank += 1
        titles = [m["title"] for m in cal_rec["flagged_recurring_meetings"]]
        proposals.append({
            "rank": rank,
            "description": f"Auto-decline or convert to async: {', '.join(titles)}",
            "rationale": f"{cal_rec['count']} recurring meetings have >40% skip rate",
            "data_used": ["scan_calendar_recurring"],
            "risk_level": "medium",
            "estimated_time_saved_weekly": f"{sum(m['total'] * 0.5 for m in cal_rec['flagged_recurring_meetings']):.0f} hours",
        })

    if em_stale.get("count", 0) > 0:
        rank += 1
        proposals.append({
            "rank": rank,
            "description": "Auto-send follow-up reminders for emails pending >7 days",
            "rationale": f"{em_stale['count']} threads are stale — risk of dropped commitments",
            "data_used": ["scan_email_stale"],
            "risk_level": "low",
            "estimated_time_saved_weekly": "1 hour",
        })

    if em_chains.get("count", 0) > 0:
        rank += 1
        proposals.append({
            "rank": rank,
            "description": "Auto-archive or mute FYI threads with >10 messages",
            "rationale": f"{em_chains['count']} threads are long FYI chains with low signal",
            "data_used": ["scan_email_long_chains"],
            "risk_level": "low",
            "estimated_time_saved_weekly": "30 minutes",
        })

    if not proposals:
        proposals.append({
            "rank": 1,
            "description": "No strong automation signals detected",
            "rationale": "Work patterns appear healthy",
            "data_used": [],
            "risk_level": "low",
            "estimated_time_saved_weekly": "0",
        })

    summary = (
        f"Detected {len(patterns)} patterns across "
        f"{cal_load.get('total_events', 0)} calendar events and "
        f"{em_vol.get('total_threads', 0)} email threads. "
        f"Severity: {xref.get('severity', 'unknown')}."
    )

    audit.log("fallback_done", f"Heuristic analysis complete: {len(proposals)} proposals")

    return {
        "analysis_summary": summary,
        "patterns_detected": patterns,
        "proposals": proposals,
        "tool_results": {
            "calendar_load": cal_load,
            "back_to_back": cal_b2b,
            "recurring": cal_rec,
            "focus_time": cal_focus,
            "email_stale": em_stale,
            "email_chains": em_chains,
            "email_volume": em_vol,
            "cross_reference": xref,
        },
    }


# ── Public entry point ──────────────────────────────────────────────────

def run_agent(
    calendar: list[dict],
    emails: list[dict],
    audit: AuditLog,
) -> dict:
    """Run the agentic analysis, falling back to heuristic if Bedrock fails."""
    try:
        return run_agent_bedrock(calendar, emails, audit)
    except Exception as e:
        audit.log("bedrock_error", f"Bedrock unavailable: {e}", {"error": str(e)})
        print(f"  ⚠ Bedrock unavailable ({e}), using heuristic fallback", file=sys.stderr)
        return run_agent_heuristic(calendar, emails, audit)
