#!/usr/bin/env python3
"""run_session2.py — Session 2: Load prior state, apply human decisions, refine."""
from __future__ import annotations
import json, sqlite3, sys
from pathlib import Path

DATA_DIR = Path("/data")
RESULTS_DIR = Path("/results")

def load_session1(db_path: Path) -> list[dict]:
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute("SELECT data FROM sessions WHERE session = 1").fetchall()
    conn.close()
    if rows:
        return json.loads(rows[0][0])
    return []

def load_papers_from_db(db_path: Path) -> list[dict]:
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute("SELECT data FROM papers").fetchall()
    conn.close()
    return [json.loads(r[0]) for r in rows]

def refine_hypotheses(hypotheses: list[dict], papers: list[dict]) -> list[dict]:
    """Use LLM to refine surviving hypotheses."""
    system = (
        "You are a scientific hypothesis refinement agent. Given accepted and edited "
        "hypotheses from a prior session, refine them and generate 1-2 new ones "
        "building on accepted work. Return JSON array."
    )
    user = f"Prior hypotheses:\n{json.dumps(hypotheses, indent=2)}"
    try:
        import os, boto3
        client = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_DEFAULT_REGION", "us-west-2"))
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 3000,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        })
        response = client.invoke_model(
            modelId=os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0"),
            contentType="application/json", accept="application/json", body=body,
        )
        result = json.loads(response["body"].read())
        t = result["content"][0]["text"]
        return json.loads(t[t.find("["):t.rfind("]") + 1])
    except Exception as e:
        print(f"  Bedrock refinement failed: {e}", file=sys.stderr)
        for h in hypotheses:
            h["status"] = "refined (LLM unavailable)"
        return hypotheses

def main() -> None:
    db_path = RESULTS_DIR / "session_state.db"
    decisions_path = DATA_DIR / "human_decisions.json"

    if not db_path.exists():
        print("ERROR: session_state.db not found. Run session 1 first.", file=sys.stderr); sys.exit(1)

    hypotheses = load_session1(db_path)
    papers = load_papers_from_db(db_path)
    print(f"Loaded {len(hypotheses)} hypotheses from session 1.")

    # Apply human decisions
    decisions = {}
    if decisions_path.exists():
        with open(decisions_path) as f:
            decisions = json.load(f)
        print(f"Loaded {len(decisions)} human decisions.")

    surviving = []
    for h in hypotheses:
        hid = h.get("id", "")
        decision = decisions.get(hid, "accepted")
        if decision == "rejected":
            h["status"] = "rejected"
            print(f"  {hid}: REJECTED")
        elif decision == "edit":
            h["claim"] = decisions.get(f"{hid}_edit", h["claim"])
            h["status"] = "edited"
            surviving.append(h)
            print(f"  {hid}: EDITED")
        else:
            h["status"] = "accepted"
            surviving.append(h)
            print(f"  {hid}: ACCEPTED")

    # Refine
    print("\nRefining hypotheses ...")
    refined = refine_hypotheses(surviving, papers)

    # Save session 2
    conn = sqlite3.connect(str(db_path))
    conn.execute("INSERT INTO sessions VALUES (2, ?)", (json.dumps(refined),))
    conn.commit()
    conn.close()

    with open(RESULTS_DIR / "session_002_hypotheses.jsonl", "w") as f:
        for h in refined:
            f.write(json.dumps(h) + "\n")

    print(f"\nSession 2 complete: {len(refined)} hypotheses.")
    for h in refined:
        print(f"  {h.get('id','?')}: {h.get('claim','')[:80]}... [{h.get('status','?')}]")

if __name__ == "__main__":
    main()
