# How to Implement: Automate Your Productivity — For Your Own Data

> **Goal**: Analyze *your* calendar and email data to detect work pattern
> anti-patterns, then generate ranked, explainable automation proposals
> using an AI agent.

---

## 1. What You Need (Your Data)

### Input Data Format

You need calendar events and/or email threads in JSON format:

| Input | Format | Description |
|-------|--------|-------------|
| **Calendar events** | JSON array | Meeting/event records with time, duration, participants, type |
| **Email threads** | JSON array | Email chains with timestamps, participants, subject, status |

### What Your Data Should Look Like

```json
// calendar_events.json
[
  {
    "id": "evt_001",
    "title": "Weekly Team Standup",
    "start": "2025-01-06T09:00:00",
    "end": "2025-01-06T09:30:00",
    "duration_minutes": 30,
    "attendees": ["alice@company.com", "bob@company.com"],
    "recurring": true,
    "category": "standup"
  },
  ...
]

// email_threads.json
[
  {
    "thread_id": "thr_001",
    "subject": "Q4 Budget Review",
    "messages": [
      {
        "from": "alice@company.com",
        "to": ["bob@company.com"],
        "timestamp": "2025-01-05T14:30:00",
        "is_fyi": false
      }
    ],
    "status": "awaiting_response",
    "last_activity": "2025-01-05T14:30:00"
  },
  ...
]
```

**Key requirements:**
- Calendar events must have `start`, `end` or `duration_minutes`, and `title`
- Email threads need `timestamp` and `participants` at minimum
- Dates should span at least 1–2 weeks for pattern detection
- No real PII required — anonymize names/emails if desired

---

## 2. Step-by-Step: Recreate This Capsule with Aqua

### Step 1: Create a New Capsule

> **Ask Aqua:**
> *"Create a new capsule called 'Productivity Analysis — [My Team/Org]' with Python 3.10, and install packages: boto3, pydantic, streamlit"*

### Step 2: Prepare Your Data

**Option A: Export from Microsoft 365 / Google Calendar**
Export your calendar and email data as JSON.

> **Ask Aqua:**
> *"Create a data asset called 'my-work-data' and attach it to my capsule at /data/work_data"*

Upload structure:
```
work_data/
├── calendar_events.json
├── email_threads.json
└── persona.json          # Optional: role description for context
```

**Option B: Use the built-in scenario generator**
The capsule includes synthetic scenario generation for prototyping.

> **Ask Aqua:**
> *"Generate a synthetic scenario based on my role: [describe your typical work pattern, e.g., 'engineering manager with 15+ meetings/week and heavy Slack/email load']"*

### Step 3: Configure the Analysis

> **Ask Aqua:**
> *"Adapt run.py to load my calendar data from /data/work_data/calendar_events.json and email data from /data/work_data/email_threads.json. Run the agent analysis with all 8 tools enabled."*

### Step 4: Run

**Batch mode (reproducible run):**
> **Ask Aqua:**
> *"Run my capsule with --scenario custom --data-dir /data/work_data"*

**Interactive mode (Streamlit):**
> **Ask Aqua:**
> *"Launch a Cloud Workstation so I can use the Streamlit app interactively"*

---

## 3. Outputs You'll Get

| File | What It Contains |
|------|-----------------|
| `habit_summary.json` | Detected patterns (back-to-back meetings, fragmented focus time, stale emails, etc.) |
| `proposals.json` | Ranked automation proposals with impact scores, reversibility flags, and explanations |
| `audit_log.jsonl` | Complete audit trail of agent reasoning and tool calls |
| `manifest.json` | Run configuration and data summary |

---

## 4. Adapting for Different Use Cases

### Use Case A: Team-wide analysis
Aggregate calendar data across team members.

> **Ask Aqua:**
> *"Modify the pipeline to analyze calendars for 5 team members. Detect cross-team meeting conflicts and suggest consolidated meeting slots."*

### Use Case B: Custom anti-patterns
Add your organization-specific patterns.

> **Ask Aqua:**
> *"Add a new analysis tool that detects 'context-switching' — meetings in different project contexts within 30 minutes of each other. Flag sequences of 3+ context switches."*

### Use Case C: Without LLM (deterministic only)
Run with the heuristic fallback (no AWS Bedrock needed).

> **Ask Aqua:**
> *"Configure the pipeline to use only the deterministic heuristic analysis (no Bedrock agent). Keep all 8 pattern detection tools."*

---

## 5. Tips

- **Anonymize first**: Replace real names/emails with pseudonyms if sharing results
- **2-week window**: Pattern detection works best with 10–15 business days of data
- **Review proposals carefully**: The agent suggests automations — always human-approve before acting
- **Iterate**: Run, review proposals, adjust thresholds (e.g., "stale email" = 5 days vs 3 days), re-run
- **Streamlit for exploration**: Use the interactive app to understand patterns before committing to automations

---

## 6. Environment Requirements

| Package | Purpose |
|---------|---------|
| `boto3` | AWS Bedrock for agentic analysis (optional) |
| `pydantic` | Data validation |
| `streamlit` | Interactive exploration UI |

**Compute**: CPU only, X-Small tier sufficient
**LLM**: AWS Bedrock (Claude) via managed credentials — falls back to heuristics if unavailable
