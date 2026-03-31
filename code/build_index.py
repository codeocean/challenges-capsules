#!/usr/bin/env python3
"""build_index.py — Embed corpus pages and build FAISS index."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

DATA_DIR = Path("/data")
INDEX_DIR = Path("/scratch/index")


def main() -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    corpus_path = DATA_DIR / "corpus.jsonl"
    if not corpus_path.exists():
        print(f"ERROR: {corpus_path} not found", file=sys.stderr)
        sys.exit(1)

    pages = []
    with open(corpus_path) as f:
        for line in f:
            if line.strip():
                pages.append(json.loads(line))
    print(f"Loaded {len(pages)} pages.")

    # Embed with sentence-transformers
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [f"{p.get('title','')} {p.get('body_text','')[:500]}" for p in pages]
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype=np.float32)

    # Build FAISS index
    import faiss
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    faiss.write_index(index, str(INDEX_DIR / "pages.index"))
    np.save(str(INDEX_DIR / "embeddings.npy"), embeddings)

    # Save page metadata alongside
    with open(INDEX_DIR / "pages.json", "w") as f:
        json.dump(pages, f)

    print(f"Index built: {index.ntotal} vectors, dim={dim}")


if __name__ == "__main__":
    main()
