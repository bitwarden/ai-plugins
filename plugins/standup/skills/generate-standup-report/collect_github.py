"""
collect_github.py -- GitHub activity collector (authored_prs + reviews_given)

Collects two categories of GitHub activity for a user via the gh CLI's
graphql subcommand:
  - authored_prs: PRs authored by the user with in-window timeline events
  - reviews_given: Reviews and comments the user made on others' PRs

All GitHub API calls go through: gh api graphql --input -
No HTTP libraries are used for GitHub -- gh CLI handles authentication.

CRITICAL: GitHub's search 'updated:>=' filter matches the PR's last-updated
timestamp, NOT per-event activity. Client-side date filtering against
individual event timestamps is MANDATORY for all items.
"""

import json
import os
import re
import subprocess
import sys


# ---------------------------------------------------------------------------
# GraphQL query constants
# ---------------------------------------------------------------------------

AUTHORED_PRS_QUERY = """
query($queryString: String!, $cursor: String) {
  search(query: $queryString, type: ISSUE, first: 50, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes {
      ... on PullRequest {
        number
        title
        url
        body
        headRefName
        state
        isDraft
        createdAt
        updatedAt
        mergedAt
        closedAt
        reviewDecision
        repository { nameWithOwner }
        timelineItems(last: 50, itemTypes: [
          PULL_REQUEST_COMMIT,
          ISSUE_COMMENT,
          PULL_REQUEST_REVIEW,
          READY_FOR_REVIEW_EVENT
        ]) {
          nodes {
            __typename
            ... on PullRequestCommit {
              commit { committedDate }
            }
            ... on IssueComment {
              createdAt
            }
            ... on PullRequestReview {
              submittedAt
            }
            ... on ReadyForReviewEvent {
              createdAt
            }
          }
        }
      }
    }
  }
}
"""

# Note: reviews(author: ...) is not supported as a search-context filter, so
# reviewed-by uses an unfiltered reviews(first: 30) and filters client-side by
# author.login (see _collect_reviews_given).
# Inline review-thread comments are captured via comments(first:100) on each
# review node so own_comment_count includes diff-level comments.
REVIEWS_GIVEN_REVIEWED_BY_QUERY = """
query($queryString: String!, $cursor: String) {
  search(query: $queryString, type: ISSUE, first: 50, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes {
      ... on PullRequest {
        number
        title
        url
        body
        headRefName
        state
        reviewDecision
        author { login }
        mergedBy { login }
        repository { nameWithOwner }
        reviews(first: 30) {
          nodes {
            author { login }
            state
            submittedAt
            body
            comments(first: 100) {
              totalCount
              nodes {
                author { login }
                createdAt
              }
            }
          }
        }
      }
    }
  }
}
"""

REVIEWS_GIVEN_COMMENTER_QUERY = """
query($queryString: String!, $cursor: String) {
  search(query: $queryString, type: ISSUE, first: 50, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes {
      ... on PullRequest {
        number
        title
        url
        body
        headRefName
        state
        reviewDecision
        author { login }
        mergedBy { login }
        repository { nameWithOwner }
        comments(first: 50) {
          nodes {
            author { login }
            createdAt
            body
          }
        }
      }
    }
  }
}
"""


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def collect_github(github_user: str, window) -> dict:
    """Run both GitHub collectors and return combined result dict.

    Args:
        github_user: GitHub login (e.g. "octocat").
        window: TimeWindow from lib.dates.

    Returns:
        dict with keys authored_prs and reviews_given.
    """
    # Build a Jira session for linked-ticket resolution if token is available.
    # Failure to construct the session must NOT crash GitHub collection.
    jira_session = _maybe_build_jira_session()

    result = {}
    result.update(_collect_authored_prs(github_user, window, jira_session))
    result.update(_collect_reviews_given(github_user, window, jira_session))
    return result


def _maybe_build_jira_session():
    """Attempt to build an AtlassianSession for linked-ticket resolution.

    Returns an AtlassianSession on success, None if JIRA_API_TOKEN is absent
    or construction fails. Never raises.
    """
    token = os.environ.get("JIRA_API_TOKEN")
    if not token:
        return None
    try:
        # Inline import to avoid circular dependency: collect_github is imported
        # by gather.py which also imports lib.atlassian separately.
        _SKILL_ROOT = os.path.dirname(os.path.abspath(__file__))
        if _SKILL_ROOT not in sys.path:
            sys.path.insert(0, _SKILL_ROOT)
        from lib.atlassian import AtlassianSession  # noqa: E402
        return AtlassianSession()
    except Exception as exc:
        print(f"[collect_github] Jira session init failed (linked_ticket disabled): {exc}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# authored_prs: Authored PRs with in-window timeline events
# ---------------------------------------------------------------------------

def _collect_authored_prs(github_user: str, window, jira_session) -> dict:
    """Collect PRs authored by the user with in-window timeline activity."""
    try:
        query_string = f"author:{github_user} type:pr updated:>={window.gh_floor}"
        variables = {"queryString": query_string}
        nodes = _paginate_search(AUTHORED_PRS_QUERY, variables)

        # Cache resolved ticket statuses within this run to avoid duplicate GETs.
        ticket_cache = {}

        items = []
        for node in nodes:
            if not node or node.get("__typename") == "Issue":
                continue

            number = node.get("number")
            title = node.get("title", "")
            url = node.get("url", "")
            body_raw = node.get("body") or ""
            branch = node.get("headRefName") or ""
            state = node.get("state", "")
            is_draft = node.get("isDraft", False)
            created_at = node.get("createdAt")
            merged_at = node.get("mergedAt")
            closed_at = node.get("closedAt")
            review_decision = node.get("reviewDecision")
            repo = (node.get("repository") or {}).get("nameWithOwner", "")

            body_excerpt = _make_body_excerpt(body_raw)
            linked_ticket = _extract_linked_ticket(branch, body_raw, jira_session, ticket_cache)

            # Collect in-window activity events
            timeline_nodes = (node.get("timelineItems") or {}).get("nodes", [])
            activity_in_window = []
            for event in timeline_nodes:
                if not event:
                    continue
                typename = event.get("__typename", "")
                event_date = None
                detail = ""

                if typename == "PullRequestCommit":
                    event_date = (event.get("commit") or {}).get("committedDate")
                    detail = "commit"
                elif typename == "IssueComment":
                    event_date = event.get("createdAt")
                    detail = "comment"
                elif typename == "PullRequestReview":
                    event_date = event.get("submittedAt")
                    detail = "review"
                elif typename == "ReadyForReviewEvent":
                    event_date = event.get("createdAt")
                    detail = "ready_for_review"

                if event_date and _in_window(event_date, window):
                    activity_in_window.append({
                        "type": typename,
                        "date": event_date,
                        "detail": detail,
                    })

            # Include PR only if it has at least one in-window event
            if not activity_in_window:
                continue

            items.append({
                "number": number,
                "title": title,
                "url": url,
                "branch": branch,
                "body_excerpt": body_excerpt,
                "linked_ticket": linked_ticket,
                "repo": repo,
                "state": state,
                "is_draft": is_draft,
                "review_decision": review_decision,
                "created_at": created_at,
                "merged_at": merged_at,
                "closed_at": closed_at,
                "activity_in_window": activity_in_window,
                "activity_count_in_window": len(activity_in_window),
                "involvement_tier": "AUTHORED",
            })

        return {"authored_prs": {"status": "ok", "count": len(items), "items": items, "error": None}}

    except Exception as exc:
        print(f"[collect_github] authored_prs error: {exc}", file=sys.stderr)
        return {"authored_prs": {"status": "error", "count": 0, "items": [], "error": str(exc)}}


# ---------------------------------------------------------------------------
# reviews_given: Reviews and comments on others' PRs
# ---------------------------------------------------------------------------

def _collect_reviews_given(github_user: str, window, jira_session) -> dict:
    """Collect reviews and comments the user made on others' PRs.

    Pass A: reviewed-by:{user} type:pr -author:{user} updated:>={floor}
      -> collect reviews where author.login == github_user AND submittedAt in-window

    Pass B: commenter:{user} type:pr -author:{user} updated:>={floor}
      -> collect comments where author.login == github_user AND createdAt in-window

    De-duplicates by PR URL using a dict keyed by url.
    """
    try:
        floor = window.gh_floor
        # Pass A: reviewed-by
        reviewed_query = f"reviewed-by:{github_user} type:pr -author:{github_user} updated:>={floor}"
        reviewed_nodes = _paginate_search(
            REVIEWS_GIVEN_REVIEWED_BY_QUERY, {"queryString": reviewed_query}
        )

        # Pass B: commenter
        commenter_query = f"commenter:{github_user} type:pr -author:{github_user} updated:>={floor}"
        commenter_nodes = _paginate_search(
            REVIEWS_GIVEN_COMMENTER_QUERY, {"queryString": commenter_query}
        )

        # Cache resolved ticket statuses within this run.
        ticket_cache = {}

        # Combine into dict keyed by PR URL for deduplication
        pr_map = {}

        for node in reviewed_nodes:
            if not node:
                continue
            url = node.get("url", "")
            if not url:
                continue
            entry = _ensure_reviews_given_entry(pr_map, node, jira_session, ticket_cache)

            reviews = (node.get("reviews") or {}).get("nodes", [])
            for review in reviews:
                if not review:
                    continue
                author_login = (review.get("author") or {}).get("login", "")
                submitted_at = review.get("submittedAt")
                if author_login == github_user and _in_window(submitted_at, window):
                    # Capture inline review-thread comments on this review node
                    review_inline_comments = (review.get("comments") or {}).get("nodes", [])
                    inline_total_count = (review.get("comments") or {}).get("totalCount", 0)
                    inline_capped = inline_total_count > len(review_inline_comments)
                    entry["reviews_by_user"].append({
                        "state": review.get("state", ""),
                        "submitted_at": submitted_at,
                        "body": review.get("body", ""),
                        "_inline_comment_nodes": review_inline_comments,
                        "_inline_comment_capped": inline_capped,
                    })

        for node in commenter_nodes:
            if not node:
                continue
            url = node.get("url", "")
            if not url:
                continue
            entry = _ensure_reviews_given_entry(pr_map, node, jira_session, ticket_cache)

            comments = (node.get("comments") or {}).get("nodes", [])
            for comment in comments:
                if not comment:
                    continue
                author_login = (comment.get("author") or {}).get("login", "")
                created_at = comment.get("createdAt")
                if author_login == github_user and _in_window(created_at, window):
                    entry["comments_by_user"].append({
                        "created_at": created_at,
                        "body": comment.get("body", ""),
                    })

        # Filter to PRs where the user actually has in-window activity,
        # then compute own_comment_count per PR.
        items = []
        for url, entry in pr_map.items():
            if not (entry["reviews_by_user"] or entry["comments_by_user"]):
                continue
            entry = _compute_own_comment_count(entry, github_user)
            # Exclude bare approvals: only surface a review if the user left at
            # least one substantive comment OR was the one who merged the PR.
            user_merged = entry.get("merged_by_login", "") == github_user
            if entry["own_comment_count"] == 0 and not user_merged:
                continue
            for r in entry["reviews_by_user"]:
                r.pop("_inline_comment_nodes", None)
                r.pop("_inline_comment_capped", None)
            entry["review_states"] = [r["state"] for r in entry["reviews_by_user"] if r.get("state")]
            entry["user_merged_pr"] = user_merged
            entry["involvement_tier"] = _compute_review_involvement_tier(entry)
            items.append(entry)

        return {"reviews_given": {"status": "ok", "count": len(items), "items": items, "error": None}}

    except Exception as exc:
        print(f"[collect_github] reviews_given error: {exc}", file=sys.stderr)
        return {"reviews_given": {"status": "error", "count": 0, "items": [], "error": str(exc)}}


def _ensure_reviews_given_entry(pr_map: dict, node: dict, jira_session, ticket_cache: dict) -> dict:
    """Get or create a reviews_given accumulator entry in pr_map for the given PR node."""
    url = node.get("url", "")
    if url not in pr_map:
        body_raw = node.get("body") or ""
        branch = node.get("headRefName") or ""
        body_excerpt = _make_body_excerpt(body_raw)
        linked_ticket = _extract_linked_ticket(branch, body_raw, jira_session, ticket_cache)
        pr_map[url] = {
            "pr_number": node.get("number"),
            "pr_title": node.get("title", ""),
            "url": url,
            "pr_url": url,
            "branch": branch,
            "body_excerpt": body_excerpt,
            "linked_ticket": linked_ticket,
            "repo": (node.get("repository") or {}).get("nameWithOwner", ""),
            "pr_author": (node.get("author") or {}).get("login", ""),
            "merged_by_login": (node.get("mergedBy") or {}).get("login", ""),
            "pr_state": node.get("state", ""),
            "pr_review_decision": node.get("reviewDecision"),
            "reviews_by_user": [],
            "comments_by_user": [],
        }
    return pr_map[url]


def _compute_own_comment_count(entry: dict, github_user: str) -> dict:
    """Compute own_comment_count and own_comment_count_capped for a reviews_given entry.

    own_comment_count = (review submissions by github_user with non-empty body)
                      + (inline review-thread comment nodes authored by github_user)
                      + (conversation comments_by_user count)

    own_comment_count_capped is True if any inline comment page hit its
    first:100 limit (meaning the count is a floor, not an exact total).

    Mutates and returns the entry dict.
    """
    count = 0
    capped = False

    # Count review submissions with a non-empty body
    for review in entry.get("reviews_by_user", []):
        if (review.get("body") or "").strip():
            count += 1
        # Count inline review-thread comments authored by github_user
        for inline_node in review.get("_inline_comment_nodes", []):
            node_author = (inline_node.get("author") or {}).get("login", "")
            if node_author == github_user:
                count += 1
        if review.get("_inline_comment_capped"):
            capped = True

    # Count conversation-tab comments (already filtered by github_user + in-window)
    count += len(entry.get("comments_by_user", []))

    entry["own_comment_count"] = count
    if capped:
        entry["own_comment_count_capped"] = True

    return entry


def _compute_review_involvement_tier(entry: dict) -> str:
    """Compute involvement tier label for a reviews_given entry.

    Returns one of: SUBSTANTIVE_REVIEW, LIGHT_REVIEW.
    Consistent with the own_comment_count >= 8 threshold in the synthesize skill.
    """
    comment_count = entry.get("own_comment_count", 0)
    review_states = entry.get("review_states", [])
    user_merged = entry.get("user_merged_pr", False)

    if comment_count >= 8:
        return "SUBSTANTIVE_REVIEW"
    if "CHANGES_REQUESTED" in review_states:
        return "SUBSTANTIVE_REVIEW"
    if user_merged and comment_count >= 2:
        return "SUBSTANTIVE_REVIEW"
    return "LIGHT_REVIEW"


# ---------------------------------------------------------------------------
# PR enrichment helpers
# ---------------------------------------------------------------------------

_TICKET_KEY_RE = re.compile(r"[A-Z]{2,}-\d+", re.IGNORECASE)


def _make_body_excerpt(body: str) -> str | None:
    """Return a plain-text excerpt of a PR body, max 500 chars.

    Returns None (not empty string) when the body is absent/empty, so the
    synthesis layer can distinguish 'no body' from 'body that is whitespace'.
    """
    if not body or not body.strip():
        return None
    # Collapse whitespace runs (newlines, tabs, multiple spaces → single space)
    text = re.sub(r"\s+", " ", body).strip()
    if len(text) <= 500:
        return text
    return text[:500] + "…"


def _extract_ticket_key(branch: str, body: str) -> str | None:
    """Extract and normalise the primary Jira ticket key from branch or body.

    Priority: branch first (e.g. 'pm-40845-remove-...' → 'PM-40845'), then
    body text (any '[A-Z]{2,}-\\d+' match). Normalises to uppercase.
    Returns None if no key is found.
    """
    # 1. Branch name: regex over the branch string (case-insensitive match)
    if branch:
        m = _TICKET_KEY_RE.search(branch)
        if m:
            return m.group(0).upper()

    # 2. PR body text
    if body:
        m = _TICKET_KEY_RE.search(body)
        if m:
            return m.group(0).upper()

    return None


def _extract_team(custom_field_value) -> str:
    """Extract team name from Jira customfield_10001 (Team field).

    Handles None, dict ({"value": "..."}), or list of dicts.
    Returns the team name string, or empty string if not set.
    """
    if custom_field_value is None:
        return ""
    if isinstance(custom_field_value, dict):
        return custom_field_value.get("value", "")
    if isinstance(custom_field_value, list) and len(custom_field_value) > 0:
        return custom_field_value[0].get("value", "")
    return ""


def _resolve_ticket_details(key: str, jira_session, cache: dict) -> dict:
    """GET /rest/api/3/issue/{key}?fields=status,customfield_10001 and return {"status": ..., "team": ...}.

    Caches results in `cache` dict to avoid duplicate requests within a run.
    Returns {"status": None, "team": ""} on any error.
    """
    if key in cache:
        return cache[key]
    try:
        data = jira_session.get(
            f"/rest/api/3/issue/{key}",
            params={"fields": "status,customfield_10001"},
        )
        fields = data.get("fields") or {}
        status_name = (fields.get("status") or {}).get("name")
        team = _extract_team(fields.get("customfield_10001"))
        result = {"status": status_name, "team": team}
        cache[key] = result
        return result
    except Exception as exc:
        print(f"[collect_github] ticket detail resolution failed for {key}: {exc}", file=sys.stderr)
        result = {"status": None, "team": ""}
        cache[key] = result
        return result


def _extract_linked_ticket(branch: str, body: str, jira_session, cache: dict) -> dict | None:
    """Build the linked_ticket object for a PR item.

    Returns None if no ticket key can be found.
    Returns {"key": "PM-####", "status": "<name>"|null, "team": "<name>"|"", "url": "...", "comments": [...]}
    where status is null on resolution errors, team is "" when unset or on error,
    and comments is [] on fetch failure.
    comments_truncated: True is added when the ticket has >50 comments (absent otherwise).
    """
    key = _extract_ticket_key(branch, body)
    if not key:
        return None

    if jira_session is not None:
        base_url = jira_session.base_url
    else:
        base_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
        if not base_url:
            return None

    url = f"{base_url}/browse/{key}"

    status = None
    team = ""
    if jira_session is not None:
        details = _resolve_ticket_details(key, jira_session, cache)
        status = details["status"]
        team = details["team"]

    linked = {"key": key, "status": status, "team": team, "url": url}

    # Attach full comment thread using the shared module-level cache from
    # collect_jira (deferred import to avoid circular dependency risk).
    if jira_session is not None:
        try:
            from collect_jira import attach_comments  # noqa: E402
            attach_comments(jira_session, key, linked)
        except Exception as exc:
            print(
                f"[collect_github] linked_ticket comment fetch failed for {key}: {exc}",
                file=sys.stderr,
            )
            linked["comments"] = []

    return linked


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _gh_graphql(query: str, variables: dict) -> dict:
    """Execute a GitHub GraphQL query via gh CLI and return the response data.

    Uses: gh api graphql --input -
    Passes {query, variables} JSON to stdin.

    Raises RuntimeError if gh exits non-zero, response contains errors, or the
    subprocess exceeds GH_GRAPHQL_TIMEOUT_SECS (prevents indefinite hang).
    """
    payload = json.dumps({"query": query, "variables": variables}).encode()
    try:
        result = subprocess.run(
            ["gh", "api", "graphql", "--input", "-"],
            input=payload,
            capture_output=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"gh api graphql timed out after 60s: {exc}"
        )
    if result.returncode != 0:
        stderr_text = result.stderr.decode(errors="replace")
        raise RuntimeError(f"gh api graphql failed (exit {result.returncode}): {stderr_text}")

    response = json.loads(result.stdout.decode())
    if "errors" in response:
        raise RuntimeError(f"GraphQL errors: {json.dumps(response['errors'])}")

    return response.get("data", {})


def _paginate_search(query: str, variables: dict, page_key: str = "search") -> list:
    """Paginate a GitHub GraphQL search query and accumulate all nodes.

    Follows pageInfo.hasNextPage / endCursor until exhausted.
    """
    nodes = []
    cursor = None

    while True:
        vars_with_cursor = dict(variables)
        if cursor:
            vars_with_cursor["cursor"] = cursor

        data = _gh_graphql(query, vars_with_cursor)
        search = data.get(page_key, {})
        page_nodes = search.get("nodes", [])
        nodes.extend(page_nodes)

        page_info = search.get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        if not cursor:
            break

    return nodes


def _in_window(dt_str: str | None, window) -> bool:
    """Check whether an ISO-8601 datetime string falls in the window.

    Inline version (avoids cross-module import). Handles Z-suffix and
    +HH:MM offset strings. Returns False on None or parse failure.
    """
    if not dt_str:
        return False
    try:
        from datetime import datetime, timezone
        normalized = dt_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return window.start <= dt <= window.end
    except (ValueError, TypeError):
        return False
