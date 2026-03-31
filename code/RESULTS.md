# Results — Challenge 14: Segment Intestine Villi

## Evidence Strength: PARTIAL — Pipeline validated on simulated spatial data; real Xenium data not available

The segmentation pipeline runs end-to-end and produces **GeoJSON polygon boundaries for 7 villi** with per-villus metrics. However, all data is **simulated** because real Xenium ileum spatial transcriptomics data was not attached as a data asset.

## Why Data Is Simulated

The challenge requires 10x Genomics Xenium spatial transcriptomics data from intestinal tissue. This data:
- Is not included in the attached data assets
- Would need to be downloaded from 10x Genomics public datasets (~several GB)
- The pipeline generates realistic simulated data (2,769 cells with spatial coordinates and epithelial marker genes) as a proof-of-concept

## Evaluation Results

### Segmentation Output
| Metric | Value |
|--------|-------|
| **Total cells** | 2,769 |
| **Epithelial cells** | 1,384 |
| **Villi identified** | 7 |
| **Output format** | GeoJSON polygons |

### Per-Villus Summary (per_villus_summary.csv)
| Villus | Cells | Area (μm²) | Mean Epithelial Score |
|--------|-------|------------|----------------------|
| 0 | 170 | 19,756 | 3.06 |
| 1 | 211 | 20,759 | 3.04 |
| 2 | 369 | 36,180 | 3.15 |
| 3 | 190 | 14,754 | 3.29 |
| 4 | 107 | 25,780 | 3.15 |
| 5 | 228 | 18,078 | 3.36 |
| 6 | 109 | 30,636 | 3.44 |

## What the Evidence Shows
- **Complete pipeline:** Epithelial scoring → spatial clustering → polygon boundary generation → QC visualization
- **GeoJSON output:** Machine-readable villus boundaries usable in downstream analysis
- **Realistic structure:** 7 villi with biologically plausible cell counts (107-369) and areas
- **Marker gene scoring:** Uses EPCAM, FABP1, FABP2, VIL1 for epithelial identification

## What Would Complete This
- Attach real Xenium ileum data (10x Genomics public dataset) as a data asset
- The pipeline accepts any AnnData with spatial coordinates and gene expression via `--input` flag
- Expected: similar villus identification on real tissue, with validation against manual annotations

## Output Artifacts
| File | Description |
|------|-------------|
| `villus_boundaries.geojson` (11 KB) | GeoJSON polygon boundaries per villus |
| `villus_assignments.csv` (66 KB) | Cell-to-villus cluster assignments |
| `per_villus_summary.csv` | Per-villus metrics |
| `spatial_plot.png` (253 KB) | Spatial visualization of segmented villi |
| `data_provenance.json` | Data source documentation (synthetic) |
