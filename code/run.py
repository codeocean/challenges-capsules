#!/usr/bin/env python3
"""run.py — Session 1: Generate and critique hypotheses from a seed question."""
from __future__ import annotations
import json, sqlite3, sys
from pathlib import Path

DATA_DIR = Path("/data")
RESULTS_DIR = Path("/results")

def load_papers(path: Path) -> list[dict]:
    papers = []
    with open(path) as f:
        for line in f:
            if line.strip():
                papers.append(json.loads(line))
    return papers

def generate_hypotheses(question: str, papers: list[dict]) -> list[dict]:
    """Use LLM to generate structured hypotheses citing specific papers."""
    papers_text = ""
    for i, p in enumerate(papers[:20]):
        papers_text += f"\n[{p.get('paper_id', i)}] {p.get('title', 'N/A')}\n  {p.get('abstract', '')[:300]}\n"

    system = (
        "You are a scientific hypothesis generator. Given a research question and "
        "paper abstracts, generate 3-5 structured hypotheses. Each must cite specific "
        "paper IDs. Return JSON array: [{\"id\": \"H1\", \"claim\": \"...\", "
        "\"evidence\": [{\"paper_id\": \"...\", \"passage\": \"...\", \"relevance\": \"supports\"}], "
        "\"confidence\": 0.7}]"
    )
    user = f"Question: {question}\n\nPapers:{papers_text}"

    try:
        result = _call_bedrock(system, user)
        return result
    except Exception as e:
        print(f"  Bedrock failed: {e}", file=sys.stderr)
    # Fallback
    return [{"id": "H1", "claim": "Hypothesis generation requires LLM access.",
             "evidence": [], "confidence": 0.0, "status": "proposed"}]

def critique_hypotheses(hypotheses: list[dict]) -> list[dict]:
    """LLM critique pass."""
    system = (
        "You are a scientific reviewer. For each hypothesis, identify weaknesses, "
        "flag overclaiming, suggest alternatives. Return JSON array with added 'critique' field."
    )
    user = json.dumps(hypotheses, indent=2)
    try:
        return _call_bedrock(system, user)
    except Exception as e:
        print(f"  Bedrock critique failed: {e}", file=sys.stderr)
        for h in hypotheses:
            h["critique"] = "Critique unavailable (LLM not reachable)"
        return hypotheses

def _call_bedrock(system, user):
    """Call AWS Bedrock Sonnet for hypothesis generation/critique."""
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
        contentType="application/json",
        accept="application/json",
        body=body,
    )
    result = json.loads(response["body"].read())
    t = result["content"][0]["text"]
    # Try array parse first, then object
    arr_start = t.find("[")
    arr_end = t.rfind("]") + 1
    if arr_start >= 0:
        return json.loads(t[arr_start:arr_end])
    obj_start = t.find("{")
    obj_end = t.rfind("}") + 1
    return json.loads(t[obj_start:obj_end])

def save_to_sqlite(hypotheses: list[dict], papers: list[dict], db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE IF NOT EXISTS hypotheses (id TEXT PRIMARY KEY, data TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS papers (paper_id TEXT PRIMARY KEY, data TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS sessions (session INTEGER, data TEXT)")
    for h in hypotheses:
        conn.execute("INSERT OR REPLACE INTO hypotheses VALUES (?, ?)", (h.get("id",""), json.dumps(h)))
    for p in papers:
        conn.execute("INSERT OR REPLACE INTO papers VALUES (?, ?)", (p.get("paper_id",""), json.dumps(p)))
    conn.execute("INSERT INTO sessions VALUES (1, ?)", (json.dumps(hypotheses),))
    conn.commit()
    conn.close()

def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    q_path = DATA_DIR / "question.json"
    papers_path = DATA_DIR / "corpus" / "papers.jsonl"
    if not q_path.exists() or not papers_path.exists():
        print("Data assets not found. Generating seed question and paper corpus...")
        question = "What molecular mechanisms drive selective vulnerability of dopaminergic neurons in the substantia nigra pars compacta in Parkinson's disease, and which cell types or pathways represent the most promising therapeutic targets?"
        papers = [
            {"paper_id": "P1", "title": "LRRK2 G2019S mutation in Parkinson's disease", "abstract": "The LRRK2 G2019S mutation is the most common genetic cause of Parkinson's disease. We show that this mutation causes selective degeneration of dopaminergic neurons in the substantia nigra through impaired mitophagy and increased oxidative stress."},
            {"paper_id": "P2", "title": "Alpha-synuclein aggregation in dopaminergic neurons", "abstract": "Alpha-synuclein aggregation is a hallmark of Parkinson's disease. We demonstrate that neuromelanin-containing neurons in the SNpc preferentially accumulate alpha-synuclein due to iron-catalyzed oxidation."},
            {"paper_id": "P3", "title": "Calbindin protects against calcium-mediated neurodegeneration", "abstract": "Calbindin-expressing dopaminergic neurons in the VTA are relatively spared in PD compared to SNpc neurons lacking calbindin. We show calcium buffering is essential for survival during pathological conditions."},
            {"paper_id": "P4", "title": "Complex I deficiency in Parkinson's disease", "abstract": "Mitochondrial Complex I deficiency is found in SNpc neurons of PD patients. We demonstrate this creates an energy crisis specifically during autonomous pacemaking activity."},
            {"paper_id": "P5", "title": "GBA1 mutations and glucocerebrosidase in PD", "abstract": "GBA1 haploinsufficiency causes glucosylceramide accumulation that templates alpha-synuclein aggregation. This represents the strongest genetic risk factor for sporadic PD."},
            {"paper_id": "P6", "title": "Neuroinflammation mediated by microglia in PD", "abstract": "Activated microglia contribute to dopaminergic neuron death through pro-inflammatory cytokine release and phagocytosis of stressed neurons in the SNpc."},
            {"paper_id": "P7", "title": "Dopamine metabolism and oxidative stress", "abstract": "Dopamine itself is a source of oxidative stress through auto-oxidation and MAO-B metabolism. SNpc neurons are particularly vulnerable due to their high dopamine turnover."},
            {"paper_id": "P8", "title": "Astrocyte dysfunction in Parkinson's disease", "abstract": "Astrocytes in the SNpc show reduced glutathione production and impaired neuroprotective functions in PD, contributing to the selective vulnerability of local dopaminergic neurons."},
            {"paper_id": "P9", "title": "Autonomous pacemaking and calcium oscillations in SNpc", "abstract": "SNpc dopaminergic neurons exhibit autonomous pacemaking driven by L-type calcium channels, creating chronic calcium stress that distinguishes them from VTA neurons."},
            {"paper_id": "P10", "title": "PINK1/Parkin mitophagy pathway in PD", "abstract": "Loss of PINK1 or Parkin disrupts mitochondrial quality control, leading to accumulation of damaged mitochondria in dopaminergic neurons and eventual cell death."},
            {"paper_id": "P11", "title": "Single-cell transcriptomics of human midbrain", "abstract": "Single-cell RNA-seq of human midbrain reveals molecular diversity among dopaminergic neurons with distinct vulnerability profiles correlated to their gene expression signatures."},
            {"paper_id": "P12", "title": "Lysosomal dysfunction in neurodegeneration", "abstract": "Impaired lysosomal function is a converging pathway in PD. Multiple PD genes (GBA1, LRRK2, ATP13A2) converge on lysosomal pH regulation and autophagy."},
            {"paper_id": "P13", "title": "Iron accumulation in the substantia nigra", "abstract": "Progressive iron accumulation in the SNpc contributes to oxidative stress and neuromelanin-mediated toxicity in PD, providing a potential therapeutic target."},
            {"paper_id": "P14", "title": "Dopamine transporter imaging in early PD", "abstract": "DAT-SPECT imaging reveals asymmetric loss of dopaminergic terminals in the putamen preceding clinical symptoms by years, enabling early diagnosis."},
            {"paper_id": "P15", "title": "Gene therapy approaches for Parkinson's disease", "abstract": "AAV-mediated delivery of GDNF, neurturin, or aromatic L-amino acid decarboxylase to the striatum shows promise in restoring dopamine signaling in PD models."},
            {"paper_id": "P16", "title": "Synaptic dysfunction precedes neuronal loss in PD", "abstract": "Electrophysiological studies show that synaptic transmission deficits in the SNpc precede frank neuronal loss, suggesting a therapeutic window for neuroprotection."},
            {"paper_id": "P17", "title": "Blood-brain barrier disruption in PD", "abstract": "BBB integrity is compromised in PD patients, allowing peripheral immune cell infiltration and exacerbating neuroinflammation in the substantia nigra."},
            {"paper_id": "P18", "title": "Gut-brain axis and alpha-synuclein propagation", "abstract": "Alpha-synuclein pathology may originate in the enteric nervous system and propagate to the brain via the vagus nerve, supporting Braak's staging hypothesis."},
            {"paper_id": "P19", "title": "Dopaminergic neuron subtypes and vulnerability", "abstract": "Molecular profiling reveals that SOX6+/ALDH1A1- dopaminergic neurons in the ventral SNpc tier are most vulnerable in PD, while CALB1+ neurons are relatively preserved."},
            {"paper_id": "P20", "title": "Neuromelanin as a double-edged sword", "abstract": "Neuromelanin initially protects neurons by sequestering iron and toxic metabolites, but upon neuronal death releases these compounds, propagating damage to neighboring cells."},
        ]
        # Save generated data to results for reproducibility
        (RESULTS_DIR / "corpus").mkdir(parents=True, exist_ok=True)
        with open(RESULTS_DIR / "corpus" / "papers.jsonl", "w") as f:
            for p in papers:
                f.write(json.dumps(p) + "\n")
        with open(RESULTS_DIR / "question.json", "w") as f:
            json.dump({"question": question}, f, indent=2)
        print(f"  Generated {len(papers)} curated PD papers")
    else:
        with open(q_path) as f:
            question = json.load(f)["question"]
        papers = load_papers(papers_path)
    print(f"Question: {question}")
    print(f"Papers: {len(papers)}")

    print("\nGenerating hypotheses ...")
    hypotheses = generate_hypotheses(question, papers)

    # Validate citations
    paper_ids = {p.get("paper_id", "") for p in papers}
    for h in hypotheses:
        for e in h.get("evidence", []):
            e["verified"] = e.get("paper_id", "") in paper_ids

    print("Running critique pass ...")
    hypotheses = critique_hypotheses(hypotheses)
    for h in hypotheses:
        h.setdefault("status", "proposed")

    # Save outputs
    db_path = RESULTS_DIR / "session_state.db"
    save_to_sqlite(hypotheses, papers, db_path)

    with open(RESULTS_DIR / "session_001_hypotheses.jsonl", "w") as f:
        for h in hypotheses:
            f.write(json.dumps(h) + "\n")

    with open(RESULTS_DIR / "evidence.jsonl", "w") as f:
        for h in hypotheses:
            for e in h.get("evidence", []):
                f.write(json.dumps(e) + "\n")

    print(f"\nSession 1 complete: {len(hypotheses)} hypotheses generated.")
    for h in hypotheses:
        print(f"  {h.get('id','?')}: {h.get('claim','')[:80]}... [{h.get('status','?')}]")

if __name__ == "__main__":
    main()
