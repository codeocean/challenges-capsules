---
name: rtk
description: >
  RTK (Rust Token Killer) - high-performance CLI proxy that reduces LLM token consumption by 60-90%.
  Use this skill when running ANY shell/Bash commands in Claude Code sessions. RTK automatically
  rewrites commands via a hook, but this skill ensures correct usage patterns, troubleshooting,
  and awareness of which commands benefit from RTK. Triggers: shell commands, git operations,
  test runners, build tools, docker/k8s, file operations, token savings analysis, rtk configuration.
---

# RTK - Rust Token Killer

CLI proxy that filters and compresses command outputs before they reach LLM context.
Single Rust binary, zero dependencies, <10ms overhead. Saves 60-90% tokens.

## How It Works

The auto-rewrite hook intercepts Bash tool calls and rewrites them to `rtk` equivalents transparently.
Claude never sees the rewrite — it just gets compressed output.

**Important limitation:** The hook only runs on Bash tool calls. Claude Code built-in tools (`Read`, `Grep`, `Glob`) bypass the hook. To get RTK filtering for those workflows, use shell commands (`cat`, `rg`, `find`) or call `rtk read`, `rtk grep`, `rtk find` directly.

## Command Reference

### Files
```bash
rtk ls .                        # Token-optimized directory tree
rtk read file.rs                # Smart file reading
rtk read file.rs -l aggressive  # Signatures only (strips bodies)
rtk smart file.rs               # 2-line heuristic code summary
rtk find "*.rs" .               # Compact find results
rtk grep "pattern" .            # Grouped search results
rtk diff file1 file2            # Condensed diff
```

### Git
```bash
rtk git status                  # Compact status
rtk git log -n 10               # One-line commits
rtk git diff                    # Condensed diff
rtk git add                     # -> "ok"
rtk git commit -m "msg"         # -> "ok abc1234"
rtk git push                    # -> "ok main"
rtk git pull                    # -> "ok 3 files +10 -2"
```

### GitHub CLI
```bash
rtk gh pr list                  # Compact PR listing
rtk gh pr view 42               # PR details + checks
rtk gh issue list               # Compact issue listing
rtk gh run list                 # Workflow run status
```

### Test Runners
```bash
rtk test cargo test             # Show failures only (-90%)
rtk err npm run build           # Errors/warnings only
rtk vitest run                  # Vitest compact (failures only)
rtk playwright test             # E2E results (failures only)
rtk pytest                      # Python tests (-90%)
rtk go test                     # Go tests (-90%)
rtk cargo test                  # Cargo tests (-90%)
```

### Build & Lint
```bash
rtk lint                        # ESLint grouped by rule/file
rtk lint biome                  # Other linters
rtk tsc                         # TypeScript errors grouped by file
rtk next build                  # Next.js build compact
rtk prettier --check .          # Files needing formatting
rtk cargo build                 # Cargo build (-80%)
rtk cargo clippy                # Cargo clippy (-80%)
rtk ruff check                  # Python linting (-80%)
rtk golangci-lint run           # Go linting (-85%)
```

### Package Managers
```bash
rtk pnpm list                   # Compact dependency tree
rtk pip list                    # Python packages (auto-detect uv)
rtk pip outdated                # Outdated packages
rtk prisma generate             # Schema generation (no ASCII art)
```

### Containers
```bash
rtk docker ps                   # Compact container list
rtk docker images               # Compact image list
rtk docker logs <container>     # Deduplicated logs
rtk docker compose ps           # Compose services
rtk kubectl pods                # Compact pod list
rtk kubectl logs <pod>          # Deduplicated logs
rtk kubectl services            # Compact service list
```

### Data & Analytics
```bash
rtk json config.json            # Structure without values
rtk deps                        # Dependencies summary
rtk env -f AWS                  # Filtered env vars
rtk log app.log                 # Deduplicated logs
rtk curl <url>                  # Auto-detect JSON + schema
rtk wget <url>                  # Download, strip progress bars
rtk summary <long command>      # Heuristic summary
rtk proxy <command>             # Raw passthrough + tracking
```

## Meta Commands (use rtk directly, not via hook)
```bash
rtk gain                        # Summary stats
rtk gain --graph                # ASCII graph (last 30 days)
rtk gain --history              # Recent command history
rtk gain --daily                # Day-by-day breakdown
rtk gain --all --format json    # JSON export
rtk discover                    # Find missed savings opportunities
rtk discover --all --since 7    # All projects, last 7 days
rtk session                     # RTK adoption across recent sessions
```

## Auto-Rewrite Table

| Raw Command | Rewritten To |
|-------------|-------------|
| `git status/diff/log/add/commit/push/pull` | `rtk git ...` |
| `gh pr/issue/run` | `rtk gh ...` |
| `cargo test/build/clippy` | `rtk cargo ...` |
| `cat/head/tail <file>` | `rtk read <file>` |
| `rg/grep <pattern>` | `rtk grep <pattern>` |
| `ls` | `rtk ls` |
| `vitest/jest` | `rtk vitest run` |
| `tsc` | `rtk tsc` |
| `eslint/biome` | `rtk lint` |
| `prettier` | `rtk prettier` |
| `playwright` | `rtk playwright` |
| `prisma` | `rtk prisma` |
| `ruff check/format` | `rtk ruff ...` |
| `pytest` | `rtk pytest` |
| `pip list/install` | `rtk pip ...` |
| `go test/build/vet` | `rtk go ...` |
| `golangci-lint` | `rtk golangci-lint` |
| `docker ps/images/logs` | `rtk docker ...` |
| `kubectl get/logs` | `rtk kubectl ...` |
| `curl` | `rtk curl` |
| `pnpm list/outdated` | `rtk pnpm ...` |

Commands already using `rtk`, heredocs (`<<`), and unrecognized commands pass through unchanged.

## Global Flags
```bash
-u, --ultra-compact    # ASCII icons, inline format (extra savings)
-v, --verbose          # Increase verbosity (-v, -vv, -vvv)
```

## Four Compression Strategies

1. **Smart Filtering** — removes noise (comments, whitespace, boilerplate)
2. **Grouping** — aggregates similar items (files by directory, errors by type)
3. **Truncation** — keeps relevant context, cuts redundancy
4. **Deduplication** — collapses repeated log lines with counts

## Tee: Full Output Recovery

When a command fails, RTK saves the full unfiltered output:
```
FAILED: 2/15 tests
[full output: ~/.local/share/rtk/tee/1707753600_cargo_test.log]
```

Read the tee file when compressed output is insufficient for debugging.

## Configuration

Config file: `~/.config/rtk/config.toml` (macOS: `~/Library/Application Support/rtk/config.toml`)

```toml
[tracking]
database_path = "/path/to/custom.db"  # default: ~/.local/share/rtk/history.db

[hooks]
exclude_commands = ["curl", "playwright"]  # skip rewrite for these

[tee]
enabled = true          # save raw output on failure (default: true)
mode = "failures"       # "failures", "always", or "never"
max_files = 20          # rotation limit
```

## Setup & Troubleshooting

Install: `brew install rtk` or `curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh`

Initialize hook: `rtk init -g` (then restart Claude Code)

Verify: `rtk --version` and `rtk gain`

Uninstall: `rtk init -g --uninstall`

**Name collision**: If `rtk gain` fails, you may have the wrong `rtk` package (Rust Type Kit). Use `cargo install --git https://github.com/rtk-ai/rtk` instead.
