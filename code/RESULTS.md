# Results — Challenge 03: Enhancer Designer

## Latest Successful Run
- **Computation ID:** `565b9f6d-147c-4224-8a1d-ef0c4fea3ce6`
- **Status:** Succeeded (exit code 0)
- **Runtime:** 260 seconds

## Evaluation Results

### Statistical Tests (stats.json)
| Comparison | p-value | Effect Size (d) | Pass |
|-----------|---------|-----------------|------|
| Evolved vs Random | 9.73e-13 | 6.20 | ✅ |
| Evolved vs Shuffled | 9.73e-13 | 4.35 | ✅ |
| Evolved vs Seeds | 9.73e-13 | 1.89 | ✅ |

### Scores
| Group | Mean Score | Std |
|-------|-----------|-----|
| Evolved (top-20) | 1.000 | 0.000 |
| Seeds | 0.675 | — |
| Random | 0.196 | — |
| Shuffled | 0.339 | — |

### Diversity
- Mean pairwise distance: 0.366
- Near-duplicate fraction: 0.0%
- Diversity pass: ✅

### Oracle
- **Primary:** Trained CNN oracle (K562 sequence features)
- **Secondary:** PWM-based scorer
- Cross-oracle Pearson correlation: 0.117

### Trajectory
- Generations: 50, Score gen1: 0.991, Score final: 1.000

## Output Artifacts
| File | Description |
|------|-------------|
| `top20.fasta` | Top 20 evolved enhancer sequences |
| `stats.json` | Statistical evaluation and comparisons |
| `enhancer_report.png` | Score distribution boxplot |
| `oracle_training_log.json` | CNN training metrics |
| `manifest.json` | Run configuration |
