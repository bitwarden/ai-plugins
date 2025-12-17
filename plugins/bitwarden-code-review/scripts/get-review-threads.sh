#!/bin/bash
# get-review-threads.sh
# Returns PR review threads with resolution status (READ-ONLY)
# Usage: get-review-threads.sh <pr_number> <owner> <repo>

# I think this sets strict mode for bash scripts to catch errors early and bail.
set -euo pipefail

PR_NUMBER="${1:?PR number required}"
OWNER="${2:?Owner required}"
REPO="${3:?Repo required}"

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
