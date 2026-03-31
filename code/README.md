# Challenge 06: Plasmid Forge


## Results Summary
- **Test Cases:** 6 | **Passed:** 1/6 (17%)
- **Safety Screening:** ✅ Correctly refuses toxin requests
- **Construct Output:** GenBank format

> See [RESULTS.md](RESULTS.md) for per-case test results and details.

## What This Capsule Does

Takes a one-line biological request (e.g., "express GFP in E. coli with kanamycin
resistance"), uses an LLM to parse intent, selects from ~20 pre-curated genetic parts,
assembles a circular plasmid with Biopython, and outputs an annotated GenBank file
plus an assumptions manifest.

## Evaluation Criteria

The .gb file opens correctly in SnapGene/Benchling showing the right parts in the
right order and orientation.

## Required Data Assets

| File | Description |
|------|-------------|
| `request.txt` | One-line biological request |
| `parts_library/` | ~20 GenBank files of common parts (promoters, RBS, terminators, genes, resistance) |
| `backbones/` | 5–10 standard backbone vectors as .gb files |

## Expected Outputs

| File | Description |
|------|-------------|
| `construct.gb` | Annotated circular plasmid GenBank file |
| `manifest.json` | Every assumption: parts selected, alternatives, rationale |
| `protocol.md` | Simple Gibson Assembly protocol |

## Environment

- Python 3.10+, CPU only
- `biopython`, `pydna`, `anthropic` (or `openai`), `pydantic`
