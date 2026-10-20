#!/usr/bin/env bash
# List Claude Code sessions with activity inside a UTC window, with a short digest of each.
#
# Usage:
#   find-sessions.sh START_UTC END_UTC [--include-home]
#     START_UTC, END_UTC  ISO-8601 UTC timestamps such as 2026-10-13T11:00:00Z, normally the
#                         window.start_utc and window.end_utc printed by gather-gh-events.sh.
#     --include-home      Also scan sessions launched from the home directory.
#
# Sessions launched from the home directory or from temp directories are skipped by
# default: those directories collect ad-hoc and tool-launched sessions that rarely
# reflect project work, and on busy machines they outnumber real sessions.
#
# Only entries whose timestamp falls inside the window are digested, because a single
# session can run across several days.
#
# Environment:
#   CLAUDE_CONFIG_DIR  Claude Code config directory. Default: ~/.claude
#
# Output (stdout): JSON array of session digests, ordered by first activity.
#
# Requires: jq, and GNU or BSD date, find, and touch.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=SCRIPTDIR/date-utils.sh
source "${SCRIPT_DIR}/date-utils.sh"

die() {
  echo "find-sessions: $*" >&2
  exit 1
}

usage() {
  echo "Usage: find-sessions.sh START_UTC END_UTC [--include-home]" >&2
  exit 2
}

command -v jq >/dev/null 2>&1 || die "'jq' is required but not installed"

[[ $# -ge 2 && $# -le 3 ]] || usage
START_UTC="$1"
END_UTC="$2"
INCLUDE_HOME=false
if [[ $# -eq 3 ]]; then
  [[ "$3" == "--include-home" ]] || usage
  INCLUDE_HOME=true
fi

iso_re='^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$'
[[ "$START_UTC" =~ $iso_re && "$END_UTC" =~ $iso_re ]] \
  || die "timestamps must look like 2026-10-13T11:00:00Z"
[[ "$START_UTC" < "$END_UTC" ]] || die "START_UTC must be earlier than END_UTC"
START_EPOCH="$(utc_to_epoch "$START_UTC")" || die "could not parse ${START_UTC}"

PROJECTS_DIR="${CLAUDE_CONFIG_DIR:-${HOME}/.claude}/projects"
[[ -d "$PROJECTS_DIR" ]] || die "no Claude Code session logs found at ${PROJECTS_DIR}"

# Claude Code names each project directory after the launch path with every
# non-alphanumeric character replaced by '-'.
HOME_SLUG="$(printf '%s' "$HOME" | sed 's/[^A-Za-z0-9]/-/g')"

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/daily-recap.XXXXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT

# A session with activity in the window was last written at or after the window start,
# so a modification-time pre-filter keeps the scan cheap without missing anything.
REF_FILE="${WORK_DIR}/window-start"
touch -t "$(epoch_fmt "$START_EPOCH" '%Y%m%d%H%M.%S')" "$REF_FILE"

DIGESTS="${WORK_DIR}/digests.jsonl"
: >"$DIGESTS"

while IFS= read -r -d '' session_file; do
  project="$(basename "$(dirname "$session_file")")"
  case "$project" in
    -tmp-* | -private-tmp-* | -var-folders-* | -private-var-folders-*) continue ;;
  esac
  if [[ "$INCLUDE_HOME" != true && "$project" == "$HOME_SLUG" ]]; then
    continue
  fi
  session="$(basename "$session_file" .jsonl)"

  # Read line by line and skip unparsable lines, since the newest line of a live
  # session can be partially written. The session path is passed only as a label, never
  # written, so SC2094 does not apply.
  # shellcheck disable=SC2094
  jq -n -R -c \
    --arg s "$START_UTC" \
    --arg e "$END_UTC" \
    --arg project "$project" \
    --arg session "$session" \
    --arg path "$session_file" '
    def text_of:
      if type == "string" then .
      elif type == "array" then [.[] | select(.type? == "text") | .text] | join("\n")
      else "" end;

    # Compare whole seconds: session timestamps carry milliseconds, and as raw strings
    # "11:00:00.250Z" sorts before "11:00:00Z" because "." sorts before "Z".
    def secs: .[0:19];

    [ inputs | fromjson? | objects
      | select((.timestamp | type) == "string")
      | select((.timestamp | secs) >= ($s | secs) and (.timestamp | secs) < ($e | secs))
    ] as $in
    | if ($in | length) == 0 then empty else
      ([ $in[]
         | select(.type == "user" and (.isMeta | not) and (.isSidechain | not))
         | .message.content | text_of
         | select(test("\\S"))
         | select(test("^\\s*(<(command-|local-command-|system-reminder|task-notification|agent-message)|Another Claude session sent a message:)") | not)
       ]) as $prompts
      | ([ $in[] | select(.type == "assistant") | .message.content[]? | objects
           | select(.type == "tool_use") ]) as $tools
      | {
          project: $project,
          session: $session,
          path: $path,
          cwd: ([$in[] | .cwd // empty] | first // null),
          branches: ([$in[] | .gitBranch // empty | select(. != "" and . != "HEAD")] | unique),
          first_activity: ($in | map(.timestamp) | min),
          last_activity: ($in | map(.timestamp) | max),
          entries_in_window: ($in | length),
          prompt_count: ($prompts | length),
          prompts: [$prompts[0:5][] | .[0:300]],
          tool_calls: ($tools | length),
          files_edited: ([$tools[]
            | select(.name == "Edit" or .name == "Write" or .name == "MultiEdit" or .name == "NotebookEdit")
            | .input.file_path // .input.notebook_path // empty] | unique)
        }
      end
  ' <"$session_file" >>"$DIGESTS" || echo "find-sessions: skipped unreadable session ${session_file}" >&2
done < <(find "$PROJECTS_DIR" -mindepth 2 -maxdepth 2 -type f -name '*.jsonl' -newer "$REF_FILE" -print0)

jq -s 'sort_by(.first_activity)' "$DIGESTS"
