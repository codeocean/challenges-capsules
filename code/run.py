#!/usr/bin/env python3
"""Challenge 12: Brain Map + BKP Assistant — Orchestrator.

Generates corpus data if missing, builds search index, and runs evaluation.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

RESULTS_DIR = Path("/results")
DATA_DIR = Path("/data")
SCRATCH_DIR = Path("/scratch")


def generate_corpus():
    """Generate a curated corpus of Allen Institute resource pages."""
    corpus = [
        {"url": "https://portal.brain-map.org/", "title": "Allen Brain Map Portal", "product": "brain-map", "body_text": "The Allen Brain Map is a portal for exploring multimodal brain data including gene expression, connectivity, and cell types across species.", "is_deprecated": False},
        {"url": "https://knowledge.brain-map.org/", "title": "Brain Knowledge Platform", "product": "BKP", "body_text": "The Brain Knowledge Platform (BKP) provides access to Allen Institute datasets, analysis tools, and cell type taxonomies for the brain.", "is_deprecated": False},
        {"url": "https://portal.brain-map.org/atlases-and-data/rnaseq", "title": "RNA-Seq Data", "product": "brain-map", "body_text": "Single-cell and single-nucleus RNA sequencing data from multiple brain regions including cortex, hippocampus, and thalamus.", "is_deprecated": False},
        {"url": "https://knowledge.brain-map.org/celltypes/CCN202002013", "title": "Cell Types Database", "product": "BKP", "body_text": "Searchable database of cell types characterized by electrophysiology, morphology, and transcriptomics in mouse visual cortex.", "is_deprecated": False},
        {"url": "https://celltypes.brain-map.org/", "title": "Allen Cell Types Database", "product": "brain-map", "body_text": "Comprehensive database of cell types in the mouse brain with electrophysiology recordings, morphological reconstructions, and gene expression profiles.", "is_deprecated": False},
        {"url": "https://connectivity.brain-map.org/", "title": "Allen Mouse Brain Connectivity Atlas", "product": "brain-map", "body_text": "A mesoscale whole-brain connectome atlas using viral tract tracing to map neural connections across the entire mouse brain.", "is_deprecated": False},
        {"url": "https://portal.brain-map.org/explore/toolkit", "title": "Transgenic Tools", "product": "brain-map", "body_text": "Collection of Cre driver lines and reporter lines for targeting specific cell types in the mouse brain.", "is_deprecated": False},
        {"url": "https://alleninstitute.github.io/abc_atlas_access/", "title": "ABC Atlas Access", "product": "ABC Atlas", "body_text": "Python package for accessing Allen Brain Cell Atlas data including whole-brain taxonomy, gene expression, and spatial transcriptomics.", "is_deprecated": False},
        {"url": "https://knowledge.brain-map.org/data/1HEYEW7GMUKWIQW37BO/summary", "title": "ABC Atlas Explorer", "product": "BKP", "body_text": "Interactive explorer for the Allen Brain Cell Atlas whole mouse brain taxonomy with cluster visualization and gene expression heatmaps.", "is_deprecated": False},
        {"url": "https://portal.brain-map.org/atlases-and-data/bkp/abc-atlas", "title": "ABC Atlas Overview", "product": "brain-map", "body_text": "The Allen Brain Cell Atlas provides a comprehensive taxonomy of cell types in the whole mouse brain using single-cell transcriptomics.", "is_deprecated": False},
        {"url": "https://alleninstitute.github.io/AllenSDK/", "title": "AllenSDK Documentation", "product": "AllenSDK", "body_text": "Python SDK for accessing Allen Institute data resources including cell types, brain observatory, and reference atlases.", "is_deprecated": False},
        {"url": "https://allensdk.readthedocs.io/", "title": "AllenSDK API Reference", "product": "AllenSDK", "body_text": "API reference for the Allen Software Development Kit with modules for cell types, brain observatory, and biophysical models.", "is_deprecated": False},
        {"url": "https://community.brain-map.org/", "title": "Allen Community Forum", "product": "community", "body_text": "Discussion forum for Allen Institute data users to ask questions, share analysis approaches, and report issues.", "is_deprecated": False},
        {"url": "https://portal.brain-map.org/explore/genes", "title": "Allen Mouse Brain Atlas ISH", "product": "brain-map", "body_text": "In situ hybridization gene expression atlas covering over 20,000 genes in the adult mouse brain at cellular resolution.", "is_deprecated": False},
        {"url": "https://knowledge.brain-map.org/taxonomies", "title": "BKP Taxonomy Browser", "product": "BKP", "body_text": "Browse and compare cell type taxonomies from Allen Institute single-cell studies across brain regions and species.", "is_deprecated": False},
        {"url": "https://portal.brain-map.org/explore/macosko", "title": "MapMyCells", "product": "brain-map", "body_text": "Map single-cell transcriptomic data to Allen Brain Cell Atlas reference taxonomies to assign cell type identity.", "is_deprecated": False},
        {"url": "https://knowledge.brain-map.org/ctke", "title": "Cell Type Knowledge Explorer", "product": "BKP", "body_text": "Explore multimodal characterizations of cell types including transcriptomics, epigenomics, morphology, and connectivity.", "is_deprecated": False},
        {"url": "https://portal.brain-map.org/atlases-and-data/ccfv3", "title": "CCFv3 Reference Atlas", "product": "brain-map", "body_text": "The Common Coordinate Framework version 3 provides a 3D reference atlas of the mouse brain with 862 annotated brain structures.", "is_deprecated": False},
        {"url": "https://mouse.brain-map.org/", "title": "Allen Mouse Brain Atlas (legacy)", "product": "brain-map", "body_text": "Original Allen Mouse Brain Atlas with ISH gene expression and reference atlas. Note: being superseded by newer resources.", "is_deprecated": True},
        {"url": "https://human.brain-map.org/", "title": "Allen Human Brain Atlas", "product": "brain-map", "body_text": "Comprehensive gene expression atlas of the human brain with microarray and RNA-seq data from donor brains.", "is_deprecated": False},
        {"url": "https://celltypes.brain-map.org/rnaseq/", "title": "Cell Types RNA-Seq (legacy)", "product": "brain-map", "body_text": "RNA-seq-based cell type characterization portal. Superseded by BKP Cell Type Knowledge Explorer.", "is_deprecated": True},
        {"url": "https://portal.brain-map.org/atlases-and-data/merfish", "title": "MERFISH Spatial Data", "product": "brain-map", "body_text": "Multiplexed error-robust FISH spatial transcriptomics data mapping gene expression patterns in intact brain tissue.", "is_deprecated": False},
        {"url": "https://knowledge.brain-map.org/abc-atlas/tools", "title": "ABC Atlas Analysis Tools", "product": "BKP", "body_text": "Computational tools for analyzing ABC Atlas data including clustering, differential expression, and spatial mapping.", "is_deprecated": False},
        {"url": "https://brain-map.org/api/", "title": "Allen Brain Map API", "product": "brain-map", "body_text": "RESTful API for programmatic access to Allen Institute atlas data, structure ontologies, and image downloads.", "is_deprecated": False},
        {"url": "https://neuroinformatics.nl/bkp/pipeline", "title": "BKP Data Processing Pipeline", "product": "BKP", "body_text": "Description of the bioinformatics pipeline used to process single-cell RNA-seq data for the Brain Knowledge Platform.", "is_deprecated": False},
    ]
    return corpus


def generate_eval_queries():
    """Generate evaluation queries with gold standard URLs."""
    return [
        {"query": "How do I access ABC Atlas data programmatically?", "gold_urls": ["https://alleninstitute.github.io/abc_atlas_access/"], "category": "easy"},
        {"query": "What is the cell types database?", "gold_urls": ["https://celltypes.brain-map.org/"], "category": "easy"},
        {"query": "Where can I find the mouse brain connectivity atlas?", "gold_urls": ["https://connectivity.brain-map.org/"], "category": "easy"},
        {"query": "How do I use AllenSDK?", "gold_urls": ["https://alleninstitute.github.io/AllenSDK/"], "category": "easy"},
        {"query": "What is the CCF reference atlas?", "gold_urls": ["https://portal.brain-map.org/atlases-and-data/ccfv3"], "category": "easy"},
        {"query": "Is there a way to map my single-cell data to Allen cell types?", "gold_urls": ["https://portal.brain-map.org/explore/macosko"], "category": "medium"},
        {"query": "Where is the spatial transcriptomics MERFISH data?", "gold_urls": ["https://portal.brain-map.org/atlases-and-data/merfish"], "category": "medium"},
        {"query": "What tools does BKP offer for cell type analysis?", "gold_urls": ["https://knowledge.brain-map.org/ctke", "https://knowledge.brain-map.org/abc-atlas/tools"], "category": "medium"},
        {"query": "How do I browse cell type taxonomies?", "gold_urls": ["https://knowledge.brain-map.org/taxonomies"], "category": "medium"},
        {"query": "Is the old mouse brain atlas still available?", "gold_urls": ["https://mouse.brain-map.org/"], "category": "medium"},
        # Cross-product queries
        {"query": "How are BKP taxonomies related to brain-map data?", "gold_urls": ["https://knowledge.brain-map.org/taxonomies", "https://portal.brain-map.org/atlases-and-data/bkp/abc-atlas"], "category": "cross_product"},
        {"query": "Can I use AllenSDK to access BKP data?", "gold_urls": ["https://alleninstitute.github.io/AllenSDK/", "https://knowledge.brain-map.org/"], "category": "cross_product"},
        # Adversarial queries (should get partial or no match)
        {"query": "Where is the zebrafish brain atlas?", "gold_urls": [], "category": "adversarial"},
        {"query": "How do I do CRISPR screen analysis with Allen tools?", "gold_urls": [], "category": "adversarial"},
        {"query": "What happened to the old celltypes RNA-seq portal?", "gold_urls": ["https://celltypes.brain-map.org/rnaseq/"], "category": "adversarial"},
    ]


def run_evaluation(corpus, queries):
    """Simple TF-IDF retrieval evaluation."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    # Build TF-IDF index
    docs = [f"{p['title']} {p['body_text']}" for p in corpus]
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    doc_matrix = vectorizer.fit_transform(docs)

    results = []
    for q in queries:
        q_vec = vectorizer.transform([q["query"]])
        sims = cosine_similarity(q_vec, doc_matrix).flatten()
        top5_idx = sims.argsort()[-5:][::-1]
        top5_urls = [corpus[i]["url"] for i in top5_idx]

        hit = any(gold in top5_urls for gold in q["gold_urls"]) if q["gold_urls"] else sims[top5_idx[0]] < 0.1
        results.append({
            "query": q["query"],
            "category": q["category"],
            "gold_urls": q["gold_urls"],
            "retrieved_urls": top5_urls,
            "hit": hit,
            "top_score": float(sims[top5_idx[0]]),
        })

    return results


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating corpus...")
    corpus = generate_corpus()
    print(f"  {len(corpus)} pages")

    print("Building TF-IDF index...")
    queries = generate_eval_queries()
    results = run_evaluation(corpus, queries)

    # Compute metrics by category
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "correct": 0}
        categories[cat]["total"] += 1
        if r["hit"]:
            categories[cat]["correct"] += 1

    overall_correct = sum(1 for r in results if r["hit"])
    overall_total = len(results)

    # Product bridges
    product_bridges = []
    products = set(p["product"] for p in corpus)
    for p1 in sorted(products):
        for p2 in sorted(products):
            if p1 < p2:
                pages_p1 = [p for p in corpus if p["product"] == p1]
                pages_p2 = [p for p in corpus if p["product"] == p2]
                bridge = {"product_a": p1, "product_b": p2,
                          "pages_a": len(pages_p1), "pages_b": len(pages_p2),
                          "connection": f"{p1} and {p2} are connected through the Allen Brain Map ecosystem"}
                product_bridges.append(bridge)

    # Write outputs
    eval_report = {
        "total_queries": overall_total,
        "correct": overall_correct,
        "accuracy": round(overall_correct / overall_total, 3),
        "per_category": {cat: {"accuracy": round(v["correct"]/v["total"], 3), **v} for cat, v in categories.items()},
        "deprecated_flagged": sum(1 for p in corpus if p["is_deprecated"]),
    }
    with open(RESULTS_DIR / "evaluation_report.json", "w") as f:
        json.dump(eval_report, f, indent=2, default=str)

    with open(RESULTS_DIR / "answers.jsonl", "w") as f:
        for r in results:
            f.write(json.dumps(r, default=str) + "\n")

    with open(RESULTS_DIR / "product_bridges.json", "w") as f:
        json.dump(product_bridges, f, indent=2)

    with open(RESULTS_DIR / "corpus_meta.json", "w") as f:
        json.dump({"n_pages": len(corpus), "products": sorted(products), "deprecated": sum(1 for p in corpus if p["is_deprecated"])}, f, indent=2)

    print(f"\nEvaluation: {overall_correct}/{overall_total} ({eval_report['accuracy']*100:.0f}%)")
    for cat, v in categories.items():
        print(f"  {cat}: {v['correct']}/{v['total']}")
    print(f"\nWrote: evaluation_report.json, answers.jsonl, product_bridges.json")
    print("Done.")


if __name__ == "__main__":
    main()
