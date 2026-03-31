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

const CAPSULE_DOC_AVAILABILITY = {
  readme: true,
  results: true,
  howToImplement: true,
  aquaPrompt: true,
  review: true
};

const CAPSULE_ENHANCEMENTS = {
  "challenge-02": {
    primaryUseCase: "Audit large Allen-style label harmonization runs against Cell Ontology with quantitative evaluation.",
    usageHighlights: [
      "Attach Allen labels, Cell Ontology, and gold mappings when you want the full real-data evaluation path.",
      "Run once to produce mapping outputs plus machine-readable quality reports.",
      "Use the reports to separate auto-mapped labels from the cases that still need curator review."
    ],
    resultsHighlights: [
      "Strong evidence on real Allen taxonomy data with F1 0.949 on the WHB mapping benchmark.",
      "Cross-dataset CELLxGENE evaluation also remains above 0.97 precision and recall.",
      "Bedrock support exists, but deterministic matching still carries most of the final signal."
    ],
    featuredArtifacts: [
      "challenge_02_agentic_data_harmonization/code/results/quality_report.json",
      "challenge_02_agentic_data_harmonization/code/results/difficulty_analysis.json",
      "challenge_02_agentic_data_harmonization/code/results/agentic_proof.json"
    ]
  },
  "challenge-03": {
    primaryUseCase: "Generate enhancer candidate panels with statistical evidence that evolved designs beat all controls.",
    usageHighlights: [
      "Use the App Panel when you want to steer generations, population size, mutation rate, and finalist count.",
      "Run self-contained for the default benchmark path or attach optional sequence assets for alternate seeds.",
      "Inspect the results bundle before opening the FASTA so you know whether the design loop actually improved scores."
    ],
    resultsHighlights: [
      "Strong statistical evidence: evolved sequences beat random, shuffled, and seed controls with p = 9.73e-13.",
      "The top-20 panel reaches a mean score of 1.000 while preserving diversity and manufacturability checks.",
      "This is one of the clearest self-contained result packages in the atlas."
    ],
    featuredArtifacts: ["challenge_03_enhancer_designer/code/results/stats.json"]
  },
  "challenge-04": {
    primaryUseCase: "Score light-sheet registration quality and triage confident passes from cases that need human review.",
    usageHighlights: [
      "Run directly when you want a self-contained QC benchmark with synthetic image pairs.",
      "Start with the metrics output, then inspect the severity breakdown if you need error-mode detail.",
      "Treat the current capsule as a validated QC harness rather than a real microscopy deployment."
    ],
    resultsHighlights: [
      "Strong evidence with AUC 0.977 and 93.75% test accuracy on the reviewed benchmark.",
      "The decision system is calibrated into pass, fail, and needs-review instead of only a raw classifier score.",
      "The main limitation is data realism, not pipeline completeness."
    ],
    featuredArtifacts: [
      "challenge_04_light_sheet_alignment_qc/code/results/metrics.json",
      "challenge_04_light_sheet_alignment_qc/code/results/severity_metrics.json"
    ]
  },
  "challenge-05": {
    primaryUseCase: "Analyze productivity anti-patterns and produce auditable automation proposals rather than direct calendar actions.",
    usageHighlights: [
      "Use Reproducible Run for the built-in scenarios or open the Cloud Workstation when you want the Streamlit workflow.",
      "Treat the output as a recommendation and audit system, not as a fully automated execution engine.",
      "Open the manifest first so you can see which scenarios, proposals, and traces were actually generated."
    ],
    resultsHighlights: [
      "Evidence is qualitative rather than benchmarked, because there is no objective ground-truth productivity target.",
      "The pipeline does run end to end across two realistic scenarios and preserves audit-trail information.",
      "Review findings still mark this capsule partial because several promised downstream workflow artifacts are missing."
    ],
    featuredArtifacts: ["challenge_05_automate_your_productivity/code/results/manifest.json"]
  },
  "challenge-06": {
    primaryUseCase: "Prototype plasmid request interpretation with deterministic safety refusal and file-based design outputs.",
    usageHighlights: [
      "Attach natural-language requests plus part libraries when you want to exercise the design path.",
      "Use the safety workflow even without Bedrock because refusal logic remains deterministic.",
      "Read the implementation and prompt docs before expecting broad biological request coverage."
    ],
    resultsHighlights: [
      "Partial evidence only: 1 of 6 evaluation cases passes, and that passing case is the safety refusal workflow.",
      "Most construct-generation cases still depend on live Bedrock parsing and part selection.",
      "This capsule currently proves the safety gate more clearly than the design engine."
    ],
    featuredArtifacts: ["challenge_06_plasmid_forge/code/results/evaluation_summary.json"]
  },
  "challenge-07": {
    primaryUseCase: "Run an agentic maintenance benchmark that attempts code fixes, tests them, and tracks cost and outcomes.",
    usageHighlights: [
      "Attach task bundles when you want to benchmark your own repository repair tasks.",
      "Inspect the dashboard before diving into patches so you can separate true fixes from already-passing tasks.",
      "Use the AQUA prompt and implementation notes if you want to adapt the agent loop to another repair benchmark."
    ],
    resultsHighlights: [
      "Moderate evidence: 5 of 15 total tasks resolve, with 5 of 7 genuine fix attempts succeeding.",
      "The pipeline records iterations, status, and Bedrock cost so the benchmark is auditable rather than anecdotal.",
      "The current benchmark mix still includes too many already-passing tasks."
    ],
    featuredArtifacts: ["challenge_07_engineering_automation/code/results/dashboard.json"]
  },
  "challenge-08": {
    primaryUseCase: "Turn natural-language metadata questions into validated BFF filters over real Allen Cell Collection manifests.",
    usageHighlights: [
      "Use Aqua or the App Panel when you want one grounded metadata query with structured filters and provenance.",
      "Leave the query blank and run the capsule to switch into evaluation mode.",
      "Use the raw AQUA prompt file from the atlas when you want copy-ready instructions for Aqua."
    ],
    resultsHighlights: [
      "Moderate real-data evidence: 75% accuracy on the current four-query evaluation set.",
      "Latency and manifest dimensions are reported, which makes the query translation behavior inspectable.",
      "This is still one of the most directly usable capsules in the atlas because the underlying data is real and the interaction model is simple."
    ],
    featuredArtifacts: ["challenge_08_query_bff/code/results/evaluation_report.json"]
  },
  "challenge-09": {
    primaryUseCase: "Analyze and rank binder candidates against a real target structure when full generative design is not available.",
    usageHighlights: [
      "Run the default analysis demo when you want the ranking, filtering, and fusion-compatibility workflow.",
      "Open the ranked candidate table alongside the compatibility output to understand why each binder rose or fell.",
      "Treat the current pipeline as post-design analysis, not as a real BindCraft generation run."
    ],
    resultsHighlights: [
      "Partial evidence: the target structure is real, but all candidate binder metrics are simulated.",
      "The results package is still useful for downstream decision-making because it preserves structural ranking and fusion checks.",
      "GPU-bound design generation remains the missing step."
    ],
    featuredArtifacts: [
      "challenge_09_bindcrafting/code/results/ranked_candidates.csv",
      "challenge_09_bindcrafting/code/results/fusion_compatibility.json"
    ]
  },
  "challenge-10": {
    primaryUseCase: "Benchmark 3D neuroanatomical encoders on Allen CCFv3 data and compare them with reusable result artifacts.",
    usageHighlights: [
      "Run directly for the default Allen CCFv3 benchmark path; the capsule downloads and caches public Allen assets itself.",
      "Start with summary.json and dice_scores.csv, then open the richer markdown and figure outputs for interpretation.",
      "Attach real NeuroBase weights later if you want to swap the proxy encoder for the intended model."
    ],
    resultsHighlights: [
      "Partial but meaningful evidence: classical features reach mean Dice 0.367 and outperform random by 2.59x.",
      "The self-supervised 3D proxy also improves over random, which validates the benchmark harness.",
      "The scientific gap is still the missing NeuroBase checkpoint, not the evaluation plumbing."
    ],
    featuredArtifacts: [
      "challenge_10_neurobase_foundation_model_evaluation/code/results/summary.json",
      "challenge_10_neurobase_foundation_model_evaluation/code/results/dice_scores.csv"
    ]
  },
  "challenge-11": {
    primaryUseCase: "Answer ABC Atlas literature questions with a retrieval pipeline that verifies every cited paper exists in the corpus.",
    usageHighlights: [
      "Run with the built-in bootstrap path when you want the default literature pack, or attach your own corpus for custom evaluation.",
      "Open the results report first to confirm citation validity before reading any narrative answer output.",
      "Use the implementation and prompt docs if you want to adapt the retrieval-plus-validation pattern to another literature corpus."
    ],
    resultsHighlights: [
      "Moderate evidence across 15 queries with 41 of 41 citations verified against the corpus.",
      "The current evaluation proves citation grounding more clearly than answer correctness.",
      "This is a strong retrieval-and-verification capsule, but not yet a full answer-quality benchmark."
    ],
    featuredArtifacts: ["challenge_11_abc_atlas_literature_assistant/code/results/eval_report.json"]
  },
  "challenge-12": {
    primaryUseCase: "Build a grounded assistant over Allen product resources with honest evaluation across easy, hard, and adversarial cases.",
    usageHighlights: [
      "Run with the built-in corpus when you want the reviewed benchmark path, or attach a custom corpus to reuse the same workflow.",
      "Start with the evaluation report because the category breakdown is the clearest signal of where the assistant is reliable.",
      "Use the AQUA prompt and implementation docs if you want to reuse the retrieval-and-citation pattern for another product knowledge base."
    ],
    resultsHighlights: [
      "Strong evidence with 86.7% overall accuracy on a 15-query evaluation set.",
      "Adversarial accuracy drops to 33.3%, which makes the benchmark more credible rather than less useful.",
      "Cross-product connections are also preserved as a separate structured artifact."
    ],
    featuredArtifacts: [
      "challenge_12_brain_map_bkp_assistant/code/results/evaluation_report.json",
      "challenge_12_brain_map_bkp_assistant/code/results/product_bridges.json"
    ]
  },
  "challenge-13": {
    primaryUseCase: "Package a scientific dataset as Croissant metadata and verify where the descriptor is valid or still broken.",
    usageHighlights: [
      "Attach your H5AD when you want to run the packaging flow on real data, or use the built-in synthetic generation path to test the pipeline.",
      "Open the validation report first because it tells you whether the Croissant descriptor is actually consumable.",
      "Use the implementation notes to fix schema issues before relying on the metadata downstream."
    ],
    resultsHighlights: [
      "Partial evidence: dataset generation and export work, but Croissant validation still fails on a schema bug.",
      "The capsule does prove the surrounding pipeline, including train/test split logic and CSV export.",
      "This is best treated as a near-complete packaging workflow with one blocking metadata fix."
    ],
    featuredArtifacts: ["challenge_13_croissant_pipeline/code/results/validation_report.json"]
  },
  "challenge-14": {
    primaryUseCase: "Segment villus-scale regions from spatial transcriptomics and export geometry plus per-villus summaries.",
    usageHighlights: [
      "Attach real Xenium ileum data when you have it, or run the synthetic fallback to validate the geometry-and-expression workflow.",
      "Open the per-villus summary together with the provenance file so you know whether the run used simulated or real data.",
      "Use the HOW TO IMPLEMENT notes if you want to adapt the spatial-neighbor graph logic to another tissue layout."
    ],
    resultsHighlights: [
      "Partial evidence on simulated data: the pipeline identifies 7 villi and exports GeoJSON-ready boundaries.",
      "The end-to-end segmentation plumbing works, but the current evidence is limited by the absence of real Xenium data.",
      "This is a strong proof-of-concept for the spatial workflow, not yet a validated biological result."
    ],
    featuredArtifacts: [
      "challenge_14_segment_intestine_villi/code/results/per_villus_summary.csv",
      "challenge_14_segment_intestine_villi/code/results/data_provenance.json"
    ]
  },
  "challenge-15": {
    primaryUseCase: "Benchmark Allen-style single-cell model adapters under one evaluation contract and surface where the environment still blocks them.",
    usageHighlights: [
      "Attach the frozen dataset and model weights if you want to exercise the intended benchmark path.",
      "Start with the leaderboard and summary because they make the current environment failures immediately visible.",
      "Use the implementation notes before spending time on the outputs, since environment repair is still the main blocker."
    ],
    resultsHighlights: [
      "Partial evidence only: the PCA baseline completes, but scVI and Geneformer are blocked by environment and configuration errors.",
      "Current macro F1 is weak because the benchmark effectively collapses to a PCA-only path.",
      "The useful part here is the benchmarking harness and exported comparison contract, not the current scientific result."
    ],
    featuredArtifacts: [
      "challenge_15_allen_single_cell_model_pantry/code/results/leaderboard.csv",
      "challenge_15_allen_single_cell_model_pantry/code/results/summary.json"
    ]
  },
  "challenge-16": {
    primaryUseCase: "Run a persistent scientific hypothesis workbench that carries evidence and decisions across sessions.",
    usageHighlights: [
      "Run with embedded defaults for the reviewed demo, or attach your own question and corpus when you want to steer the workbench.",
      "Open the evidence file and stateful session outputs together so you can confirm traceability across sessions.",
      "Use the AQUA prompt if you want to hand Aqua a copy-ready workflow prompt for hypothesis generation."
    ],
    resultsHighlights: [
      "Qualitative evidence rather than benchmark accuracy, but the citation chain and state persistence are verifiable.",
      "The capsule demonstrates a complete two-session refinement workflow backed by SQLite state.",
      "This is one of the strongest atlas entries for visible cross-session memory."
    ],
    featuredArtifacts: [
      "challenge_16_scidex/code/results/evidence.jsonl",
      "challenge_16_scidex/code/results/question.json"
    ]
  }
};

window.CAPSULES = window.CAPSULES.map((capsule) => {
  const enhancement = CAPSULE_ENHANCEMENTS[capsule.id] || {};

  return {
    ...capsule,
    primaryUseCase: enhancement.primaryUseCase || capsule.capsuleSummary,
    usageHighlights: enhancement.usageHighlights || [],
    resultsHighlights: enhancement.resultsHighlights || [],
    featuredArtifacts: enhancement.featuredArtifacts || [],
    docAvailability: {
      ...CAPSULE_DOC_AVAILABILITY,
      ...(enhancement.docAvailability || {})
    },
    resultsPath: `./${capsule.directory}/code/RESULTS.md`,
    howToImplementPath: `./${capsule.directory}/code/HOW_TO_IMPLEMENT.md`,
    aquaPromptPath: `./${capsule.directory}/code/AQUA_PROMPT.md`
  };
});
