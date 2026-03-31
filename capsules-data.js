window.CAPSULES = [
  {
    id: "challenge-02",
    number: "02",
    title: "Agentic Data Harmonization",
    directory: "challenge_02_agentic_data_harmonization",
    status: "completed",
    statusLabel: "Completed",
    problem:
      "Map cell type labels across neuroscience datasets that use different taxonomies and naming conventions.",
    capsuleSummary:
      "The capsule aligns labels to Cell Ontology terms using fuzzy matching, synonym lookup, and Bedrock support for ambiguous cases.",
    solution: [
      "This codebase solves the problem by loading labels from two sources, searching Cell Ontology for likely matches, and assigning each label into mapped, needs-review, or unmapped buckets with confidence scores.",
      "The reviewed implementation adds an independent evaluation set and honest precision, recall, and F1 reporting, which makes the harmonization quality inspectable instead of circular."
    ],
    usageMode: "Attach data asset and run",
    usageSteps: [
      "Attach a data asset that includes labels_a.csv, labels_b.csv, cl.obo, and gold_mappings.csv.",
      "Click Reproducible Run to generate mapping_table.csv and eval_report.json.",
      "Use the report to inspect overall mapping quality and open the table when you want per-label provenance."
    ],
    inputs: [
      "labels_a.csv and labels_b.csv with source labels",
      "cl.obo Cell Ontology file",
      "gold_mappings.csv for evaluation"
    ],
    outputs: ["mapping_table.csv", "eval_report.json"],
    runModes: ["Data asset", "Reproducible Run"],
    flags: ["data-asset", "bedrock", "real-data"],
    notes:
      "Review status is Completed. The agentic step exists, but the review notes that it added little value over the deterministic matcher in the latest run.",
    readmePath: "./challenge_02_agentic_data_harmonization/code/README.md",
    reviewPath: "./review-challanges-iteration-03/challenge-02-review.md"
  },
  {
    id: "challenge-03",
    number: "03",
    title: "Enhancer Designer",
    directory: "challenge_03_enhancer_designer",
    status: "completed",
    statusLabel: "Completed",
    problem:
      "Design synthetic enhancer DNA sequences that score better than controls while staying manufacturable and diverse.",
    capsuleSummary:
      "The capsule uses a configurable genetic algorithm, PWM-based scoring, filters, and diversity selection to produce candidate enhancer sequences.",
    solution: [
      "The codebase starts from seed sequences, scores them for motif quality, cooperativity, GC balance, and complexity, then evolves them through mutation, crossover, and elitist selection.",
      "It packages the result as a reproducible design loop with statistical comparisons against random, shuffled, and seed controls so the final FASTA is backed by explicit evidence."
    ],
    usageMode: "Use App Panel, optionally attach data",
    usageSteps: [
      "Open the App Panel and set the design parameters such as generations, population size, mutation rate, and top-k finalists.",
      "Run the capsule as-is for a self-contained demo, or attach optional data like /data/k562_peaks.fasta or model weights if you want to ground the run in external inputs.",
      "Review top20.fasta, stats.json, the report figure, and run_manifest.yaml to understand what changed and why."
    ],
    inputs: [
      "No required asset for the default run",
      "Optional FASTA input for real K562 peaks",
      "Optional model weights for alternate scoring"
    ],
    outputs: ["top20.fasta", "stats.json", "enhancer_report.png", "run_manifest.yaml"],
    runModes: ["App Panel", "Reproducible Run", "Optional data asset"],
    flags: ["app-panel", "self-contained", "synthetic-data"],
    notes:
      "Review status is Completed. The main limitation is that scoring remains PWM-based rather than neural, even though the output quality is still strong.",
    readmePath: "./challenge_03_enhancer_designer/code/README.md",
    reviewPath: "./review-challanges-iteration-03/challenge-03-review.md"
  },
  {
    id: "challenge-04",
    number: "04",
    title: "Light Sheet Alignment QC",
    directory: "challenge_04_light_sheet_alignment_qc",
    status: "completed",
    statusLabel: "Completed",
    problem:
      "Detect alignment failures in light-sheet microscopy registration and separate confident passes from cases that need human review.",
    capsuleSummary:
      "The capsule generates image pairs, extracts QC features, evaluates multiple models, calibrates thresholds, and produces a full visual report.",
    solution: [
      "This codebase treats QC as a structured ML pipeline: synthetic image-pair generation, feature extraction, model training, calibration, and visual diagnostics.",
      "Instead of returning a single score, it produces pass, fail, and needs-review outputs along with galleries and curves that make model behavior easy to inspect in a capsule setting."
    ],
    usageMode: "Run directly",
    usageSteps: [
      "Click Reproducible Run. The current capsule is self-contained and generates its own synthetic test data.",
      "Wait for the pipeline to finish, then open evaluation_report.html as the primary artifact.",
      "Use the plots, confusion matrix, and per-pair predictions to understand where the QC model is strong or uncertain."
    ],
    inputs: ["No external data asset required for the reviewed run"],
    outputs: ["evaluation_report.html", "predictions.csv", "metrics.json", "figures and diagnostic plots"],
    runModes: ["Self-contained", "Reproducible Run"],
    flags: ["self-contained", "synthetic-data"],
    notes:
      "Review status is Completed. The major caveat is that the demonstrated validation is synthetic rather than based on real microscopy pairs.",
    readmePath: "./challenge_04_light_sheet_alignment_qc/code/README.md",
    reviewPath: "./review-challanges-iteration-03/challenge-04-review.md"
  },
  {
    id: "challenge-05",
    number: "05",
    title: "Automate Your Productivity",
    directory: "challenge_05_automate_your_productivity",
    status: "partial",
    statusLabel: "Partially completed",
    problem:
      "Analyze calendar and email behavior to identify productivity anti-patterns and propose safe automations with human oversight.",
    capsuleSummary:
      "The capsule uses a Bedrock-driven analysis loop over synthetic calendar and email scenarios and exposes both a batch run and a Streamlit interface.",
    solution: [
      "The codebase frames productivity support as an agentic analysis problem, with tools for calendar load, recurring meetings, stale email threads, focus time, and cross-referencing.",
      "It then synthesizes ranked proposals from those signals, which is a good fit for a capsule because the outputs are structured enough to inspect, compare, and eventually approve."
    ],
    usageMode: "Batch run or Cloud Workstation",
    usageSteps: [
      "Use Reproducible Run to execute both built-in scenarios and generate the scenario output folders and manifest.",
      "If you want the interactive experience, launch the Cloud Workstation and open the Streamlit app in /code/streamlit_app.py.",
      "Treat the current capsule as a pattern-analysis demo rather than a full automation engine because the reviewed run is missing several promised workflow artifacts."
    ],
    inputs: ["No external data asset required for the default scenarios"],
    outputs: ["scenario summaries", "proposals.json", "manifest.json", "comparison_report.md"],
    runModes: ["Reproducible Run", "Cloud Workstation", "Streamlit"],
    flags: ["interactive", "bedrock", "self-contained"],
    notes:
      "Review status is Partially completed. The review explicitly calls out missing ICS output, approval logs, and audit-trail artifacts in the latest results.",
    readmePath: "./challenge_05_automate_your_productivity/code/README.md",
    reviewPath: "./review-challanges-iteration-03/challenge-05-review.md"
  },
  {
    id: "challenge-06",
    number: "06",
    title: "Plasmid Forge",
    directory: "challenge_06_plasmid_forge",
    status: "partial",
    statusLabel: "Partially completed",
    problem:
      "Turn a one-line biological request into a plasmid design with selected parts, assembly logic, and safety handling.",
    capsuleSummary:
      "The capsule parses the request, chooses from a curated part library, assembles a construct with Biopython, and emits a GenBank file plus a manifest.",
    solution: [
      "The codebase uses an LLM-assisted interpretation layer followed by deterministic design logic for part selection, plasmid construction, and output packaging.",
      "That makes it a natural Code Ocean capsule because the result is inspectable as files: construct.gb, a manifest of assumptions, and a protocol that explains how the design was assembled."
    ],
    usageMode: "Attach biological design inputs",
    usageSteps: [
      "Attach a data asset that includes request.txt, parts_library/, and backbones/.",
      "Run the capsule to generate construct.gb, manifest.json, and protocol.md.",
      "Open the GenBank output in Benchling or SnapGene if you want to inspect the annotated construct outside the capsule."
    ],
    inputs: ["request.txt", "parts_library/ with GenBank parts", "backbones/ with standard vectors"],
    outputs: ["construct.gb", "manifest.json", "protocol.md"],
    runModes: ["Data asset", "Reproducible Run"],
    flags: ["data-asset", "bedrock"],
    notes:
      "Review status is Partially completed. Safety refusal works, but most standard design requests still fail because the part selection and assembly logic are too limited.",
    readmePath: "./challenge_06_plasmid_forge/code/README.md",
    reviewPath: "./review-challanges-iteration-03/challenge-06-review.md"
  },
  {
    id: "challenge-07",
    number: "07",
    title: "Engineering Automation",
    directory: "challenge_07_engineering_automation",
    status: "completed",
    statusLabel: "Completed",
    problem:
      "Automate code maintenance tasks by having an AI agent inspect repos, propose fixes, run tests, and report what worked.",
    capsuleSummary:
      "The capsule stages bug-fix tasks, runs an edit-test-retry loop with Bedrock, and exports patches, per-task summaries, and an aggregate dashboard.",
    solution: [
      "This codebase turns repo maintenance into a reproducible benchmark: each task contains a repo snapshot, a failure description, and a validation path.",
      "The agent loop clones the task repo, runs tests, applies candidate fixes, retries within budget, and records cost and status so the capsule behaves like a measurable maintenance experiment."
    ],
    usageMode: "Attach task bundles and run",
    usageSteps: [
      "Attach a data asset containing repos/*.bundle and tasks.jsonl if you want to evaluate your own maintenance tasks.",
      "Run the capsule and inspect patches/, reports/, and dashboard.json after completion.",
      "Use the dashboard to separate resolved tasks from already-passing, budget-exhausted, and regression cases."
    ],
    inputs: ["repos/*.bundle", "tasks.jsonl with repo, issue text, and test selectors"],
    outputs: ["patches/", "reports/", "dashboard.json"],
    runModes: ["Data asset", "Reproducible Run"],
    flags: ["data-asset", "bedrock"],
    notes:
      "Review status is Completed. The resolution rate is modest, but the review treats the honest reporting and cost tracking as strengths rather than defects.",
    readmePath: "./challenge_07_engineering_automation/code/README.md",
    reviewPath: "./review-challanges-iteration-03/challenge-07-review.md"
  },
  {
    id: "challenge-08",
    number: "08",
    title: "Your Query BFF",
    directory: "challenge_08_query_bff",
    status: "completed",
    statusLabel: "Completed",
    problem:
      "Translate natural-language questions about BioFileFinder metadata into validated filters that can be executed on a manifest.",
    capsuleSummary:
      "The capsule extracts schema from a BFF manifest, uses Bedrock to build grounded filters, and returns structured answers for either one query or a whole evaluation set.",
    solution: [
      "The codebase solves the problem with a clean two-stage pattern: first derive a schema from the manifest, then constrain the language model to produce filters that can be validated and executed safely.",
      "That makes the capsule directly useful in Code Ocean because users can either ask one question through Aqua or App Panel, or run the evaluation mode to audit overall quality."
    ],
    usageMode: "Aqua or App Panel query flow",
    usageSteps: [
      "For one question, ask Aqua to run the capsule with a named query parameter, or open the App Panel and set the Query field directly.",
      "For example, pass query=\"Show me lamin B1 images\" and inspect query_answer.json for filters, explanation, and matching rows.",
      "If you leave the query empty and run the capsule, it switches into evaluation mode and writes evaluation_report.json."
    ],
    inputs: [
      "Optional bff_manifest.parquet to use your own metadata manifest",
      "Optional eval_queries.json for a custom evaluation set"
    ],
    outputs: ["query_answer.json", "evaluation_report.json", "extracted_schema.json"],
    runModes: ["Aqua", "App Panel", "Reproducible Run", "Optional data asset"],
    flags: ["aqua", "app-panel", "bedrock", "real-data"],
    notes:
      "Review status is Completed and especially strong. The review treats this as the most immediately useful capsule because it works on real Allen Cell Collection metadata.",
    readmePath: "./challenge_08_query_bff/code/README.md",
    reviewPath: "./review-challanges-iteration-03/challenge-08-review.md"
  },
  {
    id: "challenge-09",
    number: "09",
    title: "BindCrafting",
    directory: "challenge_09_bindcrafting",
    status: "partial",
    statusLabel: "Partially completed",
    problem:
      "Design or at least analyze protein binders against a neuroscience target and package the results as a decision-ready panel.",
    capsuleSummary:
      "The capsule filters and ranks synthetic binder candidates, checks fusion compatibility against a real target structure, and writes a scientific analysis report.",
    solution: [
      "The codebase solves the downstream analysis part of the problem by treating each candidate like a scored design artifact with clear filtering thresholds, structure-derived compatibility checks, and a narrative interpretation layer.",
      "In capsule form that means users can inspect the funnel, candidate ranking, and fusion distances even though the reviewed pipeline is not yet running real binder design software."
    ],
    usageMode: "Run the analysis demo",
    usageSteps: [
      "Click Reproducible Run. The current reviewed version does not require an external asset for the default path.",
      "Open ranked_candidates.csv, filtering_funnel.json, and fusion_compatibility.json to inspect the short-listed panel.",
      "Read the results as a framework demonstration for post-design analysis, not as a real BindCraft or AlphaFold2 generation workflow."
    ],
    inputs: ["No required asset for the reviewed synthetic-analysis path"],
    outputs: ["ranked_candidates.csv", "fusion_compatibility.json", "filtering_funnel.json", "agent_analysis.md"],
    runModes: ["Reproducible Run", "Self-contained"],
    flags: ["self-contained", "bedrock", "synthetic-data"],
    notes:
      "Review status is Partially completed. The GPU path is currently unused and all candidate metrics are simulated rather than generated by real design software.",
    readmePath: "./challenge_09_bindcrafting/code/README.md",
    reviewPath: "./review-challanges-iteration-03/challenge-09-review.md"
  },
  {
    id: "challenge-10",
    number: "10",
    title: "NeuroBase Foundation Model Evaluation",
    directory: "challenge_10_neurobase_foundation_model_evaluation",
    status: "completed",
    statusLabel: "Completed",
    problem:
      "Benchmark a 3D neuroanatomical foundation model on Allen brain imaging volumes against random or baseline encoders.",
    capsuleSummary:
      "Standalone benchmark harness that downloads real Allen CCFv3 data, builds ontology-based region labels, compares classical, self-supervised, and random encoders, and writes a full evaluation packet.",
    solution: [
      "The pipeline now bootstraps itself from public Allen assets at runtime: annotation volume, average template intensity volume, and the structure ontology used to collapse fine labels into 12 anatomically meaningful regions.",
      "It then extracts 3-D patches, trains LogisticRegression probes on three embedding families, and produces both compact metrics and a richer artifact set including reports, overlays, per-region comparisons, confusion matrix, and reusable embeddings."
    ],
    usageMode: "Reproducible run with optional NeuroBase weights",
    usageSteps: [
      "Click Reproducible Run. No required data asset is needed for the default benchmark path because the capsule downloads Allen CCFv3 inputs at runtime and caches them under /scratch/allen.",
      "Inspect summary.json, dice_scores.csv, evaluation_report.md, opportunity_analysis.json, and the figure outputs to compare the three encoder baselines.",
      "If real NeuroBase weights become available, attach /data/neurobase_weights/ with a .pt or .pth checkpoint and rerun to replace the self-supervised proxy encoder."
    ],
    inputs: [
      "No required asset for the default baseline benchmark path",
      "Optional: /data/neurobase_weights/*.pt or *.pth to replace the self-supervised proxy"
    ],
    outputs: [
      "summary.json",
      "dice_scores.csv",
      "evaluation_report.md",
      "opportunity_analysis.json",
      "overlay images",
      "dice_barplot.png",
      "confusion_matrix.png",
      "embeddings/*.npy"
    ],
    runModes: ["Reproducible Run", "Self-contained baseline", "Optional model asset"],
    flags: ["self-contained"],
    notes:
      "Review status is Completed. The remaining limitation is scientific rather than operational: true NeuroBase weights are still unavailable, so the pretrained path uses a self-supervised proxy unless a checkpoint is attached.",
    readmePath: "./challenge_10_neurobase_foundation_model_evaluation/code/README.md",
    reviewPath: "./review-challanges-iteration-03/challenge-10-review.md"
  },
  {
    id: "challenge-11",
    number: "11",
    title: "ABC Atlas Literature Assistant",
    directory: "challenge_11_abc_atlas_literature_assistant",
    status: "completed",
    statusLabel: "Completed",
    problem:
      "Answer questions about the ABC Atlas by retrieving papers, labeling their relationship to the atlas, and citing grounded evidence.",
    capsuleSummary:
      "The capsule assembles or loads a literature corpus, retrieves relevant papers, classifies the relationship of each paper, and writes answer and evaluation artifacts.",
    solution: [
      "This codebase solves the problem by combining retrieval, relation labeling, and citation verification in one reproducible pipeline rather than leaving the answer as free-form LLM text.",
      "The review notes that the standalone implementation can bootstrap a real PubMed-backed corpus, which makes the capsule much more robust than a static demo."
    ],
    usageMode: "Run with your own corpus or use the built-in bootstrap path",
    usageSteps: [
      "Attach seed_papers.jsonl, paper_embeddings.npy, abc_taxonomy.json, and eval_queries.json if you want to evaluate your own literature pack.",
      "If you simply run the reviewed standalone capsule, it can also bootstrap a default corpus and query set from PubMed-backed logic.",
      "Inspect demo_outputs.json and eval_report.json to verify that answers cite papers that actually exist in the loaded corpus."
    ],
    inputs: [
      "seed_papers.jsonl and paper embeddings for a custom corpus",
      "abc_taxonomy.json and eval_queries.json for custom evaluation"
    ],
    outputs: ["demo_outputs.json", "eval_report.json"],
    runModes: ["Data asset", "Standalone bootstrap", "Reproducible Run"],
    flags: ["data-asset", "bedrock", "real-data"],
    notes:
      "Review status is Completed. The strongest part of the reviewed implementation is that it verifies citations against a real corpus rather than inventing references.",
    readmePath: "./challenge_11_abc_atlas_literature_assistant/code/README.md",
    reviewPath: "./review-challanges-iteration-03/challenge-11-review.md"
  },
  {
    id: "challenge-12",
    number: "12",
    title: "Brain Map + BKP Assistant",
    directory: "challenge_12_brain_map_bkp_assistant",
    status: "completed",
    statusLabel: "Completed",
    problem:
      "Build a grounded assistant over Allen Institute product resources that can retrieve, explain, and cite the right pages.",
    capsuleSummary:
      "The capsule indexes a corpus of Allen resource pages, answers queries with citations, and reports top-5 retrieval accuracy including adversarial cases.",
    solution: [
      "The codebase solves the problem with a retrieval-first design that keeps answers tied to URLs, product groupings, and evaluation targets.",
      "What makes it valuable as a capsule is the evaluation discipline: it measures easy, medium, cross-product, and adversarial behavior so users can see where the assistant is reliable and where it breaks."
    ],
    usageMode: "Run built-in corpus or attach your own",
    usageSteps: [
      "Attach corpus.jsonl and eval_queries.jsonl if you want to benchmark your own knowledge base.",
      "If you run the reviewed standalone version as-is, it can operate on a built-in curated corpus of Allen resources.",
      "Open answers.jsonl and evaluation_report.json to inspect both the grounded responses and the retrieval score breakdown."
    ],
    inputs: ["corpus.jsonl", "eval_queries.jsonl", "or the capsule's built-in corpus"],
    outputs: ["answers.jsonl", "evaluation_report.json", "product bridge metadata"],
    runModes: ["Data asset", "Standalone built-in corpus", "Reproducible Run"],
    flags: ["data-asset", "retrieval"],
    notes:
      "Review status is Completed. The adversarial accuracy is intentionally low, which the review treats as evidence that the evaluation is honest.",
    readmePath: "./challenge_12_brain_map_bkp_assistant/code/README.md",
    reviewPath: "./review-challanges-iteration-03/challenge-12-review.md"
  },
  {
    id: "challenge-13",
    number: "13",
    title: "Croissant Pipeline for AI-Ready Data",
    directory: "challenge_13_croissant_pipeline",
    status: "completed",
    statusLabel: "Completed",
    problem:
      "Package scientific data as Croissant-compliant metadata so ML systems can discover, validate, and reload the dataset cleanly.",
    capsuleSummary:
      "The capsule exports metadata from H5AD, builds Croissant JSON-LD, validates it with mlcroissant, and demonstrates that real rows can be loaded back.",
    solution: [
      "The codebase solves the problem as a pipeline rather than a one-off script: generate or load a source dataset, export tables, build the descriptor, then validate and sample rows.",
      "That sequence is especially capsule-friendly because every stage produces a compact artifact that proves compliance, from CSV export to validation report."
    ],
    usageMode: "Attach H5AD or run the synthetic fallback",
    usageSteps: [
      "Attach source_dataset.h5ad if you want to package your own dataset with the same workflow.",
      "If you run the capsule without a dataset, the reviewed implementation can generate a synthetic H5AD so the pipeline stays self-demonstrating.",
      "Open croissant_metadata.json, cell_metadata.csv, and validation_report.json to verify that the descriptor is both valid and usable."
    ],
    inputs: ["source_dataset.h5ad or the built-in synthetic generation path"],
    outputs: ["croissant_metadata.json", "cell_metadata.csv", "validation_report.json"],
    runModes: ["Data asset", "Synthetic fallback", "Reproducible Run"],
    flags: ["data-asset", "self-contained", "synthetic-data"],
    notes:
      "Review status is Completed. The main limitation is that the demonstrated dataset is synthetic rather than a frozen real Allen dataset.",
    readmePath: "./challenge_13_croissant_pipeline/code/README.md",
    reviewPath: "./review-challanges-iteration-03/challenge-13-review.md"
  },
  {
    id: "challenge-14",
    number: "14",
    title: "Segment Intestine Villi",
    directory: "challenge_14_segment_intestine_villi",
    status: "completed",
    statusLabel: "Completed",
    problem:
      "Segment individual intestinal villi from spatial transcriptomics data using marker signals and spatial structure.",
    capsuleSummary:
      "The capsule identifies epithelial cells, builds a spatial neighbor graph, clusters the tissue into villus-scale regions, and exports plots, assignments, and boundaries.",
    solution: [
      "The codebase solves the problem by turning spatial transcriptomics into a geometry-plus-expression workflow: marker scoring, neighbor graph construction, Leiden clustering, and polygon export.",
      "In capsule form that means the run produces both analysis tables and spatial artifacts like GeoJSON boundaries, which makes it useful for both QC and downstream visualization."
    ],
    usageMode: "Attach Xenium data or use the synthetic fallback",
    usageSteps: [
      "Attach a xenium_ileum/ data asset if you want to analyze real spatial data.",
      "If no real asset is attached, the reviewed implementation can generate a synthetic villus-like dataset and still demonstrate the full segmentation pipeline.",
      "Inspect spatial_plot.png, villus_assignments.csv, per_villus_summary.csv, and villus_boundaries.geojson after the run."
    ],
    inputs: ["xenium_ileum/ or the built-in synthetic spatial fallback"],
    outputs: ["spatial_plot.png", "villus_assignments.csv", "per_villus_summary.csv", "villus_boundaries.geojson"],
    runModes: ["Data asset", "Synthetic fallback", "Reproducible Run"],
    flags: ["data-asset", "self-contained", "synthetic-data"],
    notes:
      "Review status is Completed. The key reviewed fix was wiring the spatial-neighbors graph into the clustering flow so the capsule could actually produce boundaries and summaries.",
    readmePath: "./challenge_14_segment_intestine_villi/code/README.md",
    reviewPath: "./review-challanges-iteration-03/challenge-14-review.md"
  },
  {
    id: "challenge-15",
    number: "15",
    title: "Allen Single Cell Model Pantry",
    directory: "challenge_15_allen_single_cell_model_pantry",
    status: "partial",
    statusLabel: "Partially completed",
    problem:
      "Benchmark single-cell foundation models on a shared Allen-style task with frozen splits and comparable evaluation outputs.",
    capsuleSummary:
      "The capsule builds a benchmarking harness around PCA and scVI-style adapters and writes a leaderboard plus confusion plots.",
    solution: [
      "The codebase solves the benchmarking problem as a reusable harness: standardized embeddings, a shared classifier contract, common metrics, and exported comparison artifacts.",
      "That structure is solid for a Code Ocean capsule because users can swap in real data or additional adapters later, even though the current reviewed results are not yet scientifically meaningful."
    ],
    usageMode: "Attach dataset and weights, or inspect the fallback framework",
    usageSteps: [
      "Attach mtg_dataset.h5ad, gene_mapping.csv, and geneformer_weights/ if you want to benchmark on your own packaged dataset.",
      "The reviewed implementation can generate synthetic data when real data is absent, which is useful for exercising the framework but not for trusting the resulting scores.",
      "Review leaderboard.csv, summary.json, and the confusion matrices to understand what the harness is producing."
    ],
    inputs: ["mtg_dataset.h5ad", "gene_mapping.csv", "geneformer_weights/", "or the synthetic fallback path"],
    outputs: ["leaderboard.csv", "summary.json", "confusion plots"],
    runModes: ["Data asset", "Synthetic fallback", "Reproducible Run"],
    flags: ["data-asset", "gpu", "synthetic-data"],
    notes:
      "Review status is Partially completed. The framework exists, but the synthetic benchmark is too easy and scVI stability remains uncertain.",
    readmePath: "./challenge_15_allen_single_cell_model_pantry/code/README.md",
    reviewPath: "./review-challanges-iteration-03/challenge-15-review.md"
  },
  {
    id: "challenge-16",
    number: "16",
    title: "SciDEX",
    directory: "challenge_16_scidex",
    status: "completed",
    statusLabel: "Completed",
    problem:
      "Create a persistent scientific hypothesis workbench that remembers prior reasoning and improves hypotheses across sessions.",
    capsuleSummary:
      "The capsule retrieves or loads a paper corpus, generates and critiques hypotheses, stores state in SQLite, and refines the ideas in a second session.",
    solution: [
      "The codebase solves the problem with an explicitly stateful workflow: session one generates evidence-backed hypotheses, and session two re-opens the state, applies review decisions, and revises the outputs.",
      "That is exactly the kind of behavior a capsule can demonstrate well because the persistence is visible in concrete artifacts such as the SQLite database, session files, and diff report."
    ],
    usageMode: "Run with defaults or attach your own research prompt and corpus",
    usageSteps: [
      "Attach question.json, corpus/papers.jsonl, and human_decisions.json if you want to steer the workbench with your own materials.",
      "If you run the reviewed standalone version as-is, it can fall back to an embedded research question and curated paper set.",
      "Open session_001_hypotheses.jsonl, session_002_hypotheses.jsonl, session_state.db, and the session diff artifacts to verify persistence across runs."
    ],
    inputs: ["question.json", "corpus/papers.jsonl", "human_decisions.json", "or embedded defaults"],
    outputs: ["session hypothesis files", "session_state.db", "evidence.jsonl", "session diff artifacts"],
    runModes: ["Data asset", "Standalone defaults", "Reproducible Run"],
    flags: ["data-asset", "bedrock", "self-contained"],
    notes:
      "Review status is Completed. The strongest part of the reviewed implementation is the visible cross-session memory and score evolution.",
    readmePath: "./challenge_16_scidex/code/README.md",
    reviewPath: "./review-challanges-iteration-03/challenge-16-review.md"
  }
];
