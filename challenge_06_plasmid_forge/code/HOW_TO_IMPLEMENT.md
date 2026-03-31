# How to Implement: Plasmid Forge — For Your Own Data

> **Goal**: Convert a natural-language biological request into a synthesis-ready
> plasmid construct with Gibson Assembly design, part selection, validation,
> and complete documentation.

---

## 1. What You Need (Your Data)

### Input Data Format

| Input | Format | Description |
|-------|--------|-------------|
| **Biological request** | Plain text file (`request.txt`) | Natural language describing what you want to express and in what system |
| **Parts library** | GenBank files (`.gb`) in a folder | Your collection of promoters, RBS, terminators, genes, resistance markers |
| **Backbone vectors** | GenBank files (`.gb`) in a folder | Standard plasmid backbones for your expression system |

### What Your Data Should Look Like

```
# request.txt — a single line or short paragraph
"Express human EGFP with a T7 promoter in E. coli BL21 with kanamycin resistance and a 6xHis tag for purification"
```

```
my_parts/
├── parts_library/
│   ├── T7_promoter.gb
│   ├── lac_promoter.gb
│   ├── strong_RBS.gb
│   ├── T7_terminator.gb
│   ├── EGFP.gb
│   ├── mCherry.gb
│   ├── kanR.gb
│   ├── ampR.gb
│   └── 6xHis_tag.gb
├── backbones/
│   ├── pET28a.gb
│   ├── pUC19.gb
│   └── pBAD33.gb
└── request.txt
```

**Key requirements:**
- GenBank files must have proper annotations (features, sequences)
- Parts should be 50bp–5kb each
- Request should specify: gene of interest, expression system, selection marker, and any tags

---

## 2. Step-by-Step: Recreate This Capsule with Aqua

### Step 1: Create a New Capsule

> **Ask Aqua:**
> *"Create a new capsule called 'Plasmid Design — [My Project]' with Python 3.10, and install packages: biopython, pydna, pydantic, boto3"*

### Step 2: Prepare Your Parts Library

> **Ask Aqua:**
> *"Create a data asset called 'my-plasmid-parts' and attach it to my capsule at /data/plasmid_parts"*

Upload your parts and backbone GenBank files. If you don't have a curated library:

> **Ask Aqua:**
> *"Generate a starter parts library with common E. coli expression parts: T7/lac/trc promoters, strong/medium RBS options, rrnB/T7 terminators, ampR/kanR/cmR resistance markers, and common tags (6xHis, FLAG, GST)"*

### Step 3: Write Your Request

Create a `request.txt` in your data asset or pass it as a parameter:

> **Ask Aqua:**
> *"Set up an App Panel parameter called 'request' (text type) so I can type my biological request when running the capsule"*

### Step 4: Run

> **Ask Aqua:**
> *"Run my capsule with request='Express human insulin B chain with T7 promoter in E. coli BL21(DE3) with ampicillin resistance and N-terminal 6xHis tag'"*

---

## 3. Outputs You'll Get

| File | What It Contains |
|------|-----------------|
| `construct.gb` | Complete annotated circular plasmid GenBank file |
| `manifest.json` | Every design decision: parts selected, alternatives considered, rationale |
| `protocol.md` | Step-by-step Gibson Assembly protocol with primer sequences |

---

## 4. Adapting for Different Use Cases

### Use Case A: Mammalian expression (not E. coli)
Swap the parts library for mammalian promoters/terminators.

> **Ask Aqua:**
> *"Modify the parts library to include CMV/EF1a/CAG promoters, SV40/bGH polyA terminators, and mammalian selection markers (puromycin, hygromycin, neomycin)"*

### Use Case B: Multi-gene constructs
Design operons or multi-cistonic constructs.

> **Ask Aqua:**
> *"Extend the pipeline to handle multi-gene requests like 'co-express GFP and mCherry with individual RBS elements in an operon configuration'"*

### Use Case C: Golden Gate instead of Gibson Assembly
Switch the assembly method.

> **Ask Aqua:**
> *"Replace the Gibson Assembly design with Golden Gate (BsaI-based). Add Type IIS restriction site checks and ensure no internal BsaI sites in parts."*

---

## 5. Tips

- **Validate in silico**: Open the `.gb` file in SnapGene Viewer (free) or Benchling to verify annotations
- **Check overhangs**: Gibson Assembly needs 20–40bp overlaps — the pipeline calculates these automatically
- **Codon optimization**: If expressing heterologous genes, consider adding a codon optimization step
- **Safety screening**: The pipeline checks for known hazardous sequences — review the manifest for any flags
- **Iterate**: If the first design isn't right, refine your request with more specific constraints

---

## 6. Environment Requirements

| Package | Purpose |
|---------|---------|
| `biopython` | GenBank I/O, sequence manipulation |
| `pydna` | Assembly simulation, primer design |
| `pydantic` | Data validation |
| `boto3` | AWS Bedrock for NL parsing (optional) |

**Compute**: CPU only, X-Small tier sufficient
