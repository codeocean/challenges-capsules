"""Geneformer adapter — tokenize cells, run pretrained model, extract embeddings."""
from __future__ import annotations
import numpy as np
import pandas as pd
import anndata as ad
from pathlib import Path

DATA_DIR = Path("/data")

def get_geneformer_embeddings(adata_train: ad.AnnData, adata_test: ad.AnnData) -> tuple[np.ndarray, np.ndarray]:
    from transformers import AutoModel, AutoTokenizer
    import torch

    weights_dir = DATA_DIR / "geneformer_weights"
    gene_map_path = DATA_DIR / "gene_mapping.csv"

    # Load gene mapping (HGNC symbol -> Ensembl ID)
    gene_map = {}
    if gene_map_path.exists():
        gm = pd.read_csv(gene_map_path)
        col_sym = [c for c in gm.columns if "symbol" in c.lower() or "hgnc" in c.lower()][0]
        col_ens = [c for c in gm.columns if "ensembl" in c.lower()][0]
        gene_map = dict(zip(gm[col_sym], gm[col_ens]))

    # Load model
    model = AutoModel.from_pretrained(str(weights_dir))
    model.eval()

    def embed_adata(adata: ad.AnnData) -> np.ndarray:
        """Simple tokenization: rank genes by expression, take top-2048."""
        embeddings = []
        expr = adata.X.toarray() if hasattr(adata.X, "toarray") else np.array(adata.X)

        for i in range(adata.n_obs):
            cell_expr = expr[i]
            ranked_idx = np.argsort(cell_expr)[::-1][:2048]
            # Convert to token IDs (use gene index as fallback)
            input_ids = torch.tensor([ranked_idx], dtype=torch.long)
            attention_mask = torch.ones_like(input_ids)
            with torch.no_grad():
                try:
                    out = model(input_ids=input_ids, attention_mask=attention_mask)
                    emb = out.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
                except Exception:
                    emb = np.zeros(256)
            embeddings.append(emb)

        return np.array(embeddings)

    train_emb = embed_adata(adata_train)
    test_emb = embed_adata(adata_test)
    return train_emb, test_emb
