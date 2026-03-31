#!/usr/bin/env python3
"""Two completely different synthetic workspace scenarios for productivity analysis.

Scenario 1 — "Meeting-Heavy Manager":
  Calendar dominated by long/overlapping meetings, many back-to-back,
  frequently-declined recurring meetings, very few focus blocks.
  Email has stale leadership threads and long FYI chains.

Scenario 2 — "Context-Switching Developer":
  Calendar has short scattered meetings breaking focus time,
  clustered sprint ceremonies, 1:1s spread across the week.
  Email has aging code-review requests, noisy notification threads,
  and unresolved technical discussions.
"""

from __future__ import annotations

import json
from pathlib import Path


# ── Scenario 1: Meeting-Heavy Manager ────────────────────────────────────

def _manager_calendar() -> list[dict]:
    """10 business days, ~6 events/day — heavy meetings, back-to-back days."""
    events: list[dict] = []
    eid = 0

    # Week 1: Mon 2025-06-02 … Fri 2025-06-06
    # Week 2: Mon 2025-06-09 … Fri 2025-06-13
    dates = [
        "2025-06-02", "2025-06-03", "2025-06-04", "2025-06-05", "2025-06-06",
        "2025-06-09", "2025-06-10", "2025-06-11", "2025-06-12", "2025-06-13",
    ]

    # Monday pattern: back-to-back morning, overloaded day (7 h)
    for monday in [dates[0], dates[5]]:
        for start_h, dur, title, rec, resp in [
            (8,  1.0, "Leadership Standup",        True,  "accepted"),
            (9,  1.5, "Product Strategy Review",   False, "accepted"),
            (10, 1.0, "Design Sync",               True,  "accepted"),
            (11, 1.0, "1:1 with VP Eng",           True,  "accepted"),
            (13, 1.5, "Cross-Team Planning",       False, "accepted"),
            (15, 1.0, "Vendor Call",                False, "accepted"),
        ]:
            eid += 1
            events.append(_evt(eid, title, monday, start_h, dur, rec, resp))

    # Tuesday/Wednesday: heavy day (6+ h) with back-to-back afternoon
    for day in [dates[1], dates[2], dates[6], dates[7]]:
        for start_h, dur, title, rec, resp in [
            (8,  0.5, "Morning Check-in",       True,  "accepted"),
            (9,  1.0, "Engineering All-Hands",  True,  "accepted"),
            (10, 0.5, "Hiring Debrief",         False, "accepted"),
            (11, 1.0, "Sprint Review",          True,  "accepted"),
            (13, 1.0, "Project Status Update",  False, "accepted"),
            (14, 1.5, "Architecture Review",    False, "accepted"),
            (16, 0.5, "Quick Sync — Platform",  False, "accepted"),
        ]:
            eid += 1
            events.append(_evt(eid, title, day, start_h, dur, rec, resp))

    # Thursday: interview day — short gaps but many meetings
    for thu in [dates[3], dates[8]]:
        for start_h, dur, title, rec, resp in [
            (9,  1.0, "Interview — Panel A",    False, "accepted"),
            (10, 1.0, "Interview — Panel B",    False, "accepted"),
            (11, 0.5, "Hiring Sync",            False, "accepted"),
            (13, 1.0, "Interview — Panel C",    False, "accepted"),
            (14, 1.0, "Offer Discussion",       False, "accepted"),
            (15, 1.0, "Interview Retro",        False, "accepted"),
        ]:
            eid += 1
            events.append(_evt(eid, title, thu, start_h, dur, rec, resp))

    # Friday: recurring meetings that get declined
    for fri in [dates[4], dates[9]]:
        for start_h, dur, title, rec, resp in [
            (9,  0.5, "Friday Coffee Chat",     True,  "declined"),
            (10, 1.0, "Weekly Metrics Review",  True,  "accepted"),
            (14, 1.0, "Innovation Hour",        True,  "declined"),
            (16, 1.0, "Weekly Sync",            True,  "declined"),
        ]:
            eid += 1
            events.append(_evt(eid, title, fri, start_h, dur, rec, resp))

    return events


def _manager_emails() -> list[dict]:
    """30 threads — stale leadership threads, long FYI chains."""
    threads: list[dict] = []

    # Stale threads (>7 days, awaiting reply)
    threads.append(_thread(
        "thr_001", "Q3 Budget Reforecast", age=12, awaiting=True, priority="high",
        messages=_msgs(["CFO", "You", "CFO"], "2025-05-22", "Budget numbers...",
                        "Need your input...", "Following up — please advise"),
    ))
    threads.append(_thread(
        "thr_002", "Re: Headcount Request — Data Platform", age=9, awaiting=True,
        priority="high",
        messages=_msgs(["HR", "You", "HR", "You"], "2025-05-25",
                        "Headcount form attached", "Submitted", "Missing justification",
                        "Working on revised justification"),
    ))
    threads.append(_thread(
        "thr_003", "Vendor Security Review", age=14, awaiting=True, priority="medium",
        messages=_msgs(["Security", "You", "Security"], "2025-05-20",
                        "Please review vendor SOC-2", "Will do by EOW",
                        "Any update? Blocking onboarding"),
    ))

    # Long FYI chain (>10 messages)
    threads.append(_thread(
        "thr_004", "RE: Company All-Hands Notes", age=5, awaiting=False,
        priority="low",
        messages=_msgs(
            ["CEO", "COO", "VP", "Director", "PM1", "PM2", "Eng1", "Eng2",
             "HR", "CEO", "COO", "PM1"],
            "2025-05-29",
            *[f"FYI message #{i}" for i in range(1, 13)],
        ),
    ))
    threads.append(_thread(
        "thr_005", "RE: Org Restructure Announcement", age=3, awaiting=False,
        priority="low",
        messages=_msgs(
            ["CEO", "CHRO", "VP1", "VP2", "Dir1", "Dir2", "Mgr1", "Mgr2",
             "Mgr3", "Eng1", "Eng2"],
            "2025-06-01",
            *[f"Congrats / comment #{i}" for i in range(1, 12)],
        ),
    ))

    # Normal active threads
    for i in range(6, 31):
        age = (i % 5) + 1
        threads.append(_thread(
            f"thr_{i:03d}",
            f"Project Update Thread {i - 5}",
            age=age,
            awaiting=(i % 7 == 0),
            priority=["low", "medium", "high"][i % 3],
            messages=_msgs(
                ["Colleague", "You"],
                f"2025-06-{max(1, 10 - age):02d}",
                f"Update on item {i}", f"Acknowledged",
            ),
        ))

    return threads


# ── Scenario 2: Context-Switching Developer ──────────────────────────────

def _developer_calendar() -> list[dict]:
    """10 days, ~3-4 events/day — scattered short meetings breaking focus."""
    events: list[dict] = []
    eid = 0
    dates = [
        "2025-06-02", "2025-06-03", "2025-06-04", "2025-06-05", "2025-06-06",
        "2025-06-09", "2025-06-10", "2025-06-11", "2025-06-12", "2025-06-13",
    ]

    # Sprint ceremonies clustered on Monday
    for monday in [dates[0], dates[5]]:
        for start_h, dur, title, rec, resp in [
            (9,  0.25, "Daily Standup",            True,  "accepted"),
            (10, 1.5,  "Sprint Planning",          True,  "accepted"),
            (13, 1.0,  "Backlog Grooming",         True,  "accepted"),
            (15, 0.5,  "Sprint Retro",             True,  "accepted"),
        ]:
            eid += 1
            events.append(_evt(eid, title, monday, start_h, dur, rec, resp))

    # Tues-Thu: scattered 15-30 min meetings that break focus
    for day in [dates[1], dates[2], dates[3], dates[6], dates[7], dates[8]]:
        for start_h, dur, title, rec, resp in [
            (9,   0.25, "Daily Standup",         True,  "accepted"),
            (10,  0.5,  "Code Review Sync",      False, "accepted"),
            (13,  0.25, "Quick Bug Triage",      False, "accepted"),
            (15,  0.5,  "1:1 with Tech Lead",    True,  "accepted"),
        ]:
            eid += 1
            events.append(_evt(eid, title, day, start_h, dur, rec, resp))

    # Friday: light day but recurring meetings
    for fri in [dates[4], dates[9]]:
        for start_h, dur, title, rec, resp in [
            (9,  0.25, "Daily Standup",          True,  "accepted"),
            (11, 1.0,  "Demo / Show & Tell",     True,  "tentative"),
            (14, 0.5,  "Team Social",            True,  "declined"),
        ]:
            eid += 1
            events.append(_evt(eid, title, fri, start_h, dur, rec, resp))

    return events


def _developer_emails() -> list[dict]:
    """40 threads — aging code reviews, noisy notifications, tech discussions."""
    threads: list[dict] = []

    # Aging code-review requests (>3 days)
    for i in range(1, 6):
        threads.append(_thread(
            f"thr_d{i:03d}",
            f"PR #{100 + i}: {['Refactor auth module', 'Fix memory leak', 'Add retry logic', 'Update API schema', 'Improve test coverage'][i-1]}",
            age=3 + i,
            awaiting=True,
            priority="high",
            messages=_msgs(
                ["CI Bot", "Author", "You"],
                f"2025-06-{max(1, 8 - i):02d}",
                "CI passed ✓", f"Ready for review @you", "",
            ),
        ))

    # Stale technical discussion
    threads.append(_thread(
        "thr_d006", "RFC: Migrate to gRPC", age=11, awaiting=True,
        priority="medium",
        messages=_msgs(
            ["Architect", "You", "SRE", "Architect"],
            "2025-05-23",
            "Proposal attached", "Looks promising, need benchmarks",
            "Benchmark results attached", "Waiting for your sign-off",
        ),
    ))
    threads.append(_thread(
        "thr_d007", "Database Indexing Strategy", age=8, awaiting=True,
        priority="medium",
        messages=_msgs(
            ["DBA", "You", "DBA"],
            "2025-05-26",
            "Current indexes are suboptimal", "Agreed, drafting migration",
            "Any update on migration plan?",
        ),
    ))

    # Noisy notification threads (GitHub/CI)
    for i in range(8, 23):
        threads.append(_thread(
            f"thr_d{i:03d}",
            f"[GitHub] {'Dependabot' if i % 3 == 0 else 'CI'}: {f'PR #{200 + i}'} {'security update' if i % 3 == 0 else 'build status'}",
            age=i % 4,
            awaiting=False,
            priority="low",
            messages=_msgs(["Bot"], f"2025-06-{10 - (i % 4):02d}", f"Automated notification #{i}"),
        ))

    # Normal threads
    for i in range(23, 41):
        threads.append(_thread(
            f"thr_d{i:03d}",
            f"{'Feature discussion' if i % 2 == 0 else 'Bug report'} #{i - 22}",
            age=(i % 6) + 1,
            awaiting=(i % 5 == 0),
            priority=["low", "medium", "high"][i % 3],
            messages=_msgs(
                ["Teammate", "You"],
                f"2025-06-{max(1, 10 - (i % 6)):02d}",
                f"Details on item {i}", f"Looking into it",
            ),
        ))

    return threads


# ── Helpers ──────────────────────────────────────────────────────────────

def _evt(eid: int, title: str, date: str, start_h: int | float,
         dur: float, recurring: bool, response: str) -> dict:
    sh = int(start_h)
    sm = int((start_h - sh) * 60)
    eh = int(start_h + dur)
    em = int(((start_h + dur) - eh) * 60)
    return {
        "id": f"evt_{eid:03d}",
        "title": title,
        "date": date,
        "start": f"{date}T{sh:02d}:{sm:02d}:00",
        "end": f"{date}T{eh:02d}:{em:02d}:00",
        "duration_hours": dur,
        "recurring": recurring,
        "response": response,
        "organizer": "organizer@company.com",
        "attendees": ["user@company.com"],
        "category": "work",
    }


def _thread(tid: str, subject: str, age: int, awaiting: bool,
            priority: str, messages: list[dict]) -> dict:
    return {
        "thread_id": tid,
        "subject": subject,
        "messages": messages,
        "last_message_date": messages[-1]["date"] if messages else "",
        "awaiting_reply": awaiting,
        "age_days": age,
        "priority": priority,
    }


def _msgs(senders: list[str], start_date: str, *snippets: str) -> list[dict]:
    msgs = []
    for i, (sender, snippet) in enumerate(zip(senders, snippets)):
        msgs.append({
            "from": f"{sender.lower().replace(' ', '.')}@company.com",
            "date": f"{start_date}T{9 + i}:00:00",
            "snippet": snippet,
        })
    return msgs


# ── Public API ───────────────────────────────────────────────────────────

SCENARIOS = {
    "meeting_heavy_manager": {
        "name": "Meeting-Heavy Manager",
        "description": (
            "A senior manager whose calendar is dominated by long, overlapping "
            "meetings with frequent back-to-back scheduling, many recurring "
            "meetings that are often declined, and almost no focus blocks. "
            "Email includes stale leadership threads and long FYI chains."
        ),
        "calendar": _manager_calendar,
        "emails": _manager_emails,
    },
    "context_switching_developer": {
        "name": "Context-Switching Developer",
        "description": (
            "A senior developer whose days are fragmented by scattered short "
            "meetings that break deep-focus time, clustered sprint ceremonies, "
            "and 1:1s spread across the week. Email is dominated by aging code "
            "reviews, noisy CI/bot notifications, and unresolved technical RFCs."
        ),
        "calendar": _developer_calendar,
        "emails": _developer_emails,
    },
}


def load_scenario(name: str) -> tuple[list[dict], list[dict]]:
    """Return (calendar_events, email_threads) for the named scenario."""
    s = SCENARIOS[name]
    return s["calendar"](), s["emails"]()


def save_scenario(name: str, base_dir: Path) -> Path:
    """Write scenario data to disk and return the scenario directory."""
    cal, emails = load_scenario(name)
    out = base_dir / name
    out.mkdir(parents=True, exist_ok=True)
    (out / "calendar_events.json").write_text(json.dumps(cal, indent=2))
    (out / "email_threads.json").write_text(json.dumps(emails, indent=2))
    return out
