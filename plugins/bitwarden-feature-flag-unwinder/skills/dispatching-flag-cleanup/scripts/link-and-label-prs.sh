#!/usr/bin/env bash
# Link a flag's cleanup PRs to each other and label them.
#
# Usage: link-and-label-prs.sh <flag> <step>
#
# Finds the open PR on `flag-cleanup/<flag>-step-<step>` in clients, server,
# ios, and android. When there is more than one, each PR body gets a
# "Related Step <N> PRs" block listing the others, inserted above the
# Objective heading. Every PR gets the `t:flagged-code-removal` label, its
# only type label, and loses `t:tech-debt` if a repo's labeler added it.
# Re-running is safe: the related block is replaced, not duplicated.
#
# Needs `gh` authenticated with pull-request write access to every repo that
# has a PR. Prints one line per PR and a warning for each change it couldn't
# make. Exits non-zero only on bad arguments.

# cspell:ignore gsub

set -uo pipefail

FLAG="${1:-}"
STEP="${2:-}"
if ! [[ "$FLAG" =~ ^[a-z0-9]+(-[a-z0-9]+)+$ ]] || ! [[ "$STEP" =~ ^[12]$ ]]; then
  echo "usage: $0 <flag> <1|2>" >&2
  exit 2
fi

LABEL="t:flagged-code-removal"
REPLACED_LABEL="t:tech-debt"
BRANCH="flag-cleanup/${FLAG}-step-${STEP}"
START='<!-- flag-cleanup-related -->'
END='<!-- /flag-cleanup-related -->'

declare -a REPOS=() NUMBERS=()
for repo in clients server ios android; do
  number=$(gh pr list --repo "bitwarden/$repo" --head "$BRANCH" --state open \
    --json number --jq '.[0].number // empty' 2>/dev/null) || number=""
  if [ -n "$number" ]; then
    REPOS+=("$repo")
    NUMBERS+=("$number")
  fi
done

if [ "${#REPOS[@]}" -eq 0 ]; then
  echo "No open PRs on $BRANCH."
  exit 0
fi

for i in "${!REPOS[@]}"; do
  repo="${REPOS[$i]}"
  number="${NUMBERS[$i]}"
  ref="bitwarden/$repo#$number"

  if [ "${#REPOS[@]}" -gt 1 ]; then
    related=""
    for j in "${!REPOS[@]}"; do
      [ "$j" -eq "$i" ] || related+="- bitwarden/${REPOS[$j]}#${NUMBERS[$j]}"$'\n'
    done
    block="${START}"$'\n'"Related Step ${STEP} PRs for \`${FLAG}\`:"$'\n\n'"${related}${END}"$'\n\n'

    body_file=$(mktemp)
    if gh pr view "$number" --repo "bitwarden/$repo" --json body --jq '.body' \
      | jq -Rjs --arg start "$START" --arg end "$END" --arg block "$block" '
          # Drop a block from an earlier run, then insert above the Objective
          # heading, or append when the body has none.
          gsub("\($start)[\\s\\S]*?\($end)\\n*"; "")
          | if test("(?m)^## .*Objective") then sub("(?m)(?<h>^## .*Objective)"; "\($block)\(.h)")
            else . + "\n\n" + $block end' > "$body_file" \
      && gh pr edit "$number" --repo "bitwarden/$repo" --body-file "$body_file" >/dev/null; then
      echo "$ref: linked to the other PRs"
    else
      echo "::warning::$ref: could not update the PR body"
    fi
    rm -f "$body_file"
  fi

  if ! gh api "repos/bitwarden/$repo/labels/$LABEL" --silent 2>/dev/null; then
    echo "::warning::$ref: label $LABEL does not exist in bitwarden/$repo, not labeled"
    continue
  fi
  if gh pr edit "$number" --repo "bitwarden/$repo" --add-label "$LABEL" >/dev/null; then
    echo "$ref: labeled $LABEL"
    gh pr edit "$number" --repo "bitwarden/$repo" --remove-label "$REPLACED_LABEL" >/dev/null 2>&1 || true
  else
    echo "::warning::$ref: could not add label $LABEL"
  fi
done
