#!/bin/bash
# get-review-threads.sh
# Returns PR review threads with resolution status (READ-ONLY)
# Usage: get-review-threads.sh <pr_number> <owner> <repo>
# Example: get-review-threads.sh 15 bitwarden ai-plugins

set -euo pipefail

PR_NUMBER="${1:?PR number required}"
OWNER="${2:?Owner required}"
REPO="${3:?Repo required}"

# Validate PR_NUMBER is numeric
if ! [[ "$PR_NUMBER" =~ ^[0-9]+$ ]]; then
  echo "Error: PR number must be numeric" >&2
  exit 1
fi

# Validate OWNER and REPO match GitHub username/repo pattern (alphanumeric, hyphens, underscores)
if ! [[ "$OWNER" =~ ^[a-zA-Z0-9_-]+$ ]]; then
  echo "Error: Owner must contain only alphanumeric characters, hyphens, and underscores" >&2
  exit 1
fi

if ! [[ "$REPO" =~ ^[a-zA-Z0-9_.-]+$ ]]; then
  echo "Error: Repo name must contain only alphanumeric characters, hyphens, underscores, and dots" >&2
  exit 1
fi

gh api graphql -f query='
query($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          startLine
          diffSide
          comments(first: 10) {
            nodes {
              id
              body
              author { login }
              createdAt
            }
          }
        }
      }
    }
  }
}
' -f owner="$OWNER" -f repo="$REPO" -F pr="$PR_NUMBER"
