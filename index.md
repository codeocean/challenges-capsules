# Challenge Capsules Index

This index maps the cloned challenge capsules in this repository to the iteration-03 review summaries in [`review-challanges-iteration-03/`](review-challanges-iteration-03/).

## Scope

- This index covers the cloned capsules requested for verification: Challenges 02 through 16.
- The review bundle and the cloned capsules are aligned by challenge number and topic.
- Some review titles are shortened relative to the local capsule names, but they still refer to the same capsules.
- One concrete drift exists: the iteration-03 review marks Challenge 10 as missing a `README`, but this clone now includes [`challenge_10_neurobase_foundation_model_evaluation/code/README.md`](challenge_10_neurobase_foundation_model_evaluation/code/README.md).

## Review Sources

- [`review-challanges-iteration-03/index.md`](review-challanges-iteration-03/index.md)
- [`review-challanges-iteration-03/working-capsules-summary.md`](review-challanges-iteration-03/working-capsules-summary.md)

## Capsule Map

| # | Capsule Directory | Local README | Review Status | Iteration-03 Summary |
|---|---|---|---|---|
| 02 | `challenge_02_agentic_data_harmonization` | [`README.md`](challenge_02_agentic_data_harmonization/code/README.md) | Completed | [`challenge-02-review.md`](review-challanges-iteration-03/challenge-02-review.md) - 94.9% F1 cell-type harmonization with honest non-circular evaluation; agentic step present but adds little. |
| 03 | `challenge_03_enhancer_designer` | [`README.md`](challenge_03_enhancer_designer/code/README.md) | Completed | [`challenge-03-review.md`](review-challanges-iteration-03/challenge-03-review.md) - Genetic algorithm produces statistically stronger enhancer candidates, though scoring remains PWM-based rather than neural. |
| 04 | `challenge_04_light_sheet_alignment_qc` | [`README.md`](challenge_04_light_sheet_alignment_qc/code/README.md) | Completed | [`challenge-04-review.md`](review-challanges-iteration-03/challenge-04-review.md) - Strong multi-model QC pipeline with rich outputs; still validated only on synthetic data. |
| 05 | `challenge_05_automate_your_productivity` | [`README.md`](challenge_05_automate_your_productivity/code/README.md) | Partially completed | [`challenge-05-review.md`](review-challanges-iteration-03/challenge-05-review.md) - Pattern detection works, but the automation workflow is missing key artifacts like ICS output, approval logs, and audit trail outputs in the reviewed run. |
| 06 | `challenge_06_plasmid_forge` | [`README.md`](challenge_06_plasmid_forge/code/README.md) | Partially completed | [`challenge-06-review.md`](review-challanges-iteration-03/challenge-06-review.md) - Safety refusal works, but most plasmid design cases fail because part selection and assembly are too limited. |
| 07 | `challenge_07_engineering_automation` | [`README.md`](challenge_07_engineering_automation/code/README.md) | Completed | [`challenge-07-review.md`](review-challanges-iteration-03/challenge-07-review.md) - Bedrock-powered code-repair agent runs across 15 synthetic tasks with honest reporting and cost tracking. |
| 08 | `challenge_08_query_bff` | [`README.md`](challenge_08_query_bff/code/README.md) | Completed | [`challenge-08-review.md`](review-challanges-iteration-03/challenge-08-review.md) - Natural-language filtering over real BioFileFinder metadata; strongest practical capsule in the review set. |
| 09 | `challenge_09_bindcrafting` | [`README.md`](challenge_09_bindcrafting/code/README.md) | Partially completed | [`challenge-09-review.md`](review-challanges-iteration-03/challenge-09-review.md) - Binder analysis framework runs, but all candidates and scores are simulated and the GPU path is unused. |
| 10 | `challenge_10_neurobase_foundation_model_evaluation` | [`README.md`](challenge_10_neurobase_foundation_model_evaluation/code/README.md) | Blocked | [`challenge-10-review.md`](review-challanges-iteration-03/challenge-10-review.md) - Standalone runtime remains broken by environment and model-weight issues. Review says no `README`; this clone now has one. |
| 11 | `challenge_11_abc_atlas_literature_assistant` | [`README.md`](challenge_11_abc_atlas_literature_assistant/code/README.md) | Completed | [`challenge-11-review.md`](review-challanges-iteration-03/challenge-11-review.md) - Self-bootstrapping literature assistant retrieves real PubMed papers and verifies citations successfully. |
| 12 | `challenge_12_brain_map_bkp_assistant` | [`README.md`](challenge_12_brain_map_bkp_assistant/code/README.md) | Completed | [`challenge-12-review.md`](review-challanges-iteration-03/challenge-12-review.md) - Grounded assistant reports 86.7% overall accuracy with adversarial failures that show honest limits. |
| 13 | `challenge_13_croissant_pipeline` | [`README.md`](challenge_13_croissant_pipeline/code/README.md) | Completed | [`challenge-13-review.md`](review-challanges-iteration-03/challenge-13-review.md) - End-to-end Croissant packaging pipeline validates successfully on synthetic scRNA-seq data. |
| 14 | `challenge_14_segment_intestine_villi` | [`README.md`](challenge_14_segment_intestine_villi/code/README.md) | Completed | [`challenge-14-review.md`](review-challanges-iteration-03/challenge-14-review.md) - Spatial segmentation pipeline now produces GeoJSON boundaries and non-empty villus summaries on synthetic data. |
| 15 | `challenge_15_allen_single_cell_model_pantry` | [`README.md`](challenge_15_allen_single_cell_model_pantry/code/README.md) | Partially completed | [`challenge-15-review.md`](review-challanges-iteration-03/challenge-15-review.md) - Benchmark framework runs, but synthetic data is trivially separable and scVI stability remains questionable. |
| 16 | `challenge_16_scidex` | [`README.md`](challenge_16_scidex/code/README.md) | Completed | [`challenge-16-review.md`](review-challanges-iteration-03/challenge-16-review.md) - Persistent two-session hypothesis workflow works end-to-end with citation tracking and state evolution. |

## Alignment Notes

- Challenge 08 review title is more descriptive than the local folder name, but it clearly maps to `challenge_08_query_bff`.
- Challenges 10, 12, 15, and 16 use slightly different title formatting between the review docs and local `README`s.
- The only content mismatch found during verification is Challenge 10's `README` presence in the clone versus `README = No` in the iteration-03 review summary.
