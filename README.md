# Allen Institute Nautilex 2026 Challenge Capsules

This repository documents an AI-driven implementation sprint for the **Allen Institute Nautilex 2026** hackathon challenges.

The goal was simple: take the challenge prompts, build a **Code Ocean capsule** for each one, run them as standalone research products, review the results honestly, and iterate fast.

Over **4 days** and **3 implementation / review iterations**, the work was driven through **Code Ocean Aqua** and **Claude Code**:

- **Aqua** was used as the Code Ocean agent layer for building and running the capsules.
- **Claude Code** was used as the coding agent to implement and revise the capsules.
- Claude Code was also used as a critic across iterations to review outputs, identify gaps, and drive the next round of fixes.

## Live Atlas

- **GitHub Pages atlas:** https://codeocean.github.io/challenges-capsules/
- **Repo atlas source:** [index.html](./index.html)
- **Repo capsule index:** [index.md](./index.md)
- **Iteration 03 summary:** [working-capsules-summary.md](./review-challanges-iteration-03/working-capsules-summary.md)

## Outcome

The current repo snapshot covers **15 capsules** for **Challenges 02-16**.

- **10 completed**
- **4 partially completed**
- **1 blocked**

The most important outcome is not just the code. It is the combination of:

- runnable capsule implementations
- capsule-specific READMEs
- review summaries with honest limitations
- a local and hosted HTML atlas for fast navigation

## What Is In This Repo

- `challenge_02_*` to `challenge_16_*`: the capsule codebases
- [`index.html`](./index.html): the main navigable atlas
- [`docs/`](./docs): styled HTML pages for every local README and review summary
- [`review-challanges-iteration-03/`](./review-challanges-iteration-03): iteration-03 review bundle
- [`build-embedded-docs.mjs`](./build-embedded-docs.mjs): rebuilds the embedded markdown bundle
- [`build-static-doc-pages.mjs`](./build-static-doc-pages.mjs): regenerates the static HTML doc pages

## Quick Navigation

| Challenge | Capsule | Status | Live README | Live Review |
|---|---|---:|---|---|
| 02 | Agentic Data Harmonization | Completed | [README](https://codeocean.github.io/challenges-capsules/docs/challenge-02-readme.html) | [Review](https://codeocean.github.io/challenges-capsules/docs/challenge-02-review.html) |
| 03 | Enhancer Designer | Completed | [README](https://codeocean.github.io/challenges-capsules/docs/challenge-03-readme.html) | [Review](https://codeocean.github.io/challenges-capsules/docs/challenge-03-review.html) |
| 04 | Light Sheet Alignment QC | Completed | [README](https://codeocean.github.io/challenges-capsules/docs/challenge-04-readme.html) | [Review](https://codeocean.github.io/challenges-capsules/docs/challenge-04-review.html) |
| 05 | Automate Your Productivity | Partial | [README](https://codeocean.github.io/challenges-capsules/docs/challenge-05-readme.html) | [Review](https://codeocean.github.io/challenges-capsules/docs/challenge-05-review.html) |
| 06 | Plasmid Forge | Partial | [README](https://codeocean.github.io/challenges-capsules/docs/challenge-06-readme.html) | [Review](https://codeocean.github.io/challenges-capsules/docs/challenge-06-review.html) |
| 07 | Engineering Automation | Completed | [README](https://codeocean.github.io/challenges-capsules/docs/challenge-07-readme.html) | [Review](https://codeocean.github.io/challenges-capsules/docs/challenge-07-review.html) |
| 08 | Query BFF | Completed | [README](https://codeocean.github.io/challenges-capsules/docs/challenge-08-readme.html) | [Review](https://codeocean.github.io/challenges-capsules/docs/challenge-08-review.html) |
| 09 | BindCrafting | Partial | [README](https://codeocean.github.io/challenges-capsules/docs/challenge-09-readme.html) | [Review](https://codeocean.github.io/challenges-capsules/docs/challenge-09-review.html) |
| 10 | NeuroBase Foundation Model Evaluation | Blocked | [README](https://codeocean.github.io/challenges-capsules/docs/challenge-10-readme.html) | [Review](https://codeocean.github.io/challenges-capsules/docs/challenge-10-review.html) |
| 11 | ABC Atlas Literature Assistant | Completed | [README](https://codeocean.github.io/challenges-capsules/docs/challenge-11-readme.html) | [Review](https://codeocean.github.io/challenges-capsules/docs/challenge-11-review.html) |
| 12 | Brain Map + BKP Assistant | Completed | [README](https://codeocean.github.io/challenges-capsules/docs/challenge-12-readme.html) | [Review](https://codeocean.github.io/challenges-capsules/docs/challenge-12-review.html) |
| 13 | Croissant Pipeline | Completed | [README](https://codeocean.github.io/challenges-capsules/docs/challenge-13-readme.html) | [Review](https://codeocean.github.io/challenges-capsules/docs/challenge-13-review.html) |
| 14 | Segment Intestine Villi | Completed | [README](https://codeocean.github.io/challenges-capsules/docs/challenge-14-readme.html) | [Review](https://codeocean.github.io/challenges-capsules/docs/challenge-14-review.html) |
| 15 | Allen Single Cell Model Pantry | Partial | [README](https://codeocean.github.io/challenges-capsules/docs/challenge-15-readme.html) | [Review](https://codeocean.github.io/challenges-capsules/docs/challenge-15-review.html) |
| 16 | SciDEX | Completed | [README](https://codeocean.github.io/challenges-capsules/docs/challenge-16-readme.html) | [Review](https://codeocean.github.io/challenges-capsules/docs/challenge-16-review.html) |

## Fastest Way To Explore

1. Open the live atlas: https://codeocean.github.io/challenges-capsules/
2. Use the sortable top table to scan by challenge, status, inputs, or usage mode.
3. Open any capsule's HTML README or review page for the styled document view.
4. Jump into the matching `challenge_*` folder when you want to iterate on the code.

## Quick Iteration Loop

When capsule code or review markdown changes, regenerate the local docs:

```bash
node build-embedded-docs.mjs
node build-static-doc-pages.mjs
```

Then reopen [`index.html`](./index.html) locally or refresh the GitHub Pages site after pushing.

## Notes

- The current cloned challenge set in this repo starts at **Challenge 02**.
- The review status labels are intentionally honest: some capsules are strong demonstrations, some are incomplete, and one remains blocked.
- The atlas and doc pages are static and can be opened directly in a browser over `file://`, with no local server required.
