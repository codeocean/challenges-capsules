# Challenge 10 — NeuroBase Foundation Model Evaluation

## Original Challenge
Benchmark the NeuroBase 3D neuroanatomical foundation model on Allen brain imaging data, comparing downstream task performance against conventional baselines.

## Intended Goal
Load real Allen CCFv3 brain volumes, extract patches, run them through the NeuroBase encoder, classify brain regions with LogisticRegression, and compare against random-weights and classical baselines.

## Initial State
Code existed for the full pipeline including AllenSDK data download, synthetic fallback, proxy encoder, and baseline comparison. The entrypoint was fixed to a clean bash launcher.

## Improvement Plan
Fix data loading (download Allen CCFv3 at runtime or use synthetic), ensure the baseline path works without NeuroBase weights, and produce honest metrics.

## Final Implementation
The code downloads Allen CCFv3 data via requests or AllenSDK (with synthetic fallback), extracts 3D patches, runs both a proxy 3D CNN encoder and a random-weights baseline, trains LogisticRegression classifiers, and reports per-region metrics.

## Final Result
The capsule does not produce standalone results. The latest bare run (597 seconds, exit 1) fails without producing output. A previous build attempt also failed (9 seconds, build failure). The code has all the right components but the runtime consistently crashes.

## Evaluation
Blocked. The capsule cannot run standalone. Multiple attempts have been made to fix the environment (removing allensdk, adjusting package versions) but the runtime continues to fail. Prior CC-orchestrated runs produced valid results (summary.json, opportunity_analysis.json, figures/), proving the code works in a CC environment, but the standalone execution path is broken.

## Remaining Limitations
NeuroBase model weights are unavailable (organizer-provided). Even the baseline path crashes on standalone execution. The environment has compatibility issues between PyTorch 2.4, CUDA 12.4, and the required scientific packages. The Allen data download path may timeout in the run environment.

## Overall Verdict
Blocked. This is the only capsule that cannot run standalone. The code and logic are sound (proven by prior CC runs), but the environment/runtime combination prevents standalone execution. Needs environment debugging.

## Usage Documentation
No README because the capsule is not usable standalone.

## Final Runnable State
The `/code/run` entrypoint is clean, but the capsule fails at runtime. Not usable without fixing the environment.
