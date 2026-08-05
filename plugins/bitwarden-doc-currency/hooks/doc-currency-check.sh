#!/bin/bash
# doc-currency-check.sh
# Stop hook: deterministic tripwire for stale in-repo documentation.
#
# Trigger rule: fire when a changed file has a documented ancestor scope
# below the repo root and no documentation along its ancestor chain was
# touched. A directory is a documented scope when it contains a README.md
# or a docs/ directory. Root-scope docs do not arm the tripwire, since the
# root is an ancestor of every file; their verification belongs to the
# semantic layer.
#
# Behavior: blocks exactly once per session with a message directing the
# agent to the verifying-doc-currency skill, then allows through.
# Generalizes bitwarden/server's .claude/hooks/seeder-docs-check.sh.
#
# Fail-open: any environment problem (no jq, no git repo) lets the turn end without blocking.

set -uo pipefail

command -v jq >/dev/null 2>&1 || exit 0

INPUT=$(cat)

# Guard: if a Stop hook already blocked this turn, allow through.
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
if [[ "$STOP_HOOK_ACTIVE" == "true" ]]; then
  exit 0
fi

# Guard: block at most once per session.
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty' | tr -cd 'a-zA-Z0-9_-')
MARKER=""
if [[ -n "$SESSION_ID" ]]; then
  MARKER="${TMPDIR:-/tmp}/doc-currency-blocked-${SESSION_ID}"
  if [[ -f "$MARKER" ]]; then
    exit 0
  fi
fi

CWD=$(echo "$INPUT" | jq -r '.cwd // empty')
if [[ -z "$CWD" ]]; then
  exit 0
fi

REPO_ROOT=$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null) || exit 0

# Gather all changed files (staged, unstaged, and untracked) relative to repo root.
DIFF_HEAD=$(git -C "$REPO_ROOT" diff --name-only HEAD 2>/dev/null || true)
UNTRACKED=$(git -C "$REPO_ROOT" ls-files --others --exclude-standard 2>/dev/null || true)
ALL_CHANGED=$(printf "%s\n%s" "$DIFF_HEAD" "$UNTRACKED" | sort -u | grep -v '^$' || true)

if [[ -z "$ALL_CHANGED" ]]; then
  exit 0
fi

# A file is documentation when it is a markdown or diagram source file, or
# when it lives under a docs/ directory.
is_doc_file() {
  case "$1" in
    *.md | *.mdx | *.mmd | *.mermaid) return 0 ;;
    docs/* | */docs/*) return 0 ;;
  esac
  return 1
}

# The scope a documentation file describes: the directory holding it, or the
# parent of its docs/ directory when it lives under one.
doc_scope() {
  local path="$1"
  case "$path" in
    docs/*) echo "." ;;
    */docs/*) echo "${path%%/docs/*}" ;;
    *) dirname "$path" ;;
  esac
}

# Partition the change set and collect the scope of every touched doc.
CHANGED_CODE=""
TOUCHED_DOC_SCOPES=""
while IFS= read -r file; do
  if is_doc_file "$file"; then
    TOUCHED_DOC_SCOPES="${TOUCHED_DOC_SCOPES}$(doc_scope "$file")"$'\n'
  else
    CHANGED_CODE="${CHANGED_CODE}${file}"$'\n'
  fi
done <<<"$ALL_CHANGED"

if [[ -z "$CHANGED_CODE" ]]; then
  exit 0
fi
TOUCHED_DOC_SCOPES=$(printf '%s' "$TOUCHED_DOC_SCOPES" | sort -u)

# A touched doc covers a file when the doc's scope is an ancestor of the file.
is_covered() {
  local file="$1" scope
  while IFS= read -r scope; do
    [[ -z "$scope" ]] && continue
    if [[ "$scope" == "." || "$file" == "$scope/"* ]]; then
      return 0
    fi
  done <<<"$TOUCHED_DOC_SCOPES"
  return 1
}

# Documented ancestor scopes of a file, strictly below the repo root.
documented_ancestors() {
  local dir
  dir=$(dirname "$1")
  while [[ "$dir" != "." && "$dir" != "/" ]]; do
    if [[ -f "$REPO_ROOT/$dir/README.md" || -d "$REPO_ROOT/$dir/docs" ]]; then
      echo "$dir"
    fi
    dir=$(dirname "$dir")
  done
}

VIOLATIONS=""
VIOLATION_SCOPES=""
while IFS= read -r file; do
  [[ -z "$file" ]] && continue
  ancestors=$(documented_ancestors "$file")
  [[ -z "$ancestors" ]] && continue
  if ! is_covered "$file"; then
    VIOLATIONS="${VIOLATIONS}  - ${file}"$'\n'
    VIOLATION_SCOPES="${VIOLATION_SCOPES}${ancestors}"$'\n'
  fi
done <<<"$CHANGED_CODE"

if [[ -z "$VIOLATIONS" ]]; then
  exit 0
fi

VIOLATION_SCOPES=$(printf '%s' "$VIOLATION_SCOPES" | sort -u | sed 's/^/  - /')

if [[ -n "$MARKER" ]]; then
  touch "$MARKER" 2>/dev/null || true
fi

REASON=$(printf 'Code changed inside documented scopes, but no documentation along the changed files'\'' ancestor chains was touched.\n\nChanged files without a documentation update:\n%s\nDocumented scopes involved:\n%s\n\nRun the bitwarden-doc-currency:verifying-doc-currency skill now: read the diff, then verify or update the documentation at every documented ancestor scope of the change. If nothing documented at a scope drifted, say so explicitly per scope. Do not make a token documentation edit to satisfy this check.' "$VIOLATIONS" "$VIOLATION_SCOPES")

jq -n --arg reason "$REASON" '{ "decision": "block", "reason": $reason }'
