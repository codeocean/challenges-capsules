# Challenge 09 — BindCrafting

## Original Challenge
Design protein binders using BindCraft and AlphaFold2 for target proteins, generating fluorescent-compatible affinity reagents with structural validation.

## Intended Goal
Run real protein design software (BindCraft, RFdiffusion, ProteinMPNN) on GPU to generate binder candidates against target PDB structures, filter by AF2 quality metrics, check fusion compatibility, and produce a wet-lab synthesis package.

## Initial State
A simulation pipeline existed that generated synthetic BindCraft-like scores and candidates. No real protein design code was present. GPU was recently upgraded to g6e.8xlarge (L40S, 46GB VRAM).

## Improvement Plan
With GPU now available, attempt real BindCraft installation and a smoke test. If blocked, improve the simulation pipeline with real target PDB structures and honest labeling.

## Final Implementation
The capsule generates synthetic binder candidates with realistic AF2-like metrics, loads a real target PDB (1RK9 Parvalbumin), applies predeclared filtering thresholds (iPTM >= 0.7, pLDDT >= 80, PAE <= 10), checks fluorescent fusion compatibility via terminus distances, and uses Bedrock for scientific interpretation. Visualizations are generated for score distributions and filtering funnels.

## Final Result
Produces ranked_candidates.csv (750B, top 5 candidates), fusion_compatibility.json, filtering_funnel.json, top5_visualizations/, and agent_analysis.md. All candidates are simulated with realistic but fabricated scores.

## Evaluation
The capsule runs standalone (exit 0) and demonstrates the complete analysis framework. However, no real protein design computation occurs. The code does not import BindCraft, AlphaFold2, or any protein design software. The GPU is provisioned but completely unused.

## Remaining Limitations
All binder candidates are simulated. No real BindCraft or AF2 code exists in the capsule. GPU hardware is available but unused. The analysis pipeline is a framework demonstration, not real protein design. Significant new development would be needed to integrate actual design software.

## Overall Verdict
Partially completed. The analysis and filtering framework works, but the core challenge — actually designing protein binders computationally — is not addressed. The capsule is a demonstration of what the post-design analysis would look like.

## Usage Documentation
The capsule has a README.md.

## Final Runnable State
Clean `/code/run` entrypoint. Runs standalone.
