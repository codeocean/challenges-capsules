#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

fail() {
  echo "TEST FAILED: $*" >&2
  exit 1
}

assert_contains() {
  local haystack="$1"
  local needle="$2"
  if [[ "$haystack" != *"$needle"* ]]; then
    fail "Expected output to contain: $needle"
  fi
}

echo "Running subtree migration validation..."

if git ls-files --stage | rg -q '^160000 .*challenge_'; then
  fail "Found gitlink entries for challenge_* paths"
fi

if [[ -e .gitmodules ]]; then
  fail ".gitmodules still exists"
fi

if find challenge_* -name .git -print -quit | grep -q .; then
  fail "Found nested .git metadata under challenge_*"
fi

if [[ ! -f subtrees.conf ]]; then
  fail "subtrees.conf is missing"
fi

pull_output="$(./pull_all_challenges.sh challenge_02_agentic_data_harmonization 2>&1)"
echo "$pull_output"
if [[ "$pull_output" != *"skipped"* && "$pull_output" != *"updated"* ]]; then
  fail "pull_all_challenges.sh did not report skipped or updated"
fi

push_output="$(./push_all_challenges.sh challenge_02_agentic_data_harmonization 2>&1)"
echo "$push_output"
assert_contains "$push_output" "unchanged"

dirty_probe=".subtree-dirty-check"
touch "$dirty_probe"

if ./pull_all_challenges.sh challenge_02_agentic_data_harmonization >/tmp/subtree-pull-dirty.log 2>&1; then
  rm -f "$dirty_probe"
  fail "pull_all_challenges.sh succeeded on a dirty working tree"
fi

if ./push_all_challenges.sh challenge_02_agentic_data_harmonization >/tmp/subtree-push-dirty.log 2>&1; then
  rm -f "$dirty_probe"
  fail "push_all_challenges.sh succeeded on a dirty working tree"
fi

rm -f "$dirty_probe" /tmp/subtree-pull-dirty.log /tmp/subtree-push-dirty.log

echo "All subtree migration checks passed."
