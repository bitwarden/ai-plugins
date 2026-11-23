#!/usr/bin/env bash
# Pull the authenticated user's Jira and Confluence activity for one workday and emit a
# compact JSON summary.
#
# A workday runs from the cutoff hour on the given date to the cutoff hour on the next
# date, in local time, so work done after midnight counts toward the day it continues.
#
# Usage:
#   gather-atlassian.sh [YYYY-MM-DD]
#     The workday to collect, named by the local date it starts on. Defaults to the most
#     recently completed workday (yesterday once today's cutoff has passed, otherwise
#     the day before).
#
# Environment:
#   DAILY_RECAP_CUTOFF_HOUR               Local hour (0-23) at which a workday begins. Default: 7.
#   TZ                                    Standard timezone override, e.g. America/Los_Angeles.
#   ATLASSIAN_CLOUD_ID                    Atlassian Cloud ID, used to build the gateway base URLs.
#   ATLASSIAN_EMAIL                       Atlassian account email, used for basic auth.
#   ATLASSIAN_JIRA_READ_ONLY_TOKEN        Atlassian API token scoped for Jira read access.
#   ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN  Atlassian API token scoped for Confluence read access.
#
# Output (stdout): a JSON object with "jira" and "confluence" keys. The two are entirely
# independent: each is null (with its own stderr notice) when its credentials are unset
# or its identity check fails, regardless of whether the other succeeded -- the recap
# must not fail, or lose one service's data, because the other is unavailable.
#
# "jira" holds account_id, site_url, window, complete, and issues (each issue carries a
# returned flag when the user moved it backward in status within the window).
# "confluence" holds account_id, site_url, window, complete, and pages (each page: title,
# space_key, space_id, created, version_count, url) when present. The window line for
# both goes to stderr before either credential check, so a recap built without Atlassian
# still has it. "complete" is false, with a matching stderr warning, when the
# MAX_SEARCH_PAGES safety cap truncated that service's search before exhausting all pages.
#
# Requires: curl, jq, and GNU or BSD date. Never prints a token: auth for each service
# goes through its own private, mode-600 netrc file in a temp directory removed on exit,
# rather than on the curl command line where `ps` could see it.

# cspell:ignore issuekey strptime todateiso lastmodified tonumber

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=SCRIPTDIR/date-utils.sh
source "${SCRIPT_DIR}/date-utils.sh"

die() {
  echo "gather-atlassian: $*" >&2
  exit 1
}

# Pages of search results, for either service, beyond this are not collected (safety cap
# against unbounded pagination on a very busy window). Overridable only so tests can force
# the cap without needing ten-plus pages of fixture data; not documented as a user-facing
# knob.
readonly MAX_SEARCH_PAGES="${DAILY_RECAP_MAX_SEARCH_PAGES:-10}"

command -v jq >/dev/null 2>&1 || die "'jq' is required but not installed"

cutoff_raw="${DAILY_RECAP_CUTOFF_HOUR:-7}"
if ! [[ "$cutoff_raw" =~ ^[0-9]{1,2}$ ]] || ((10#$cutoff_raw > 23)); then
  die "DAILY_RECAP_CUTOFF_HOUR must be a whole hour from 0 to 23 (got '${cutoff_raw}')"
fi
CUTOFF_HOUR=$((10#$cutoff_raw))
CUTOFF_HH="$(printf '%02d' "$CUTOFF_HOUR")"

TODAY="$(date +%Y-%m-%d)"
if [[ $# -ge 1 ]]; then
  DATE="$1"
  is_valid_date "$DATE" || die "date must be a real calendar date in YYYY-MM-DD form (got '${DATE}')"
elif ((10#$(date +%H) >= CUTOFF_HOUR)); then
  DATE="$(add_days "$TODAY" -1)"
else
  DATE="$(add_days "$TODAY" -2)"
fi

NEXT_DATE="$(add_days "$DATE" 1)"
START_EPOCH="$(local_to_epoch "${DATE} ${CUTOFF_HH}:00:00")" \
  || die "could not compute the window start for ${DATE} ${CUTOFF_HH}:00 local time"
END_EPOCH="$(local_to_epoch "${NEXT_DATE} ${CUTOFF_HH}:00:00")" \
  || die "could not compute the window end for ${NEXT_DATE} ${CUTOFF_HH}:00 local time"

START_UTC="$(epoch_fmt_utc "$START_EPOCH" '%Y-%m-%dT%H:%M:%SZ')"
END_UTC="$(epoch_fmt_utc "$END_EPOCH" '%Y-%m-%dT%H:%M:%SZ')"
TZ_LABEL="$(epoch_fmt "$START_EPOCH" '%Z')"

echo "# Window: ${START_UTC} -> ${END_UTC} (${CUTOFF_HH}:00 ${TZ_LABEL} boundary)" >&2

# A day-widened JQL/CQL window, shared in spirit by both services: Atlassian query
# languages' date literals are evaluated in a tenant/user timezone that may not match TZ
# here, so both collectors widen their query bounds by a day on each side and then apply
# an exact epoch filter in jq afterward.
WIDE_START="$(add_days "$DATE" -1) 00:00"
WIDE_END="$(add_days "$NEXT_DATE" 1) 23:59"

# report_api_error LABEL RESPONSE_FILE -> prints the response's errorMessages (or
# errors) to stderr, if any, so a future failure is diagnosable without printing the
# whole body (which could echo back request content). Never touches credentials: the
# Atlassian error payload is JSON describing the request, not the auth headers. Jira's
# error shape (errorMessages array, errors object) is covered directly; Confluence v1/v2
# error shapes (message/errors array of objects) are not fully covered by this yet --
# failures still surface the HTTP status even when this extracts no message.
report_api_error() {
  local label="$1" resp_file="$2"
  local messages
  messages="$(jq -r '
    [ (.errorMessages // [])[],
      ((.errors // {}) | to_entries[]? | "\(.key): \(.value)")
    ] | join("; ")
  ' "$resp_file" 2>/dev/null || true)"
  if [[ -n "$messages" ]]; then
    echo "gather-atlassian: ${label}: ${messages}" >&2
  fi
}

# write_netrc FILE TOKEN -> writes a mode-600 netrc entry for api.atlassian.com with the
# given token as the password, so the token never appears on a curl command line (where
# `ps` could see it) or in this script's own logging.
write_netrc() {
  local file="$1" token="$2"
  (
    umask 077
    {
      echo "machine api.atlassian.com"
      echo "login ${ATLASSIAN_EMAIL}"
      echo "password ${token}"
    } >"$file"
  )
}

# curl_api NETRC BASE METHOD PATH OUT_FILE [DATA_FILE] -> prints the HTTP status code to
# stdout, writes the response body to OUT_FILE. METHOD is GET or POST. NETRC and BASE
# are passed explicitly so Jira and Confluence calls -- different tokens, different
# gateway paths, same host -- never share a netrc entry.
curl_api() {
  local netrc="$1" base="$2" method="$3" path="$4" out="$5" data="${6:-}"
  local url="${base}${path}"
  if [[ -n "$data" ]]; then
    curl -sS --netrc-file "$netrc" \
      -H "Accept: application/json" -H "Content-Type: application/json" \
      -X "$method" --data-binary "@${data}" \
      -o "$out" -w '%{http_code}' "$url"
  else
    curl -sS --netrc-file "$netrc" \
      -H "Accept: application/json" \
      -X "$method" \
      -o "$out" -w '%{http_code}' "$url"
  fi
}

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/daily-recap-atlassian.XXXXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT INT TERM HUP

# jira_ts_to_epoch "2026-10-20T10:00:00.000+0000" -> epoch seconds.
# Jira's own timestamps carry milliseconds and a numeric (non-colon) UTC offset, which
# neither GNU nor BSD date parses with the Z-only helpers in date-utils.sh.
jira_ts_to_epoch() {
  local ts="$1"
  date -u -d "$ts" +%s 2>/dev/null && return
  date -j -f '%Y-%m-%dT%H:%M:%S%z' "$(sed -E 's/\.[0-9]+//' <<<"$ts")" +%s 2>/dev/null
}

# confluence_ts_to_epoch "2026-10-20T10:00:00.000Z" -> epoch seconds.
# Confluence's v2 timestamps carry milliseconds before the Z, which BSD date's strict
# formatter cannot parse directly.
confluence_ts_to_epoch() {
  local ts="$1"
  date -u -d "$ts" +%s 2>/dev/null && return
  date -j -u -f '%Y-%m-%dT%H:%M:%S' "$(sed -E 's/\.[0-9]+Z$//' <<<"$ts")" +%s 2>/dev/null
}

# =============================================================================
# Jira
# =============================================================================
collect_jira() {
  if [[ -z "${ATLASSIAN_CLOUD_ID:-}" || -z "${ATLASSIAN_EMAIL:-}" || -z "${ATLASSIAN_JIRA_READ_ONLY_TOKEN:-}" ]]; then
    echo "gather-atlassian: Jira credentials not set; skipping Jira" >&2
    echo 'null'
    return 0
  fi

  command -v curl >/dev/null 2>&1 || die "'curl' is required but not installed"

  skip_jira() {
    echo "gather-atlassian: $*; skipping Jira" >&2
    echo 'null'
    exit 0
  }

  local BASE_URL="https://api.atlassian.com/ex/jira/${ATLASSIAN_CLOUD_ID}"
  local NETRC_FILE="${WORK_DIR}/jira-netrc"
  write_netrc "$NETRC_FILE" "$ATLASSIAN_JIRA_READ_ONLY_TOKEN"

  # ---------------------------------------------------------------------------
  # Identity check. /search/jql can return 200 on bad credentials, so verify who we are
  # first via /myself.
  # ---------------------------------------------------------------------------
  local MYSELF_FILE="${WORK_DIR}/myself.json"
  local status
  status="$(curl_api "$NETRC_FILE" "$BASE_URL" GET "/rest/api/3/myself" "$MYSELF_FILE")" || status="000"
  if [[ ! "$status" =~ ^2 ]]; then
    report_api_error "identity check" "$MYSELF_FILE"
    skip_jira "Jira identity check failed (HTTP ${status})"
  fi
  local ACCOUNT_ID
  ACCOUNT_ID="$(jq -r '.accountId // empty' "$MYSELF_FILE" 2>/dev/null || true)"
  if [[ -z "$ACCOUNT_ID" ]]; then
    skip_jira "Jira identity check returned no accountId"
  fi

  # Best-effort tenant hostname for human-readable browse URLs. Not fatal if it fails;
  # issues just carry a null url.
  local SITE_URL=""
  local SERVER_INFO_FILE="${WORK_DIR}/server-info.json"
  if status="$(curl_api "$NETRC_FILE" "$BASE_URL" GET "/rest/api/3/serverInfo" "$SERVER_INFO_FILE" 2>/dev/null)" && [[ "$status" =~ ^2 ]]; then
    SITE_URL="$(jq -r '.baseUrl // empty' "$SERVER_INFO_FILE" 2>/dev/null || true)"
  fi

  # ---------------------------------------------------------------------------
  # Search for candidate issues: assigned to or reported by the user, status-transitioned
  # by the user, or otherwise updated (which includes commenting) by the user, within a
  # day-widened window (Jira JQL dates are in the user's Jira timezone, which may not
  # match TZ here -- widened bounds plus an exact epoch filter in jq below cover that).
  #
  # `status CHANGED BY ... DURING (...)` and `issuekey IN updatedBy(...)` are what
  # surface issues the user transitioned or commented on without being assignee or
  # reporter -- validated live against Jira Cloud's /search/jql gateway endpoint.
  # updatedBy() is broader than comments alone (any field edit by the user), but the
  # per-issue comment fetch below filters precisely to the user's own in-window comments,
  # so the extra candidates it pulls in just cost a comment fetch, not a false positive.
  # ---------------------------------------------------------------------------
  local JQL="(assignee = \"${ACCOUNT_ID}\" OR reporter = \"${ACCOUNT_ID}\" OR status CHANGED BY \"${ACCOUNT_ID}\" DURING (\"${WIDE_START}\", \"${WIDE_END}\") OR issuekey IN updatedBy(\"${ACCOUNT_ID}\", \"${WIDE_START}\", \"${WIDE_END}\")) AND updated >= \"${WIDE_START}\" ORDER BY updated DESC"

  local FIELDS_JSON='["summary","status","created","updated","reporter","assignee"]'

  local ISSUES_PAGES_DIR="${WORK_DIR}/pages"
  mkdir -p "$ISSUES_PAGES_DIR"

  local page=1 next_token="" body_file resp_file is_last complete=true
  while ((page <= MAX_SEARCH_PAGES)); do
    body_file="${WORK_DIR}/search-body-${page}.json"
    # `expand` must be the comma-joined string form ("changelog"), not a JSON array, on
    # POST /rest/api/3/search/jql -- an array there is rejected with a bare HTTP 400
    # "Invalid request payload" (confirmed live against the gateway endpoint).
    if [[ -z "$next_token" ]]; then
      jq -n --arg jql "$JQL" --argjson fields "$FIELDS_JSON" \
        '{jql: $jql, fields: $fields, expand: "changelog", maxResults: 50}' >"$body_file"
    else
      jq -n --arg jql "$JQL" --argjson fields "$FIELDS_JSON" --arg token "$next_token" \
        '{jql: $jql, fields: $fields, expand: "changelog", maxResults: 50, nextPageToken: $token}' >"$body_file"
    fi

    resp_file="${WORK_DIR}/search-resp-${page}.json"
    status="$(curl_api "$NETRC_FILE" "$BASE_URL" POST "/rest/api/3/search/jql" "$resp_file" "$body_file")" || status="000"
    if [[ ! "$status" =~ ^2 ]]; then
      report_api_error "search" "$resp_file"
      skip_jira "Jira search failed (HTTP ${status})"
    fi

    jq '.issues // []' "$resp_file" >"${ISSUES_PAGES_DIR}/page-${page}.json"

    is_last="$(jq -r 'if .isLast == false then "false" else "true" end' "$resp_file")"
    next_token="$(jq -r '.nextPageToken // empty' "$resp_file")"
    if [[ "$is_last" == "true" || -z "$next_token" ]]; then
      break
    fi
    page=$((page + 1))
  done

  if [[ "$is_last" == "false" && -n "$next_token" ]]; then
    echo "gather-atlassian: the Jira search hit the ${MAX_SEARCH_PAGES}-page safety cap with more results remaining; some issues may be missing." >&2
    complete=false
  fi

  local ISSUES_ALL="${WORK_DIR}/issues-all.json"
  jq -s 'add // []' "${ISSUES_PAGES_DIR}"/page-*.json >"$ISSUES_ALL"

  # ---------------------------------------------------------------------------
  # Attach the user's comments per candidate issue (single page per issue is enough for
  # one workday's worth of activity, since we request newest-first ordering so the
  # first page always holds the most recent comments).
  # ---------------------------------------------------------------------------
  local MERGED="${WORK_DIR}/merged.json"
  jq -c '.[]' "$ISSUES_ALL" | while IFS= read -r issue; do
    key="$(jq -r '.key' <<<"$issue")"
    comment_file="${WORK_DIR}/comments-${key}.json"
    c_status="$(curl_api "$NETRC_FILE" "$BASE_URL" GET "/rest/api/3/issue/${key}/comment?maxResults=100&orderBy=-created" "$comment_file")" || c_status="000"
    # Slim the comment payload down to the two fields the final jq pass below actually
    # consumes (created, author.accountId) and pass it through a file via --slurpfile
    # rather than argv: a busy issue's full comment history can exceed Linux's
    # MAX_ARG_STRLEN (131072 bytes) for a single argv string, which fails execve with
    # E2BIG -- silently, since this loop runs inside collect_jira's $(...) subshell
    # where errexit is disabled.
    comment_slim_file="${WORK_DIR}/comments-slim-${key}.json"
    if [[ "$c_status" =~ ^2 ]]; then
      jq -c '[.comments[]? | {created, author: {accountId: .author.accountId}}]' "$comment_file" \
        >"$comment_slim_file" || echo '[]' >"$comment_slim_file"
    else
      echo '[]' >"$comment_slim_file"
    fi
    jq -c --slurpfile c "$comment_slim_file" '. + {comments: $c[0]}' <<<"$issue"
  done >"${WORK_DIR}/merged.ndjson"
  jq -s '.' "${WORK_DIR}/merged.ndjson" >"$MERGED"

  # ---------------------------------------------------------------------------
  # Convert every timestamp we might need (changelog entries, issue created/updated,
  # comment created) to epoch seconds once, in bash, so window comparisons do not rely
  # on jq's platform-dependent strptime.
  # ---------------------------------------------------------------------------
  local TIMESTAMPS_FILE="${WORK_DIR}/timestamps.txt"
  jq -r '
    [ .[]
      | .fields.created, .fields.updated,
        (.changelog.histories[]?.created), (.comments[]?.created)
    ] | map(select(. != null)) | unique | .[]
  ' "$MERGED" >"$TIMESTAMPS_FILE"

  local TS_MAP_FILE="${WORK_DIR}/ts_map.json"
  local TS_EPOCH_PAIRS="${WORK_DIR}/ts_epoch_pairs.tsv"
  : >"$TS_EPOCH_PAIRS"
  local ts epoch
  while IFS= read -r ts; do
    [[ -z "$ts" ]] && continue
    epoch="$(jira_ts_to_epoch "$ts" 2>/dev/null || true)"
    printf '%s\t%s\n' "$ts" "$epoch" >>"$TS_EPOCH_PAIRS"
  done <"$TIMESTAMPS_FILE"

  jq -Rn '
    [ inputs
      | select(. != "")
      | split("\t")
      | {key: .[0], value: (if (.[1] // "") == "" then null else (.[1] | tonumber) end)}
    ] | from_entries
  ' "$TS_EPOCH_PAIRS" >"$TS_MAP_FILE"

  local FINAL_JQ="${WORK_DIR}/final.jq"
  cat >"$FINAL_JQ" <<'JQ_PROGRAM'
# Coarse status-category ranking used only to detect a backward ("returned") status
# transition from changelog fromString/toString names, which carry no category info
# of their own. Unrecognized names are treated as an in-progress-like middle rank.
def rank(name):
  if name == null then 1
  elif (name == "To Do" or name == "Open" or name == "Backlog" or name == "New" or name == "Blocked") then 0
  elif (name == "In Review" or name == "In QA" or name == "QA" or name == "Ready for Review" or name == "In Testing" or name == "Code Review") then 2
  elif (name == "Done" or name == "Closed" or name == "Resolved") then 3
  else 1
  end;

def epoch_of(ts): if ts == null then null else ($ts_map_file[0][ts] // null) end;

def in_window(ts): (epoch_of(ts)) as $e | ($e != null and $e >= $start_epoch and $e < $end_epoch);

( [ .[]
    | . as $issue
    | ($issue.changelog.histories // []) as $histories
    | ($issue.comments // []) as $comments
    | {
        key: $issue.key,
        summary: ($issue.fields.summary // ""),
        status: ($issue.fields.status.name // null),
        status_category: ($issue.fields.status.statusCategory.name // null),
        url: (if $site_url != "" then ($site_url + "/browse/" + $issue.key) else null end),
        reporter_id: ($issue.fields.reporter.accountId // null),
        assignee_id: ($issue.fields.assignee.accountId // null),
        created_in_window: in_window($issue.fields.created),
        updated_in_window: in_window($issue.fields.updated),
        transitions: [
          $histories[]
          | select(.author.accountId == $account_id)
          | select(in_window(.created))
          | . as $h
          | .items[]?
          | select(.field == "status")
          | {from: .fromString, to: .toString, at: (epoch_of($h.created) | todateiso8601)}
        ],
        comment_count: ([
          $comments[]
          | select(.author.accountId == $account_id)
          | select(in_window(.created))
        ] | length)
      }
  ]
  # Transitions TO "Blocked" never count as "returned": blocking your own ticket
  # isn't the same as a reviewer bouncing it back, regardless of rank.
  | map(. + {returned: ([.transitions[] | select(rank(.to) < rank(.from) and .to != "Blocked")] | length > 0)})
) as $enriched
| {
    account_id: $account_id,
    site_url: (if $site_url != "" then $site_url else null end),
    window: { start_utc: $start_utc, end_utc: $end_utc },
    complete: $complete,
    issues: [
      $enriched[]
      | {
          key: .key,
          summary: .summary,
          status: .status,
          status_category: .status_category,
          url: .url,
          involvement: (
            [ (if (.created_in_window and .reporter_id == $account_id) then "created" else empty end),
              (if (.transitions | length) > 0 then "transitioned" else empty end),
              (if .comment_count > 0 then "commented" else empty end),
              (if (.assignee_id == $account_id and .updated_in_window) then "assigned" else empty end)
            ]
          ),
          transitions: .transitions,
          comment_count: .comment_count,
          returned: .returned
        }
      | select((.involvement | length) > 0)
    ]
  }
JQ_PROGRAM

  jq -f "$FINAL_JQ" \
    --slurpfile ts_map_file "$TS_MAP_FILE" \
    --arg account_id "$ACCOUNT_ID" \
    --arg site_url "${SITE_URL}" \
    --argjson start_epoch "$START_EPOCH" \
    --argjson end_epoch "$END_EPOCH" \
    --arg start_utc "$START_UTC" \
    --arg end_utc "$END_UTC" \
    --argjson complete "$complete" \
    "$MERGED"
}

# =============================================================================
# Confluence
# =============================================================================
collect_confluence() {
  if [[ -z "${ATLASSIAN_CLOUD_ID:-}" || -z "${ATLASSIAN_EMAIL:-}" || -z "${ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN:-}" ]]; then
    echo "gather-atlassian: Confluence credentials not set; skipping Confluence" >&2
    echo 'null'
    return 0
  fi

  command -v curl >/dev/null 2>&1 || die "'curl' is required but not installed"

  skip_confluence() {
    echo "gather-atlassian: $*; skipping Confluence" >&2
    echo 'null'
    exit 0
  }

  # The gateway's Confluence path includes the "/wiki" segment the product's own REST
  # API lives under, same as a self-managed site's https://<site>/wiki.
  local BASE_URL="https://api.atlassian.com/ex/confluence/${ATLASSIAN_CLOUD_ID}/wiki"
  local NETRC_FILE="${WORK_DIR}/confluence-netrc"
  write_netrc "$NETRC_FILE" "$ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN"

  # ---------------------------------------------------------------------------
  # Identity check, applying the same precaution as Jira's /myself: verify who we are
  # before trusting any search results, in case a bad-credentials request still returns
  # a usable-looking 200.
  # ---------------------------------------------------------------------------
  local MYSELF_FILE="${WORK_DIR}/confluence-myself.json"
  local status
  status="$(curl_api "$NETRC_FILE" "$BASE_URL" GET "/rest/api/user/current" "$MYSELF_FILE")" || status="000"
  if [[ ! "$status" =~ ^2 ]]; then
    report_api_error "Confluence identity check" "$MYSELF_FILE"
    skip_confluence "Confluence identity check failed (HTTP ${status})"
  fi
  local ACCOUNT_ID
  ACCOUNT_ID="$(jq -r '.accountId // empty' "$MYSELF_FILE" 2>/dev/null || true)"
  if [[ -z "$ACCOUNT_ID" ]]; then
    skip_confluence "Confluence identity check returned no accountId"
  fi

  # ---------------------------------------------------------------------------
  # CQL search (v1 content search) for candidate pages the user contributed to in a
  # day-widened window. "contributor" covers both the page creator and anyone who has
  # edited it, so each candidate is confirmed against its version history below before
  # being counted as this user's activity.
  # ---------------------------------------------------------------------------
  local CQL="contributor = \"${ACCOUNT_ID}\" and type = page and lastmodified >= \"${WIDE_START}\" order by lastmodified desc"
  local CQL_ENCODED
  CQL_ENCODED="$(jq -rn --arg c "$CQL" '$c | @uri')"

  local CONFLUENCE_PAGES_DIR="${WORK_DIR}/confluence-pages"
  mkdir -p "$CONFLUENCE_PAGES_DIR"

  local SITE_BASE=""
  local page=1 next_path resp_file next_href complete=true
  next_path="/rest/api/search?cql=${CQL_ENCODED}&limit=25&expand=content.version,content.space,content.history"
  while ((page <= MAX_SEARCH_PAGES)) && [[ -n "$next_path" ]]; do
    resp_file="${WORK_DIR}/confluence-search-${page}.json"
    # The expand value here is a comma-joined query-string value, not a JSON array, by
    # construction -- GET query parameters are always strings -- so the array-vs-string
    # 400 Jira's POST /search/jql hits does not apply to this GET call.
    status="$(curl_api "$NETRC_FILE" "$BASE_URL" GET "$next_path" "$resp_file")" || status="000"
    if [[ ! "$status" =~ ^2 ]]; then
      report_api_error "Confluence search" "$resp_file"
      skip_confluence "Confluence search failed (HTTP ${status})"
    fi

    if [[ "$page" -eq 1 ]]; then
      SITE_BASE="$(jq -r '._links.base // empty' "$resp_file" 2>/dev/null || true)"
    fi

    jq '.results // []' "$resp_file" >"${CONFLUENCE_PAGES_DIR}/page-${page}.json"

    next_href="$(jq -r '._links.next // empty' "$resp_file" 2>/dev/null || true)"
    if [[ -z "$next_href" ]]; then
      next_path=""
    else
      next_path="$next_href"
    fi
    page=$((page + 1))
  done

  if [[ -n "$next_path" ]]; then
    echo "gather-atlassian: the Confluence search hit the ${MAX_SEARCH_PAGES}-page safety cap with more results remaining; some pages may be missing." >&2
    complete=false
  fi

  local CONFLUENCE_ALL="${WORK_DIR}/confluence-all.json"
  jq -s 'add // []' "${CONFLUENCE_PAGES_DIR}"/page-*.json >"$CONFLUENCE_ALL"

  # ---------------------------------------------------------------------------
  # spaceId resolution. Confluence v2 endpoints (the page version-history call below)
  # key on the numeric spaceId, not the space key the v1 CQL search above returns, so
  # each distinct space key found among the candidates is resolved once via
  # GET /api/v2/spaces?keys=<key> and cached for the rest of this run.
  # ---------------------------------------------------------------------------
  local SPACE_ID_MAP_FILE="${WORK_DIR}/space-id-map.json"
  echo '{}' >"$SPACE_ID_MAP_FILE"

  resolve_space_id() {
    local key="$1"
    [[ -z "$key" ]] && return 0
    local cached
    cached="$(jq -r --arg k "$key" '.[$k] // empty' "$SPACE_ID_MAP_FILE" 2>/dev/null || true)"
    if [[ -n "$cached" ]]; then
      echo "$cached"
      return 0
    fi
    local resp="${WORK_DIR}/confluence-space-${key}.json"
    local s id=""
    s="$(curl_api "$NETRC_FILE" "$BASE_URL" GET "/api/v2/spaces?keys=${key}" "$resp")" || s="000"
    if [[ "$s" =~ ^2 ]]; then
      id="$(jq -r '.results[0].id // empty' "$resp" 2>/dev/null || true)"
    else
      report_api_error "Confluence space lookup for ${key}" "$resp"
    fi
    jq --arg k "$key" --arg v "$id" '.[$k] = $v' "$SPACE_ID_MAP_FILE" >"${SPACE_ID_MAP_FILE}.tmp" \
      && mv "${SPACE_ID_MAP_FILE}.tmp" "$SPACE_ID_MAP_FILE"
    echo "$id"
  }

  # fetch_version_matches PAGE_ID -> the page's v2 version-history results (JSON array),
  # or "[]" on a fetch failure for that page. A single page's version fetch failing does
  # not fail the whole collector, matching the reference collector's per-page tolerance.
  fetch_version_matches() {
    local page_id="$1"
    local resp="${WORK_DIR}/confluence-versions-${page_id}.json"
    local s
    s="$(curl_api "$NETRC_FILE" "$BASE_URL" GET "/api/v2/pages/${page_id}/versions?limit=50" "$resp")" || s="000"
    if [[ ! "$s" =~ ^2 ]]; then
      echo "gather-atlassian: Confluence version fetch failed for page ${page_id} (HTTP ${s}); skipping page" >&2
      echo "[]"
      return 0
    fi
    jq -c '.results // []' "$resp" 2>/dev/null || echo "[]"
  }

  # ---------------------------------------------------------------------------
  # Per-candidate confirmation: only pages where this account authored at least one
  # version inside the window are included, same confirm-via-version-history gate the
  # reference Python collector uses to filter the CQL search's broader "contributor"
  # match down to this user's actual in-window edits.
  # ---------------------------------------------------------------------------
  jq -c '.[]' "$CONFLUENCE_ALL" | while IFS= read -r item; do
    page_id="$(jq -r '.content.id // empty' <<<"$item")"
    [[ -z "$page_id" ]] && continue
    title="$(jq -r '.content.title // ""' <<<"$item")"
    space_key="$(jq -r '.content.space.key // ""' <<<"$item")"
    webui="$(jq -r '.content._links.webui // ""' <<<"$item")"

    space_id="$(resolve_space_id "$space_key")"
    versions_json="$(fetch_version_matches "$page_id")"

    in_window_matches="[]"
    while IFS= read -r v; do
      [[ -z "$v" ]] && continue
      author_id="$(jq -r '.authorId // empty' <<<"$v")"
      [[ "$author_id" != "$ACCOUNT_ID" ]] && continue
      created_at="$(jq -r '.createdAt // empty' <<<"$v")"
      epoch="$(confluence_ts_to_epoch "$created_at" 2>/dev/null || true)"
      if [[ -n "$epoch" ]] && ((epoch >= START_EPOCH && epoch < END_EPOCH)); then
        in_window_matches="$(jq -c --argjson v "$v" '. + [$v]' <<<"$in_window_matches")"
      fi
    done < <(jq -c '.[]' <<<"$versions_json")

    version_count="$(jq 'length' <<<"$in_window_matches")"
    # Not confirmed as this user's edit within the window: the CQL "contributor" match
    # was stale, out-of-window, or belonged to someone else despite the field name.
    ((version_count == 0)) && continue

    created_flag="$(jq '[ .[] | select(.number == 1) ] | length > 0' <<<"$in_window_matches")"

    page_url="$webui"
    if [[ -n "$SITE_BASE" && "$webui" != http* ]]; then
      page_url="${SITE_BASE}${webui}"
    fi

    jq -n --arg title "$title" --arg space_key "$space_key" --arg space_id "$space_id" \
      --argjson created "$created_flag" --argjson version_count "$version_count" \
      --arg url "$page_url" \
      '{
         title: $title,
         space_key: $space_key,
         space_id: (if $space_id == "" then null else $space_id end),
         created: $created,
         version_count: $version_count,
         url: (if $url == "" then null else $url end)
       }'
  done >"${WORK_DIR}/confluence-result.ndjson"

  local PAGES_JSON
  PAGES_JSON="$(jq -s '.' "${WORK_DIR}/confluence-result.ndjson")"

  jq -n --arg account_id "$ACCOUNT_ID" --arg site_url "${SITE_BASE}" \
    --arg start_utc "$START_UTC" --arg end_utc "$END_UTC" --argjson pages "$PAGES_JSON" \
    --argjson complete "$complete" \
    '{
       account_id: $account_id,
       site_url: (if $site_url == "" then null else $site_url end),
       window: { start_utc: $start_utc, end_utc: $end_utc },
       complete: $complete,
       pages: $pages
     }'
}

JIRA_VALUE="$(collect_jira)"
CONFLUENCE_VALUE="$(collect_confluence)"

jq -n -c --argjson jira "$JIRA_VALUE" --argjson confluence "$CONFLUENCE_VALUE" \
  '{jira: $jira, confluence: $confluence}'
