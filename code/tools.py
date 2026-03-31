#!/usr/bin/env python3
"""Pure-Python heuristic tools for the productivity agent.

Each function accepts structured workspace data and returns pattern
dictionaries.  These are registered as Bedrock tool-use functions so the
agent decides *when* and *in what order* to call them.
"""

from __future__ import annotations


# ── Calendar tools ───────────────────────────────────────────────────────

def scan_calendar_load(events: list[dict]) -> dict:
    """Compute per-day meeting-load statistics.

    Returns summary with overloaded days (>5 h), daily totals, and
    overall meeting-hour average.
    """
    by_date: dict[str, list[dict]] = {}
    for ev in events:
        d = ev.get("date", ev.get("start", ""))[:10]
        by_date.setdefault(d, []).append(ev)

    daily: list[dict] = []
    overloaded: list[dict] = []
    for date, devs in sorted(by_date.items()):
        total = sum(e.get("duration_hours", 1.0) for e in devs)
        entry = {"date": date, "meetings": len(devs), "total_hours": round(total, 2)}
        daily.append(entry)
        if total > 5:
            overloaded.append(entry)

    avg = round(sum(d["total_hours"] for d in daily) / max(len(daily), 1), 2)
    return {
        "total_events": len(events),
        "days_analysed": len(daily),
        "average_meeting_hours_per_day": avg,
        "overloaded_days": overloaded,
        "daily_breakdown": daily,
    }


def scan_calendar_back_to_back(events: list[dict]) -> dict:
    """Identify back-to-back meetings with no gap."""
    by_date: dict[str, list[dict]] = {}
    for ev in events:
        d = ev.get("date", ev.get("start", ""))[:10]
        by_date.setdefault(d, []).append(ev)

    pairs: list[dict] = []
    for date, devs in sorted(by_date.items()):
        devs_sorted = sorted(devs, key=lambda e: e.get("start", ""))
        for i in range(len(devs_sorted) - 1):
            end_cur = devs_sorted[i].get("end", "")
            start_nxt = devs_sorted[i + 1].get("start", "")
            if end_cur and start_nxt and end_cur >= start_nxt:
                pairs.append({
                    "date": date,
                    "meeting_a": devs_sorted[i].get("title", "?"),
                    "meeting_b": devs_sorted[i + 1].get("title", "?"),
                    "end_a": end_cur,
                    "start_b": start_nxt,
                })
    return {"back_to_back_pairs": pairs, "count": len(pairs)}


def scan_calendar_recurring(events: list[dict]) -> dict:
    """Identify recurring meetings with high decline/tentative rates."""
    rec: dict[str, dict] = {}
    for ev in events:
        if not ev.get("recurring"):
            continue
        title = ev.get("title", "Unknown")
        rec.setdefault(title, {"total": 0, "declined": 0, "tentative": 0})
        rec[title]["total"] += 1
        resp = ev.get("response", "").lower()
        if resp == "declined":
            rec[title]["declined"] += 1
        elif resp == "tentative":
            rec[title]["tentative"] += 1

    flagged: list[dict] = []
    for title, c in rec.items():
        skip = c["declined"] + c["tentative"]
        rate = skip / max(c["total"], 1)
        if skip >= 2 or rate > 0.4:
            flagged.append({
                "title": title,
                "total": c["total"],
                "declined": c["declined"],
                "tentative": c["tentative"],
                "skip_rate": round(rate, 2),
            })
    return {"flagged_recurring_meetings": flagged, "count": len(flagged)}


def scan_calendar_focus_time(events: list[dict]) -> dict:
    """Estimate available focus-block time (>= 2 h uninterrupted)."""
    by_date: dict[str, list[dict]] = {}
    for ev in events:
        d = ev.get("date", ev.get("start", ""))[:10]
        by_date.setdefault(d, []).append(ev)

    focus_blocks: list[dict] = []
    for date, devs in sorted(by_date.items()):
        devs_sorted = sorted(devs, key=lambda e: e.get("start", ""))
        # workday 08:00-18:00
        boundaries = [8.0]
        for ev in devs_sorted:
            sh = _hour_of(ev.get("start", ""))
            eh = _hour_of(ev.get("end", ""))
            if sh is not None:
                boundaries.append(sh)
            if eh is not None:
                boundaries.append(eh)
        boundaries.append(18.0)
        boundaries = sorted(set(boundaries))

        gaps: list[dict] = []
        for i in range(len(boundaries) - 1):
            gap = boundaries[i + 1] - boundaries[i]
            # check no meeting occupies this gap
            occupied = False
            for ev in devs_sorted:
                es = _hour_of(ev.get("start", ""))
                ee = _hour_of(ev.get("end", ""))
                if es is not None and ee is not None:
                    if es < boundaries[i + 1] and ee > boundaries[i]:
                        occupied = True
                        break
            if not occupied and gap >= 2.0:
                gaps.append({"start_hour": boundaries[i], "hours": round(gap, 2)})
        focus_blocks.append({"date": date, "focus_gaps": gaps, "total_focus_hours": round(sum(g["hours"] for g in gaps), 2)})

    avg = round(sum(d["total_focus_hours"] for d in focus_blocks) / max(len(focus_blocks), 1), 2)
    zero_days = [d["date"] for d in focus_blocks if d["total_focus_hours"] < 2]
    return {
        "average_focus_hours_per_day": avg,
        "days_with_no_focus_block": zero_days,
        "daily_focus": focus_blocks,
    }


# ── Email tools ──────────────────────────────────────────────────────────

def scan_email_stale(threads: list[dict]) -> dict:
    """Find threads awaiting reply for > 7 days."""
    stale = [
        {
            "thread_id": t["thread_id"],
            "subject": t.get("subject", ""),
            "age_days": t.get("age_days", 0),
            "priority": t.get("priority", ""),
        }
        for t in threads
        if t.get("awaiting_reply") and t.get("age_days", 0) > 7
    ]
    return {"stale_threads": stale, "count": len(stale)}


def scan_email_long_chains(threads: list[dict], threshold: int = 10) -> dict:
    """Find threads with more than *threshold* messages (FYI chains)."""
    long = [
        {
            "thread_id": t["thread_id"],
            "subject": t.get("subject", ""),
            "message_count": len(t.get("messages", [])),
        }
        for t in threads
        if len(t.get("messages", [])) > threshold
    ]
    return {"long_chains": long, "count": len(long)}


def scan_email_volume(threads: list[dict]) -> dict:
    """Summarise email volume: total threads, awaiting-reply, priority split."""
    awaiting = sum(1 for t in threads if t.get("awaiting_reply"))
    by_priority: dict[str, int] = {}
    for t in threads:
        p = t.get("priority", "unknown")
        by_priority[p] = by_priority.get(p, 0) + 1
    return {
        "total_threads": len(threads),
        "awaiting_reply": awaiting,
        "by_priority": by_priority,
    }


# ── Cross-analysis ───────────────────────────────────────────────────────

def cross_reference(
    cal_load: dict, cal_b2b: dict, cal_recurring: dict, cal_focus: dict,
    email_stale: dict, email_chains: dict, email_volume: dict,
) -> dict:
    """Synthesise insights across calendar and email patterns."""
    insights: list[str] = []

    if cal_load.get("overloaded_days"):
        n = len(cal_load["overloaded_days"])
        insights.append(f"{n} overloaded days (>5 h meetings) leave no room for deep work.")

    if cal_b2b.get("count", 0) > 2:
        insights.append(
            f"{cal_b2b['count']} back-to-back meeting pairs cause context-switching fatigue."
        )

    if cal_recurring.get("count", 0) > 0:
        titles = [m["title"] for m in cal_recurring.get("flagged_recurring_meetings", [])]
        insights.append(
            f"Recurring meetings frequently skipped: {', '.join(titles)}. "
            "Consider removing or making optional."
        )

    if cal_focus.get("days_with_no_focus_block"):
        n = len(cal_focus["days_with_no_focus_block"])
        insights.append(f"{n} days have no 2-hour focus block.")

    if email_stale.get("count", 0) > 0:
        insights.append(
            f"{email_stale['count']} email threads stale >7 days — risk of dropped commitments."
        )

    if email_chains.get("count", 0) > 0:
        insights.append(
            f"{email_chains['count']} email threads exceed 10 messages — likely low-signal FYI chains."
        )

    severity = "high" if len(insights) >= 4 else ("medium" if insights else "low")
    return {"insights": insights, "severity": severity, "insight_count": len(insights)}


# ── Helper ───────────────────────────────────────────────────────────────

def _hour_of(ts: str) -> float | None:
    """Extract fractional hour from ISO timestamp."""
    if not ts or "T" not in ts:
        return None
    parts = ts.split("T")[1].split(":")
    return int(parts[0]) + int(parts[1]) / 60.0


# ── Tool registry (used by the Bedrock agent) ───────────────────────────

TOOL_REGISTRY: dict[str, callable] = {
    "scan_calendar_load": scan_calendar_load,
    "scan_calendar_back_to_back": scan_calendar_back_to_back,
    "scan_calendar_recurring": scan_calendar_recurring,
    "scan_calendar_focus_time": scan_calendar_focus_time,
    "scan_email_stale": scan_email_stale,
    "scan_email_long_chains": scan_email_long_chains,
    "scan_email_volume": scan_email_volume,
    "cross_reference": cross_reference,
}
