#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST_PATH="$ROOT_DIR/subtrees.conf"

cd "$ROOT_DIR"
export PATH="$(git --exec-path):$PATH"

declare -a TARGETS=("$@")
declare -a SUMMARY=()
declare -a MATCHED_TARGETS=()

if [[ ! -f "$MANIFEST_PATH" ]]; then
  echo "Missing manifest: $MANIFEST_PATH" >&2
  exit 1
fi

require_clean_tree() {
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "Working tree is not clean. Commit or stash changes before running subtree pull." >&2
    git status --short >&2
    exit 1
  fi
}

ensure_remote() {
  local remote_name="$1"
  local remote_url="$2"
  local current_url

  current_url="$(git remote get-url "$remote_name" 2>/dev/null || true)"
  if [[ -z "$current_url" ]]; then
    git remote add "$remote_name" "$remote_url"
    return
  fi

  if [[ "$current_url" != "$remote_url" ]]; then
    git remote set-url "$remote_name" "$remote_url"
  fi
}

should_process() {
  local name="$1"
  local path="$2"

  if [[ ${#TARGETS[@]} -eq 0 ]]; then
    return 0
  fi

  local target
  for target in "${TARGETS[@]}"; do
    if [[ "$target" == "$name" || "$target" == "$path" ]]; then
      MATCHED_TARGETS+=("$target")
      return 0
    fi
  done

  return 1
}

print_summary() {
  echo
  echo "Subtree pull summary"
  echo "===================="
  local entry path status
  for entry in "${SUMMARY[@]}"; do
    path="${entry%%|*}"
    status="${entry##*|}"
    printf '  %-45s %s\n' "$path" "$status"
  done
}

require_clean_tree

while IFS=$'\t' read -r name path remote_name remote_url branch; do
  [[ -n "$name" ]] || continue

  if ! should_process "$name" "$path"; then
    continue
  fi

  echo
  echo "Processing subtree pull for $path"
  echo "----------------------------------------------"

  ensure_remote "$remote_name" "$remote_url"
  git fetch "$remote_name" "$branch" --prune

  local_split="$(git subtree split --prefix="$path" HEAD)"
  remote_ref="refs/remotes/$remote_name/$branch"
  remote_head="$(git rev-parse --verify "$remote_ref")"

  if [[ "$local_split" == "$remote_head" ]]; then
    echo "  Status: skipped (already aligned with $remote_name/$branch)"
    SUMMARY+=("$path|skipped")
    continue
  fi

  echo "  Status: pulling updates from $remote_name/$branch"
  git subtree pull --prefix="$path" "$remote_name" "$branch" \
    -m "Merge subtree updates for $path from $remote_name/$branch"
  SUMMARY+=("$path|updated")
done < "$MANIFEST_PATH"

if [[ ${#TARGETS[@]} -gt 0 ]]; then
  for target in "${TARGETS[@]}"; do
    found=0
    for matched in "${MATCHED_TARGETS[@]}"; do
      if [[ "$matched" == "$target" ]]; then
        found=1
        break
      fi
    done

    if [[ "$found" -eq 0 ]]; then
      echo "Unknown subtree target: $target" >&2
      exit 1
    fi
  done
fi

print_summary
