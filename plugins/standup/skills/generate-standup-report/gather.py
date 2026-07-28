"""
gather.py -- Single entry point for generate-standup-report skill

Parses CLI arguments, resolves Atlassian identity, runs all collectors,
and emits a combined JSON document conforming to the Combined JSON Output Schema.

Usage:
    python3 gather.py --timeline "last 1 week" \\
                      --jira-user "Your Display Name" \\
                      --github-user your-github-login \\
                      [--out /path/to/output.json] \\
                      [--dry-run]

--dry-run makes ZERO network calls. JIRA_API_TOKEN, JIRA_EMAIL, and
JIRA_BASE_URL are NOT required with --dry-run or --help.
--help exits 0 without any environment variables set.

Environment variables:
    JIRA_API_TOKEN  (required for live mode; not needed for --dry-run/--help)
    JIRA_EMAIL      (required for live mode; no default -- must be set explicitly)
    JIRA_BASE_URL   (required for live mode; no default -- must be set explicitly)
    STANDUP_TZ      (optional; timezone for date calculations; default: UTC)

Categories emitted:
    cat1_authored_prs     -- GitHub PRs authored by user with in-window events
    cat2_reviews_given    -- GitHub reviews/comments on others' PRs (+ own_comment_count)
    cat3_jira_done        -- Jira tickets resolved in time window
    cat4_jira_created     -- Jira tickets created by user in time window
    cat5_jira_comments    -- Jira comments by user in time window
    cat6_confluence_edits -- Confluence pages edited by user in time window
    cat7_jira_grooming    -- Jira field edits via Activity Streams in time window
    cat8_in_progress      -- CURRENT SNAPSHOT: all in-progress tickets (NOT windowed)
    cat9_blocked          -- CURRENT SNAPSHOT: all blocked tickets (NOT windowed)
"""

import argparse
import json
import os
import sys

# sys.path insert MUST come before any lib.* imports
_SKILL_ROOT = os.path.dirname(os.path.abspath(__file__))
if _SKILL_ROOT not in sys.path:
    sys.path.insert(0, _SKILL_ROOT)

# dates.py has no network dependencies; safe to import at module level
from lib.dates import parse_timeline  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Gather GitHub and Atlassian activity for a user in a time window "
            "and emit a combined JSON document."
        )
    )
    parser.add_argument(
        "--timeline",
        default="last 1 week",
        help=(
            "Time window for activity. "
            "Relative: 'last 1 day', 'last 1 week', 'last 2 weeks'. "
            "Absolute: 'YYYY-MM-DD - YYYY-MM-DD'. "
            "(default: 'last 1 week')"
        ),
    )
    parser.add_argument(
        "--jira-user",
        required=True,
        help="Atlassian display name or email to search for. (required; no default)",
    )
    parser.add_argument(
        "--github-user",
        required=True,
        help="GitHub login to search for. (required; no default)",
    )
    parser.add_argument(
        "--out",
        default=None,
        metavar="FILE",
        help="Write output JSON to FILE instead of stdout.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Emit a dry-run JSON skeleton without making any network calls. "
            "JIRA_API_TOKEN is not required in dry-run mode."
        ),
    )
    args = parser.parse_args()

    # Parse timeline (no network calls)
    try:
        window = parse_timeline(args.timeline)
    except ValueError as exc:
        print(f"Error: invalid --timeline value: {exc}", file=sys.stderr)
        sys.exit(1)

    # Dry-run short-circuits here -- zero network calls
    if args.dry_run:
        output = _dry_run_output(args, window)
        _emit(output, args.out)
        return

    # --- Live mode: JIRA_API_TOKEN required from this point ---
    if not os.environ.get("JIRA_API_TOKEN"):
        print(
            "Error: JIRA_API_TOKEN environment variable is required for live mode. "
            "Use --dry-run to skip API calls.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Deferred imports: these require JIRA_API_TOKEN or make network calls
    from lib.atlassian import AtlassianSession  # noqa: E402
    from lib.identity import resolve_atlassian_identity, IdentityResolutionError  # noqa: E402
    from collect_jira import collect_jira  # noqa: E402
    from collect_confluence import collect_confluence  # noqa: E402
    from collect_github import collect_github  # noqa: E402

    session = AtlassianSession()

    try:
        identity = resolve_atlassian_identity(session, args.jira_user)
    except IdentityResolutionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    # Run all collectors -- each degrades gracefully on error.
    # Wrap each top-level call defensively so a catastrophic failure in one
    # collector (e.g. an unexpected exception escaping its own try/except)
    # cannot prevent the remaining collectors from running.
    categories = {}

    try:
        categories.update(collect_jira(session, identity, window))
    except Exception as exc:
        print(f"[gather] collect_jira top-level error (degraded): {exc}", file=sys.stderr)
        categories.update({
            "cat3_jira_done":     {"status": "error", "count": 0, "items": [], "error": str(exc)},
            "cat4_jira_created":  {"status": "error", "count": 0, "items": [], "error": str(exc)},
            "cat5_jira_comments": {"status": "error", "count": 0, "items": [], "error": str(exc)},
            "cat7_jira_grooming": {
                "status": "error", "count": 0, "items": [],
                "summary": {"issues_touched": 0, "field_counts": {}},
                "error": str(exc),
            },
            "cat8_in_progress": {"status": "error", "count": 0, "items": [], "error": str(exc)},
            "cat9_blocked":     {"status": "error", "count": 0, "items": [], "error": str(exc)},
        })

    try:
        categories.update(collect_confluence(session, identity, window))
    except Exception as exc:
        print(f"[gather] collect_confluence top-level error (degraded): {exc}", file=sys.stderr)
        categories.update({
            "cat6_confluence_edits": {"status": "error", "count": 0, "items": [], "error": str(exc)},
        })

    try:
        categories.update(collect_github(args.github_user, window))
    except Exception as exc:
        print(f"[gather] collect_github top-level error (degraded): {exc}", file=sys.stderr)
        categories.update({
            "cat1_authored_prs":  {"status": "error", "count": 0, "items": [], "error": str(exc)},
            "cat2_reviews_given": {"status": "error", "count": 0, "items": [], "error": str(exc)},
        })

    # Build output schema
    from datetime import datetime, timezone  # noqa: E402
    now_iso = datetime.now(tz=timezone.utc).isoformat()

    output = {
        "schema_version": "1.0",
        "generated_at": now_iso,
        "dry_run": False,
        "window": {
            "start": window.iso_start,
            "end": window.iso_end,
            "input_timeline": window.input_timeline,
        },
        "identity": {
            "atlassian": {
                "account_id": identity.account_id,
                "display_name": identity.display_name,
                "email": identity.email,
                "input_name": args.jira_user,
            },
            "github": {
                "login": args.github_user,
                "input_login": args.github_user,
            },
        },
        "categories": categories,
    }

    _emit(output, args.out)


def _dry_run_output(args, window) -> dict:
    """Build a dry-run skeleton that matches the full schema shape."""
    from datetime import datetime, timezone
    now_iso = datetime.now(tz=timezone.utc).isoformat()

    return {
        "schema_version": "1.0",
        "generated_at": now_iso,
        "dry_run": True,
        "window": {
            "start": window.iso_start,
            "end": window.iso_end,
            "input_timeline": window.input_timeline,
        },
        "identity": {
            "atlassian": {
                "account_id": "DRY_RUN",
                "display_name": args.jira_user,
                "email": "",
                "input_name": args.jira_user,
            },
            "github": {
                "login": args.github_user,
                "input_login": args.github_user,
            },
        },
        "categories": {},
    }


def _emit(output: dict, out_file: str | None) -> None:
    """Serialize output to JSON and write to out_file or stdout."""
    text = json.dumps(output, indent=2, default=str)
    if out_file:
        with open(out_file, "w") as fh:
            fh.write(text)
            fh.write("\n")
        print(f"Output written to {out_file}", file=sys.stderr)
    else:
        print(text)


if __name__ == "__main__":
    main()
