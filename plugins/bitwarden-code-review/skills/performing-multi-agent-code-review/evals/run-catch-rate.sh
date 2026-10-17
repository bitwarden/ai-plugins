#!/usr/bin/env bash
# Runs one catch-rate eval case: one corpus PR, one configuration, one run number.
# Usage: run-catch-rate.sh <eval-id> <with_skill|without_skill> <run-number>
# Env:   CLONES_DIR  directory holding a local clone of each corpus repo, named by repo (server, clients, ...)
#        OUT_DIR     scratch directory for checkouts, transcripts, and reports
#        MODEL       optional, defaults to opus
set -euo pipefail

EVALS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGINS_DIR="$(cd "$EVALS_DIR/../../../.." && pwd)"
EVAL_SET="$EVALS_DIR/catch-rate-eval.json"

id="$1"
config="$2"
run="$3"
: "${CLONES_DIR:?set CLONES_DIR}"
: "${OUT_DIR:?set OUT_DIR}"
model="${MODEL:-opus}"

[[ "$id" =~ ^[0-9]+$ ]] || { echo "eval id must be numeric" >&2; exit 1; }
[[ "$run" =~ ^[0-9]+$ ]] || { echo "run number must be numeric" >&2; exit 1; }
case "$config" in with_skill|without_skill) ;; *) echo "unknown configuration: $config" >&2; exit 1 ;; esac

case_json="$(jq -ce --argjson id "$id" '.evals[] | select(.id == $id)' "$EVAL_SET")"
repo="$(jq -r .repo <<<"$case_json")"
pr_url="$(jq -r .pr_url <<<"$case_json")"
head_sha="$(jq -r .head_sha <<<"$case_json")"
[[ "$repo" =~ ^bitwarden/[A-Za-z0-9._-]+$ ]] || { echo "unexpected repo: $repo" >&2; exit 1; }
[[ "$head_sha" =~ ^[0-9a-f]{40}$ ]] || { echo "unexpected head_sha: $head_sha" >&2; exit 1; }

run_dir="$OUT_DIR/$id/$config/run-$run"
checkout="$run_dir/repo"
report_dir="$run_dir/report"
mkdir -p "$report_dir"

# A shared clone keeps the user's clone untouched apart from the fetched head commit.
# The remote is pointed back at GitHub so `gh pr diff <number>` resolves the PR's repo from the checkout.
clone="$CLONES_DIR/${repo#bitwarden/}"
git -C "$clone" cat-file -e "$head_sha^{commit}" 2>/dev/null || git -C "$clone" fetch -q origin "$head_sha"
if [[ ! -d "$checkout/.git" ]]; then
  git clone -q --shared --no-checkout "$clone" "$checkout"
  git -C "$checkout" remote set-url origin "https://github.com/$repo.git"
  git -C "$checkout" checkout -q --detach "$head_sha"
  # Branches and tags from the source clone reach the later fix; drop them so a run cannot read the answer.
  git -C "$checkout" for-each-ref --format='delete %(refname)' | git -C "$checkout" update-ref --no-deref --stdin
fi

if [[ "$config" == with_skill ]]; then
  prompt="/bitwarden-code-review:performing-multi-agent-code-review $pr_url --output-dir $report_dir"
  plugin_args=(--plugin-dir "$PLUGINS_DIR/bitwarden-code-review" --plugin-dir "$PLUGINS_DIR/bitwarden-security-engineer")
else
  prompt="Review pull request $pr_url for defects. The working tree is checked out at the pull request's head commit. Write the review as markdown to $report_dir/review.md. Put every finding under a \`## Findings\` heading, each in its own subsection that gives its location as \`path/to/file.ext:<line>\` or \`path/to/file.ext:<start>-<end>\`."
  plugin_args=(--plugin-dir "$PLUGINS_DIR/bitwarden-security-engineer")
fi

# A corpus PR is untrusted input. dontAsk denies every call not allowed here. The deny list closes
# options that write files (--output) or run commands (--upload-pack) under an allowed git prefix.
allowed=(
  Read Grep Glob Skill Agent
  "Edit(/$report_dir/**)"
  "Bash(gh pr view:*)" "Bash(gh pr diff:*)"
  "Bash(git diff:*)" "Bash(git status:*)" "Bash(git log:*)" "Bash(git show:*)" "Bash(git rev-parse:*)"
  "Bash(git merge-base:*)" "Bash(git ls-files:*)"
  "Bash(ls:*)" "Bash(cat:*)" "Bash(head:*)" "Bash(wc:*)"
)
denied=(
  "Bash(git * --output*)" "Bash(git *--output=*)"
  "Bash(git * --upload-pack*)" "Bash(git *--upload-pack=*)"
)

# Without this note, one denied compound command led a run to stop using Bash altogether.
harness_note="Tool permissions in this session are an allow-list, enforced per command. Allowed Bash commands: gh pr view, gh pr diff, and read-only git subcommands (diff, status, log, show, rev-parse, merge-base, ls-files), plus ls, cat, head, and wc. Run each command on its own, not chained with && or ;. A denied command does not mean Bash is unavailable."

cd "$checkout"
env -u CLAUDECODE claude -p "$prompt" \
  --model "$model" \
  --setting-sources local \
  --permission-mode dontAsk \
  --allowedTools "${allowed[@]}" \
  --disallowedTools "${denied[@]}" \
  --append-system-prompt "$harness_note" \
  --no-session-persistence \
  --output-format stream-json --verbose \
  "${plugin_args[@]}" \
  >"$run_dir/run.jsonl" 2>"$run_dir/stderr.log" || echo "claude exited $? for $id/$config/run-$run" >&2
