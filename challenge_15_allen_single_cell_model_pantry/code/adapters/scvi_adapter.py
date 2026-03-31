"""scVI adapter — train scVI and extract latent embeddings."""
from __future__ import annotations
import numpy as np
import anndata as ad

def get_scvi_embeddings(adata_train: ad.AnnData, adata_test: ad.AnnData,
                        n_latent: int = 30, max_epochs: int = 50) -> tuple[np.ndarray, np.ndarray]:
    import scvi
    scvi.settings.seed = 42
    adata_full = ad.concat([adata_train, adata_test])
    scvi.model.SCVI.setup_anndata(adata_full)
    model = scvi.model.SCVI(adata_full, n_latent=n_latent)
    model.train(max_epochs=max_epochs, train_size=1.0)
    latent = model.get_latent_representation()
    n_train = adata_train.n_obs
    return latent[:n_train], latent[n_train:]
