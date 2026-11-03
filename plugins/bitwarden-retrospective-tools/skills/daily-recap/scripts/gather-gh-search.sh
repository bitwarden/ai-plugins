#!/usr/bin/env bash
# Pull the authenticated user's authored, reviewed, and commented pull requests for a
# window via GitHub's search API, and emit a compact JSON summary.
#
# gather-gh-events.sh reads the events feed, which holds at most 300 events from the
# last 30 days. This script instead issues paginated `gh api graphql` searches, so it
# has no such cap and can cover a multi-day window (e.g. a full week) in one run.
#
# Usage:
#   gather-gh-search.sh [START-DATE [END-DATE]]
#     With no dates: the same single-workday window gather-gh-events.sh defaults to
#       (yesterday once today's cutoff has passed, otherwise the day before), running
#       from the cutoff hour on that date to the cutoff hour on the next date.
#     With one date: a single workday starting on START-DATE, same as above.
#     With two dates: a multi-day window running from the cutoff hour on START-DATE to
#       the cutoff hour on the day after END-DATE, local time, so END-DATE is inclusive.
#       A 7-day run looks like `gather-gh-search.sh 2026-10-15 2026-10-21`.
#
# Environment:
#   DAILY_RECAP_CUTOFF_HOUR  Local hour (0-23) at which a workday begins. Default: 7.
#   TZ                       Standard timezone override, e.g. America/Los_Angeles.
#
# Output (stdout): a JSON object with "login", "window", "search_complete", "pr_count",
# and "prs". Each PR carries repo, number, title, state, is_draft, url, author, the
# user's role(s) (authored, reviewed, and/or commented), its in-window activity sorted
# by time, and last_activity. The window line and any pagination-cap warning also go to
# stderr. PR titles are passed through raw; HTML-escaping happens at render time.
#
# CRITICAL: GitHub's search `updated:>=` filter matches a PR's last-updated timestamp,
# not per-event activity, so every candidate PR's activity is filtered client-side
# against the window, and only activity performed by the user themselves is counted. A PR
# with no qualifying in-window activity by the user is dropped even if search found it.
#
# Requires: gh (authenticated), jq, and GNU or BSD date.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=SCRIPTDIR/date-utils.sh
source "${SCRIPT_DIR}/date-utils.sh"

die() {
  echo "gather-gh-search: $*" >&2
  exit 1
}

command -v jq >/dev/null 2>&1 || die "'jq' is required but not installed"

# Safety cap against unbounded pagination on a very busy window, per query.
readonly MAX_SEARCH_PAGES=20

cutoff_raw="${DAILY_RECAP_CUTOFF_HOUR:-7}"
if ! [[ "$cutoff_raw" =~ ^[0-9]{1,2}$ ]] || ((10#$cutoff_raw > 23)); then
  die "DAILY_RECAP_CUTOFF_HOUR must be a whole hour from 0 to 23 (got '${cutoff_raw}')"
fi
CUTOFF_HOUR=$((10#$cutoff_raw))
CUTOFF_HH="$(printf '%02d' "$CUTOFF_HOUR")"

TODAY="$(date +%Y-%m-%d)"
if [[ $# -ge 2 ]]; then
  DATE="$1"
  END_DATE="$2"
  is_valid_date "$DATE" || die "start date must be a real calendar date in YYYY-MM-DD form (got '${DATE}')"
  is_valid_date "$END_DATE" || die "end date must be a real calendar date in YYYY-MM-DD form (got '${END_DATE}')"
  [[ "$END_DATE" < "$DATE" ]] && die "end date (${END_DATE}) must not be before start date (${DATE})"
elif [[ $# -eq 1 ]]; then
  DATE="$1"
  is_valid_date "$DATE" || die "date must be a real calendar date in YYYY-MM-DD form (got '${DATE}')"
  END_DATE="$DATE"
elif ((10#$(date +%H) >= CUTOFF_HOUR)); then
  DATE="$(add_days "$TODAY" -1)"
  END_DATE="$DATE"
else
  DATE="$(add_days "$TODAY" -2)"
  END_DATE="$DATE"
fi

NEXT_DATE="$(add_days "$END_DATE" 1)"
START_EPOCH="$(local_to_epoch "${DATE} ${CUTOFF_HH}:00:00")" \
  || die "could not compute the window start for ${DATE} ${CUTOFF_HH}:00 local time"
END_EPOCH="$(local_to_epoch "${NEXT_DATE} ${CUTOFF_HH}:00:00")" \
  || die "could not compute the window end for ${NEXT_DATE} ${CUTOFF_HH}:00 local time"

START_UTC="$(epoch_fmt_utc "$START_EPOCH" '%Y-%m-%dT%H:%M:%SZ')"
END_UTC="$(epoch_fmt_utc "$END_EPOCH" '%Y-%m-%dT%H:%M:%SZ')"
START_LOCAL="$(epoch_fmt "$START_EPOCH" '%Y-%m-%dT%H:%M:%S%z')"
END_LOCAL="$(epoch_fmt "$END_EPOCH" '%Y-%m-%dT%H:%M:%S%z')"
TZ_LABEL="$(epoch_fmt "$START_EPOCH" '%Z')"

echo "# Window: ${START_UTC} -> ${END_UTC} (${CUTOFF_HH}:00 ${TZ_LABEL} boundary)" >&2

# Checked only after the window is printed, so a recap built without GitHub still has it.
command -v gh >/dev/null 2>&1 || die "'gh' is required but not installed"
LOGIN="$(gh api user --jq .login 2>/dev/null)" \
  || die "could not read your GitHub login; run 'gh auth login' and try again"

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/daily-recap-gh-search.XXXXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT

# Search's `updated:` qualifier matches a PR's *last* update time, not when the user's
# activity happened, so it can only be used as a floor: a PR worked on inside the window
# still gets dropped by an upper bound if anyone touches it again afterward (a merge, a CI
# push, a reply). Floor-only only needs to be as precise as a calendar date; the exact
# epoch filtering happens client-side in jq below. Over-scanning old date ranges is already
# handled by MAX_SEARCH_PAGES and its search_complete: false warning.
FLOOR="${START_UTC:0:10}"

AUTHORED_QUERY='
query($q: String!, $cursor: String) {
  search(query: $q, type: ISSUE, first: 50, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes {
      __typename
      ... on PullRequest {
        number
        title
        url
        state
        isDraft
        createdAt
        mergedAt
        author { login }
        repository { nameWithOwner }
        timelineItems(last: 100, itemTypes: [PULL_REQUEST_COMMIT, ISSUE_COMMENT, PULL_REQUEST_REVIEW, READY_FOR_REVIEW_EVENT]) {
          nodes {
            __typename
            ... on PullRequestCommit {
              commit { committedDate author { user { login } } }
            }
            ... on IssueComment {
              createdAt
              author { login }
            }
            ... on PullRequestReview {
              submittedAt
              author { login }
            }
            ... on ReadyForReviewEvent {
              createdAt
              actor { login }
            }
          }
        }
      }
    }
  }
}
'

REVIEWED_QUERY='
query($q: String!, $cursor: String) {
  search(query: $q, type: ISSUE, first: 50, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes {
      __typename
      ... on PullRequest {
        number
        title
        url
        state
        isDraft
        createdAt
        mergedAt
        author { login }
        repository { nameWithOwner }
        reviews(last: 100) {
          nodes {
            state
            submittedAt
            author { login }
          }
        }
      }
    }
  }
}
'

COMMENTED_QUERY='
query($q: String!, $cursor: String) {
  search(query: $q, type: ISSUE, first: 50, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes {
      __typename
      ... on PullRequest {
        number
        title
        url
        state
        isDraft
        createdAt
        mergedAt
        author { login }
        repository { nameWithOwner }
        comments(last: 100) {
          nodes {
            createdAt
            author { login }
          }
        }
      }
    }
  }
}
'

AUTHORED_Q="author:${LOGIN} type:pr updated:>=${FLOOR}"
REVIEWED_Q="reviewed-by:${LOGIN} type:pr -author:${LOGIN} updated:>=${FLOOR}"
COMMENTED_Q="commenter:${LOGIN} type:pr -author:${LOGIN} updated:>=${FLOOR}"

SEARCH_COMPLETE=true

# run_search LABEL QUERY_DOC SEARCH_STRING -> paginates the search, writing each page's
# nodes to WORK_DIR/<label>-pages/page-N.json and the combined node array to
# WORK_DIR/<label>-nodes.json. Dies naming LABEL on a transport failure, or on a non-null
# `errors` field when `.data.search` came back null (no usable data). If `.data.search`
# has usable data despite a non-null `errors` field (partial failure), warns on stderr
# and sets SEARCH_COMPLETE=false instead of dying. Also sets SEARCH_COMPLETE=false and
# warns on stderr if the safety cap is hit with more pages remaining.
run_search() {
  local label="$1" query="$2" search_string="$3"
  local pages_dir="${WORK_DIR}/${label}-pages"
  mkdir -p "$pages_dir"
  local cursor="" page=1 has_next="false"

  while ((page <= MAX_SEARCH_PAGES)); do
    local resp="${WORK_DIR}/${label}-resp-${page}.json"
    local err="${WORK_DIR}/${label}-err-${page}.txt"
    if [[ -z "$cursor" ]]; then
      gh api graphql -f query="$query" -f q="$search_string" >"$resp" 2>"$err" \
        || die "gh api graphql failed for the ${label} query: $(cat "$err")"
    else
      gh api graphql -f query="$query" -f q="$search_string" -f cursor="$cursor" >"$resp" 2>"$err" \
        || die "gh api graphql failed for the ${label} query: $(cat "$err")"
    fi

    local errs
    errs="$(jq -r 'if (.errors // null) != null then (.errors | tostring) else empty end' "$resp" 2>/dev/null || true)"
    if [[ -n "$errs" ]]; then
      if [[ "$(jq -r '.data.search // empty' "$resp")" == "" ]]; then
        die "gh api graphql returned errors for the ${label} query: ${errs}"
      fi
      echo "# Warning: partial errors on the ${label} query: ${errs}" >&2
      SEARCH_COMPLETE=false
    fi

    jq -c '.data.search.nodes // []' "$resp" >"${pages_dir}/page-${page}.json"

    has_next="$(jq -r '.data.search.pageInfo.hasNextPage // false' "$resp")"
    cursor="$(jq -r '.data.search.pageInfo.endCursor // empty' "$resp")"
    if [[ "$has_next" != "true" || -z "$cursor" ]]; then
      has_next="false"
      break
    fi
    page=$((page + 1))
  done

  if [[ "$has_next" == "true" ]]; then
    echo "# Warning: the ${label} search hit the ${MAX_SEARCH_PAGES}-page safety cap with more results remaining; some PRs may be missing." >&2
    SEARCH_COMPLETE=false
  fi

  jq -s 'add // []' "${pages_dir}"/page-*.json >"${WORK_DIR}/${label}-nodes.json"
}

run_search "authored" "$AUTHORED_QUERY" "$AUTHORED_Q"
run_search "reviewed" "$REVIEWED_QUERY" "$REVIEWED_Q"
run_search "commented" "$COMMENTED_QUERY" "$COMMENTED_Q"

# shape_search LABEL ROLE ACTIVITY_FILTER -> emits one JSON object (as a single-line
# array) per candidate PR that has at least one in-window activity entry attributable to
# the user themselves. ACTIVITY_FILTER is a jq expression, evaluated with $pr bound to the
# PullRequest node, that must produce a (possibly empty) stream of activity objects.
shape_search() {
  local label="$1" role="$2" activity_filter="$3"
  jq -c \
    --arg login "$LOGIN" --arg start "$START_UTC" --arg end "$END_UTC" --arg role "$role" '
    def in_window(t): (t != null) and (t >= $start) and (t < $end);
    [ .[]
      | select(.__typename == "PullRequest")
      | . as $pr
      | ('"$activity_filter"') as $activity
      | select(($activity | length) > 0)
      | {
          url: $pr.url,
          repo: $pr.repository.nameWithOwner,
          number: $pr.number,
          title: $pr.title,
          state: $pr.state,
          is_draft: $pr.isDraft,
          author: ($pr.author.login // null),
          role: $role,
          activity: $activity
        }
    ] | .[]
  ' "${WORK_DIR}/${label}-nodes.json" >"${WORK_DIR}/${label}-items.ndjson"
}

AUTHORED_ACTIVITY='
  ( [ (if in_window($pr.createdAt) then {time: $pr.createdAt, type: "opened"} else empty end) ]
    + [ ($pr.timelineItems.nodes // [])[]?
        | if .__typename == "PullRequestCommit" then
            (if ((.commit.author.user.login // "") == $login) and in_window(.commit.committedDate)
             then {time: .commit.committedDate, type: "commit"} else empty end)
          elif .__typename == "IssueComment" then
            (if ((.author.login // "") == $login) and in_window(.createdAt)
             then {time: .createdAt, type: "comment"} else empty end)
          elif .__typename == "PullRequestReview" then
            (if ((.author.login // "") == $login) and in_window(.submittedAt)
             then {time: .submittedAt, type: "review"} else empty end)
          elif .__typename == "ReadyForReviewEvent" then
            (if ((.actor.login // "") == $login) and in_window(.createdAt)
             then {time: .createdAt, type: "ready_for_review"} else empty end)
          else empty end
      ]
  )
'

REVIEWED_ACTIVITY='
  [ ($pr.reviews.nodes // [])[]?
    | select(((.author.login // "") == $login) and in_window(.submittedAt))
    | {time: .submittedAt, type: "review", review_state: .state}
  ]
'

COMMENTED_ACTIVITY='
  [ ($pr.comments.nodes // [])[]?
    | select(((.author.login // "") == $login) and in_window(.createdAt))
    | {time: .createdAt, type: "comment"}
  ]
'

shape_search "authored" "authored" "$AUTHORED_ACTIVITY"
shape_search "reviewed" "reviewed" "$REVIEWED_ACTIVITY"
shape_search "commented" "commented" "$COMMENTED_ACTIVITY"

: >"${WORK_DIR}/all-items.ndjson"
for label in authored reviewed commented; do
  cat "${WORK_DIR}/${label}-items.ndjson" >>"${WORK_DIR}/all-items.ndjson"
done

PRS_JSON="$(jq -s '
  group_by(.url)
  | map(
      .[0] as $base
      | . as $group
      | {
          repo: $base.repo,
          number: $base.number,
          title: $base.title,
          state: $base.state,
          is_draft: $base.is_draft,
          url: $base.url,
          author: $base.author,
          roles: (["authored", "reviewed", "commented"]
                  | map(select(. as $r | $group | any(.role == $r)))),
          activity: ([$group[].activity[]] | unique_by([.type, .time]) | sort_by(.time))
        }
      | . + {last_activity: (.activity | last | .time)}
    )
  | sort_by(.last_activity)
' "${WORK_DIR}/all-items.ndjson")"

jq -n \
  --arg login "$LOGIN" \
  --arg start_date "$DATE" \
  --arg end_date "$END_DATE" \
  --argjson cutoff "$CUTOFF_HOUR" \
  --arg tz "$TZ_LABEL" \
  --arg start "$START_UTC" \
  --arg end "$END_UTC" \
  --arg start_local "$START_LOCAL" \
  --arg end_local "$END_LOCAL" \
  --argjson complete "$SEARCH_COMPLETE" \
  --argjson prs "$PRS_JSON" '
  {
    login: $login,
    window: {
      start_date: $start_date,
      end_date: $end_date,
      cutoff_hour: $cutoff,
      timezone: $tz,
      start_utc: $start,
      end_utc: $end,
      start_local: $start_local,
      end_local: $end_local
    },
    search_complete: $complete,
    pr_count: ($prs | length),
    prs: $prs
  }
'
