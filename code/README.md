# Challenge 14: Segment Intestine Villi


## Results Summary
- **GeoJSON boundaries** generated for villus polygons
- **Cell assignments** for all cells to villus clusters
- **Data:** Simulated spatial data (PARTIAL — pending real Xenium)

> See [RESULTS.md](RESULTS.md) for output artifact details.

## What This Capsule Does
Loads Xenium ileum spatial transcriptomics data, scores cells as epithelial using
marker genes (EPCAM, FABP1, FABP2, VIL1), builds spatial neighbor graph, runs
Leiden clustering, outputs color-coded spatial map + per-villus composition.

## Evaluation
Visual — do the colored clusters correspond to individual villi as judged by domain expert?

## Required Data Assets
| File | Description |
|------|-------------|
| `xenium_ileum/` | Xenium cell feature matrix + spatial coordinates |

## Expected Outputs
| File | Description |
|------|-------------|
| `spatial_plot.png` | Color-coded spatial map (each color = one villus cluster) |
| `villus_assignments.csv` | cell_id, villus_cluster_id, is_epithelial, x, y |
| `per_villus_summary.csv` | villus_cluster_id, n_cells |

## Environment
- CPU only. `scanpy`, `squidpy`, `matplotlib`, `pandas`, `numpy`, `anndata`
