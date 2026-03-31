#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

shopt -s nullglob

declare -a CHALLENGE_DIRS=()
declare -a SUMMARY=()

for dir in challenge_*; do
    [[ -d "$dir" ]] || continue
    CHALLENGE_DIRS+=("$dir")
done

if [[ ${#CHALLENGE_DIRS[@]} -eq 0 ]]; then
    echo "No challenge directories found under $ROOT_DIR" >&2
    exit 1
fi

echo "Starting safe git sync for challenges 02-16..."
echo "=============================================="

echo
echo "Preflight: verifying all challenge repos are clean..."
for dir in "${CHALLENGE_DIRS[@]}"; do
    if [[ ! -d "$dir/.git" ]]; then
        echo "Preflight failed: $dir is not a git repository." >&2
        exit 1
    fi

    if [[ -n "$(git -C "$dir" status --porcelain)" ]]; then
        echo "Preflight failed: $dir has uncommitted changes." >&2
        git -C "$dir" status --short
        exit 1
    fi
done

echo "Preflight passed."

for dir in "${CHALLENGE_DIRS[@]}"; do
    echo
    echo "Processing: $dir"
    echo "----------------------------------------------"

    git -C "$dir" fetch origin master --prune

    counts="$(git -C "$dir" rev-list --left-right --count HEAD...origin/master)"
    ahead="${counts%%[[:space:]]*}"
    behind="${counts##*[[:space:]]}"

    if [[ "$ahead" -eq 0 && "$behind" -eq 0 ]]; then
        echo "  Status: up to date"
        SUMMARY+=("$dir|up-to-date")
        continue
    fi

    if [[ "$ahead" -eq 0 && "$behind" -gt 0 ]]; then
        echo "  Status: behind by $behind commit(s); fast-forwarding"
        git -C "$dir" pull --ff-only origin master
        SUMMARY+=("$dir|fast-forwarded")
        continue
    fi

    if [[ "$ahead" -gt 0 && "$behind" -eq 0 ]]; then
        echo "  Status: ahead by $ahead commit(s); leaving local-only history untouched"
        SUMMARY+=("$dir|local-only")
        continue
    fi

    echo "  Status: diverged (ahead $ahead, behind $behind); rebasing onto origin/master"
    if git -C "$dir" pull --rebase origin master; then
        SUMMARY+=("$dir|rebased")
        continue
    fi

    echo "  Rebase failed in $dir" >&2
    echo "  Conflicted files:" >&2
    git -C "$dir" diff --name-only --diff-filter=U >&2 || true
    git -C "$dir" status --short >&2 || true
    exit 1
done

echo
echo "=============================================="
echo "Sync summary"
echo "=============================================="

for entry in "${SUMMARY[@]}"; do
    dir="${entry%%|*}"
    status="${entry##*|}"
    printf '  %-45s %s\n' "$dir" "$status"
done

echo
echo "Completed safe git sync for all challenges."
