# Results — Challenge 14: Segment Intestine Villi

## Latest Successful Run
- **Computation ID:** `44736dab-fca3-4702-83e6-2de1732e080c`
- **Status:** Succeeded (exit code 0)
- **Runtime:** 49 seconds

## Evaluation Results

### Segmentation Outputs
- **Villus boundaries:** GeoJSON polygon file (11 KB)
- **Per-villus summary:** CSV with villus metrics (309 bytes)
- **Cell assignments:** 66 KB CSV mapping cells to villi

### Pipeline
- Spatial data (simulated, marked as PARTIAL pending real Xenium data)
- Epithelial cell identification using marker genes (EPCAM, FABP1, FABP2, VIL1)
- Leiden clustering for villus assignment
- Alpha-shape polygon boundary generation

## Output Artifacts
| File | Description |
|------|-------------|
| `villus_boundaries.geojson` (11 KB) | GeoJSON polygon boundaries per villus |
| `villus_assignments.csv` (66 KB) | Cell-to-villus assignments |
| `per_villus_summary.csv` | Per-villus metrics (area, cell count) |
| `spatial_plot.png` (253 KB) | Spatial visualization |
| `data_provenance.json` | Data source documentation |
