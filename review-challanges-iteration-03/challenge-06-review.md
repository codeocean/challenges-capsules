# Challenge 06 — Plasmid Forge

## Original Challenge
Build a natural-language-to-plasmid design workflow that converts biological requests into synthesis-ready constructs with Gibson Assembly, part retrieval, validation, and safety screening.

## Intended Goal
Parse natural language requests, select genetic parts from registries, assemble circular plasmids, validate designs, screen for safety, and handle ambiguous or dangerous requests.

## Initial State
A Strands Agent + pydna pipeline existed but used fake parts and lacked validation. The pipeline was expanded to 22KB run.py with Bedrock integration and heuristic fallback.

## Improvement Plan
Add real parts library, synthesis-readiness validation, safety screening, codon optimization, multi-request test suite with 6 test cases including toxin refusal and ambiguity handling.

## Final Implementation
The capsule parses requests via Bedrock (with heuristic fallback), selects parts from a curated library, assembles a plasmid using BioPython, and outputs annotated GenBank files. A 6-case evaluation suite tests standard, therapeutic, high-copy, safety, regulated, and vague requests.

## Final Result
Produces construct.gb, evaluation_summary.json, manifest.json, protocol.md, and test_cases/. However, the evaluation shows only 1/6 cases pass — the safety refusal case. The other 5 cases fail because the part selection logic is too limited and the construct is only 286 bytes.

## Evaluation
The capsule runs standalone (exit 0). Safety screening correctly refuses the toxin request. However, core plasmid design fails for 5 of 6 test cases. The heuristic parser works but the part library and assembly logic are insufficient to produce real constructs.

## Remaining Limitations
Core design failure rate of 83%. The part library is too small for diverse requests. Assembly produces minimal constructs. Bedrock integration works for parsing but not for full design. The challenge's main value proposition — generating real plasmid designs — is not achieved.

## Overall Verdict
Partially completed. The framework and safety screening work, but the core design capability is weak. Significant additional work on part selection and assembly is needed.

## Usage Documentation
The capsule has a README.md.

## Final Runnable State
Clean `/code/run` entrypoint. Runs standalone.
