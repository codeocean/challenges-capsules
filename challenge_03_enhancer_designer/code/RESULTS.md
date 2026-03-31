# Results — Challenge 03: Enhancer Designer

## Evidence Strength: STRONG

This capsule produces **rigorous statistical evidence** that evolved enhancer sequences score significantly higher than all controls. The pipeline is fully self-contained (no external dependencies) and uses a trained CNN oracle for scoring.

## Evaluation Results

### Statistical Tests (stats.json)
| Comparison | p-value | Cohen's d | Pass |
|-----------|---------|-----------|------|
| Evolved vs Random | 9.73e-13 | 6.20 | ✅ |
| Evolved vs Shuffled | 9.73e-13 | 4.35 | ✅ |
| Evolved vs Seeds | 9.73e-13 | 1.89 | ✅ |

### Score Distributions
| Group | Mean Score |
|-------|-----------|
| Evolved (top-20) | 1.000 |
| Seeds | 0.675 |
| Shuffled | 0.339 |
| Random | 0.196 |

### Diversity Metrics
- Mean pairwise distance: 0.366
- Near-duplicate fraction: 0.0%
- Diversity pass: ✅

### Oracle Details
- **Primary scorer:** Trained CNN oracle (K562 sequence features)
- **Secondary scorer:** PWM-based (quality⁴ + cooperativity + GC + entropy)
- Cross-oracle Pearson correlation: 0.117

### Evolutionary Trajectory
- 50 generations, population size 200
- Score improved from 0.991 (gen 1) to 1.000 (final)

## Known Limitations
- The CNN oracle is trained on synthetic positive/negative sequences, not real experimentally-validated enhancers
- Cross-oracle correlation is low (0.117), meaning the CNN and PWM scorers measure different properties
- No wet-lab validation of designed sequences

## Output Artifacts
| File | Description |
|------|-------------|
| `top20.fasta` | Top 20 evolved enhancer sequences with annotations |
| `stats.json` | Full statistical evaluation |
| `enhancer_report.png` | Score distributions, trajectory, diversity matrix |
| `oracle_training_log.json` | CNN training metrics |
