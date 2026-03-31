#!/usr/bin/env python3
"""Challenge 15: Allen Single Cell Model Pantry — Main benchmark script.

Head-to-head benchmark of scVI vs. Geneformer on Allen Human MTG cell-type
annotation. Loads frozen pre-split h5ad, runs both models through adapters,
classifies with KNN, outputs leaderboard CSV plus confusion matrices.

Eval: Cell-type classification macro F1 on donor-held-out test split.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import anndata as ad
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (f1_score, accuracy_score, confusion_matrix,
                             ConfusionMatrixDisplay)

sys.path.insert(0, "/code")

DATA_DIR = Path("/data")
RESULTS_DIR = Path("/results")
SEED = 42
K = 15

def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    np.random.seed(SEED)

    h5ad_path = DATA_DIR / "mtg_dataset.h5ad"
    if not h5ad_path.exists():
        print("Dataset not found. Generating synthetic MTG-like dataset...")
        rng = np.random.default_rng(SEED)
        n_cells, n_genes = 10000, 2000
        cell_types = ["L2/3 IT", "L4 IT", "L5 IT", "L5 ET", "L6 CT",
                      "Pvalb", "Sst", "Vip", "Lamp5", "Astro",
                      "Oligo", "OPC", "Micro", "Endo"]
        donors = [f"donor_{i}" for i in range(8)]
        test_donors = set(rng.choice(donors, 3, replace=False))

        X = rng.negative_binomial(3, 0.4, (n_cells, n_genes)).astype(np.float32)
        # Add cell-type-specific signal to first 50 genes
        for i, ct in enumerate(cell_types):
            mask = rng.choice(n_cells, n_cells // len(cell_types), replace=False)
            X[mask, i*3:(i+1)*3] += rng.poisson(8, (len(mask), 3))

        obs = pd.DataFrame({
            "cell_type": rng.choice(cell_types, n_cells),
            "donor_id": rng.choice(donors, n_cells),
        })
        obs["split"] = obs["donor_id"].apply(lambda d: "test" if d in test_donors else "train")

        adata = ad.AnnData(X=X, obs=obs)
        adata.var_names = [f"Gene_{i}" for i in range(n_genes)]
        adata.uns["source"] = "synthetic"
        h5ad_path = RESULTS_DIR / "mtg_dataset.h5ad"
        adata.write(h5ad_path)
        print(f"  Generated {n_cells} cells, {n_genes} genes, {len(cell_types)} types")
    else:
        adata = None

    print("Loading dataset ...")
    adata = ad.read_h5ad(h5ad_path)
    print(f"  {adata.n_obs} cells, {adata.n_vars} genes")

    # Split
    if "split" not in adata.obs.columns:
        print("ERROR: h5ad must have 'split' column in obs (train/test)", file=sys.stderr)
        sys.exit(1)

    label_col = None
    for c in ["cell_type", "celltype", "subclass", "cluster"]:
        if c in adata.obs.columns:
            label_col = c; break
    if not label_col:
        label_col = adata.obs.columns[0]
    print(f"  Using label column: {label_col}")

    adata_train = adata[adata.obs["split"] == "train"].copy()
    adata_test = adata[adata.obs["split"] == "test"].copy()
    y_train = adata_train.obs[label_col].values.astype(str)
    y_test = adata_test.obs[label_col].values.astype(str)
    print(f"  Train: {adata_train.n_obs}, Test: {adata_test.n_obs}")

    leaderboard = []

    # --- scVI ---------------------------------------------------------------
    print("\n=== scVI ===")
    t0 = time.time()
    try:
        from adapters.scvi_adapter import get_scvi_embeddings
        train_emb, test_emb = get_scvi_embeddings(adata_train, adata_test)
        knn = KNeighborsClassifier(n_neighbors=K)
        knn.fit(train_emb, y_train)
        pred_scvi = knn.predict(test_emb)
        f1_scvi = f1_score(y_test, pred_scvi, average="macro", zero_division=0)
        acc_scvi = accuracy_score(y_test, pred_scvi)
        elapsed_scvi = time.time() - t0
        print(f"  F1={f1_scvi:.4f}, Acc={acc_scvi:.4f}, Time={elapsed_scvi:.1f}s")
        leaderboard.append({"model": "scVI", "accuracy": round(acc_scvi, 4),
                            "macro_f1": round(f1_scvi, 4), "runtime_seconds": round(elapsed_scvi, 1)})
        # Confusion matrix
        labels = sorted(set(y_test))
        cm = confusion_matrix(y_test, pred_scvi, labels=labels)
        fig, ax = plt.subplots(figsize=(10, 8))
        ConfusionMatrixDisplay(cm, display_labels=labels).plot(ax=ax, xticks_rotation=90, cmap="Blues")
        ax.set_title("scVI — Confusion Matrix")
        fig.tight_layout()
        fig.savefig(str(RESULTS_DIR / "confusion_scvi.png"), dpi=150)
        plt.close(fig)
    except Exception as e:
        print(f"  scVI FAILED: {e}")
        leaderboard.append({"model": "scVI", "accuracy": 0, "macro_f1": 0, "error": str(e)})

    # --- Geneformer ---------------------------------------------------------
    print("\n=== Geneformer ===")
    t0 = time.time()
    try:
        from adapters.geneformer_adapter import get_geneformer_embeddings
        train_emb, test_emb = get_geneformer_embeddings(adata_train, adata_test)
        knn = KNeighborsClassifier(n_neighbors=K)
        knn.fit(train_emb, y_train)
        pred_gf = knn.predict(test_emb)
        f1_gf = f1_score(y_test, pred_gf, average="macro", zero_division=0)
        acc_gf = accuracy_score(y_test, pred_gf)
        elapsed_gf = time.time() - t0
        print(f"  F1={f1_gf:.4f}, Acc={acc_gf:.4f}, Time={elapsed_gf:.1f}s")
        leaderboard.append({"model": "Geneformer", "accuracy": round(acc_gf, 4),
                            "macro_f1": round(f1_gf, 4), "runtime_seconds": round(elapsed_gf, 1)})
        labels = sorted(set(y_test))
        cm = confusion_matrix(y_test, pred_gf, labels=labels)
        fig, ax = plt.subplots(figsize=(10, 8))
        ConfusionMatrixDisplay(cm, display_labels=labels).plot(ax=ax, xticks_rotation=90, cmap="Oranges")
        ax.set_title("Geneformer — Confusion Matrix")
        fig.tight_layout()
        fig.savefig(str(RESULTS_DIR / "confusion_geneformer.png"), dpi=150)
        plt.close(fig)
    except Exception as e:
        print(f"  Geneformer FAILED: {e}")
        leaderboard.append({"model": "Geneformer", "accuracy": 0, "macro_f1": 0, "error": str(e)})

    # --- Write outputs ------------------------------------------------------
    # --- PCA Baseline (always works, no external deps) ----------------------
    print("\n=== PCA Baseline ===")
    t0 = time.time()
    try:
        from sklearn.decomposition import PCA as PCAModel
        from sklearn.preprocessing import StandardScaler
        # Normalize
        scaler = StandardScaler(with_mean=True, with_std=True)
        X_train_norm = scaler.fit_transform(adata_train.X.toarray() if hasattr(adata_train.X, 'toarray') else adata_train.X)
        X_test_norm = scaler.transform(adata_test.X.toarray() if hasattr(adata_test.X, 'toarray') else adata_test.X)
        # PCA
        n_components = min(50, X_train_norm.shape[1], X_train_norm.shape[0])
        pca = PCAModel(n_components=n_components, random_state=SEED)
        train_emb_pca = pca.fit_transform(X_train_norm)
        test_emb_pca = pca.transform(X_test_norm)
        # KNN
        knn = KNeighborsClassifier(n_neighbors=K)
        knn.fit(train_emb_pca, y_train)
        pred_pca = knn.predict(test_emb_pca)
        f1_pca = f1_score(y_test, pred_pca, average="macro", zero_division=0)
        acc_pca = accuracy_score(y_test, pred_pca)
        elapsed_pca = time.time() - t0
        print(f"  F1={f1_pca:.4f}, Acc={acc_pca:.4f}, Time={elapsed_pca:.1f}s")
        leaderboard.append({"model": "PCA_baseline", "accuracy": round(acc_pca, 4),
                            "macro_f1": round(f1_pca, 4), "runtime_seconds": round(elapsed_pca, 1)})
        labels = sorted(set(y_test))
        cm = confusion_matrix(y_test, pred_pca, labels=labels)
        fig, ax = plt.subplots(figsize=(10, 8))
        ConfusionMatrixDisplay(cm, display_labels=labels).plot(ax=ax, xticks_rotation=90, cmap="Greens")
        ax.set_title("PCA Baseline — Confusion Matrix")
        fig.tight_layout()
        fig.savefig(str(RESULTS_DIR / "confusion_pca.png"), dpi=150)
        plt.close(fig)
    except Exception as e:
        print(f"  PCA FAILED: {e}")
        leaderboard.append({"model": "PCA_baseline", "accuracy": 0, "macro_f1": 0, "error": str(e)})

    # --- Write outputs (final) -----------------------------------------------
    lb_df = pd.DataFrame(leaderboard)
    lb_df.to_csv(RESULTS_DIR / "leaderboard.csv", index=False)
    print(f"\nLeaderboard:\n{lb_df.to_string(index=False)}")

    winner = max(leaderboard, key=lambda x: x.get("macro_f1", 0))
    summary = {"winner": winner["model"], "test_cells": int(adata_test.n_obs)}
    for r in leaderboard:
        summary[f"{r['model'].lower()}_f1"] = r.get("macro_f1", 0)
    with open(RESULTS_DIR / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\nDone.")

if __name__ == "__main__":
    main()
