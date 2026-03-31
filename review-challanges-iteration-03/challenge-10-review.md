# Challenge 10 — NeuroBase Foundation Model Evaluation

## Original Challenge
Benchmark the NeuroBase 3D neuroanatomical foundation model on Allen brain imaging data, comparing downstream task performance against conventional baselines.

## Intended Goal
Load real Allen CCFv3 brain volumes, extract patches, run them through the NeuroBase encoder, classify brain regions with LogisticRegression, and compare against random-weights and classical baselines.

## Initial State
An early pipeline existed but the benchmark quality was poor: region mapping was not anatomically meaningful, intensity could be derived from labels, the test split had almost no regional coverage, and the so-called pretrained path was not actually pretrained.

## Improvement Plan
Replace the fragile prototype with a self-contained runtime download path for Allen CCFv3 data, ontology-based region collapsing, a legitimate conventional baseline, an actual self-supervised proxy encoder, denser patch extraction, and a fuller output packet with honest metrics.

## Final Implementation
The capsule downloads the Allen CCFv3 annotation volume, average template intensity volume, and structure ontology at runtime; walks the ontology tree to collapse labels into 12 coarse brain regions; extracts 345 overlapping 3-D patches with a stratified 80/20 split; and benchmarks three encoders:

- Classical hand-crafted features
- A self-supervised 3-D CNN proxy pretrained by rotation prediction
- A random-weight CNN baseline

It writes 17 result files including summary.json, dice_scores.csv, evaluation_report.md, opportunity_analysis.json, overlay figures, a Dice comparison bar chart, a confusion matrix, and reusable embeddings.

## Final Result
The standalone run now succeeds and produces a meaningful benchmark packet. Verified results in the current README report:

- Classical features mean Dice = 0.3671, macro F1 = 0.4005
- Pretrained proxy mean Dice = 0.3228, macro F1 = 0.3522
- Random baseline mean Dice = 0.1416, macro F1 = 0.1545

The pretrained proxy improves over random by 2.28x, and the classical baseline is the strongest overall reference at this scale.

## Evaluation
Completed. The capsule now runs standalone, uses real Allen CCFv3 downloads on the primary path, covers 11 of 12 target regions in the test split, and produces scientifically interpretable comparisons instead of a nominal pass-through demo. This is now a legitimate benchmark harness rather than a blocked prototype.

## Remaining Limitations
Organizer-provided NeuroBase weights are still unavailable, so the "pretrained" path defaults to a self-supervised proxy unless a checkpoint is attached. The benchmark is patch-level rather than voxel-dense segmentation, uses one Allen template volume rather than a multi-volume study, and still depends on successful runtime download of public Allen assets.

## Overall Verdict
Completed. Challenge 10 has moved from blocked to runnable. The benchmark now stands on real Allen data, anatomically grounded region mapping, honest baselines, and a reusable result bundle.

## Usage Documentation
The capsule has a detailed README.md covering the pipeline, verified results, artifact inventory, runtime profile, and changelog.

## Final Runnable State
The `/code/run` entrypoint is clean and the current reviewed version runs standalone with runtime Allen downloads. Real NeuroBase weights remain optional rather than required for the default path.
