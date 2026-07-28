"""
collect_confluence.py -- Confluence activity collector (CAT6)

Collects Confluence page edits made by the user in a time window via a
two-step process:
  1. CQL search for candidate pages (contributor = accountId AND lastmodified in window)
  2. Per-page version history confirmation that the user's accountId appears
     as the version author for a version created in-window.

Confluence base URL is session.base_url + "/wiki" (not a separate env var).

All operations use Confluence v1 REST API (CQL search, content version endpoint).
Individual page version fetch failures are caught and logged; they do not
fail the whole collector.
"""

import re
import sys
import urllib.parse


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def collect_confluence(session, identity, window) -> dict:
    """Run the Confluence collector and return combined result dict.

    Args:
        session: AtlassianSession instance.
        identity: AtlassianIdentity with account_id, display_name, email.
        window: TimeWindow from lib.dates.

    Returns:
        dict with key cat6_confluence_edits.
    """
    return {"cat6_confluence_edits": _collect_cat6(session, identity, window)}


# ---------------------------------------------------------------------------
# CAT6: Confluence page edits
# ---------------------------------------------------------------------------

def _collect_cat6(session, identity, window) -> dict:
    """Collect Confluence pages edited by the user in the time window.

    CQL strategy: contributor = "<accountId>" AND type = page AND
                  lastmodified >= "<start>" AND lastmodified <= "<end>"

    Then confirms each candidate by checking version history: only pages
    where at least one version was authored by accountId within the window
    are included in items.
    """
    try:
        account_id = identity.account_id
        confluence_base = session.base_url + "/wiki"

        cql = (
            f'contributor = "{account_id}" '
            f'AND type = page '
            f'AND lastmodified >= "{window.cql_start}" '
            f'AND lastmodified <= "{window.cql_end}"'
        )
        search_url = (
            f"{confluence_base}/rest/api/search"
            f"?cql={urllib.parse.quote(cql)}"
            f"&limit=50"
            f"&expand=content.version,content.history,content.space"
        )

        # Fetch first page, then follow _links.next manually
        all_results = []
        next_url = search_url
        while next_url:
            data = session._fetch(next_url)
            results = data.get("results", [])
            all_results.extend(results)
            next_href = data.get("_links", {}).get("next")
            if next_href:
                next_url = (
                    next_href
                    if next_href.startswith("http")
                    else confluence_base + next_href
                )
            else:
                next_url = None

        confirmed_items = []

        for result in all_results:
            content = result.get("content") or {}
            page_id = content.get("id", "")
            title = content.get("title", "")
            space_key = (content.get("space") or {}).get("key", "")
            version_number = (content.get("version") or {}).get("number")

            # Build page URL
            webui = (content.get("_links") or {}).get("webui", "")
            if webui and not webui.startswith("http"):
                page_url = confluence_base + webui
            else:
                page_url = webui or f"{confluence_base}/pages/{page_id}"

            if not page_id:
                continue

            # Confirm via version history
            try:
                versions = _fetch_versions(session, confluence_base, page_id)
                confirmed = False
                edit_date = None
                for version in versions:
                    by_id = (version.get("by") or {}).get("accountId", "")
                    when = version.get("when")
                    if by_id == account_id and _in_window_str(when, window):
                        confirmed = True
                        edit_date = when
                        break  # First match is enough

                if confirmed:
                    body_excerpt = _fetch_body_excerpt(
                        session, confluence_base, page_id
                    )
                    confirmed_items.append({
                        "page_id": page_id,
                        "title": title,
                        "url": page_url,
                        "space_key": space_key,
                        "version_number": version_number,
                        "user_edit_confirmed": True,
                        "edit_date": edit_date,
                        "body_excerpt": body_excerpt,
                    })

            except Exception as exc:
                print(
                    f"[collect_confluence] Version fetch error for page {page_id}: {exc}",
                    file=sys.stderr,
                )
                # Skip this page; do not fail the whole collector
                continue

        return {
            "status": "ok",
            "count": len(confirmed_items),
            "items": confirmed_items,
            "error": None,
        }

    except Exception as exc:
        print(f"[collect_confluence] CAT6 error: {exc}", file=sys.stderr)
        return {"status": "error", "count": 0, "items": [], "error": str(exc)}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _fetch_body_excerpt(session, confluence_base: str, page_id: str) -> str | None:
    """Fetch the body of a Confluence page and return a plain-text excerpt.

    GETs /wiki/rest/api/content/{page_id}?expand=body.view, strips HTML,
    collapses whitespace, truncates to <=500 chars ("…" if truncated).
    Returns None on fetch failure or if the body is empty after stripping.
    """
    try:
        url = f"{confluence_base}/rest/api/content/{page_id}"
        data = session.get(url, params={"expand": "body.view"})
        body_html = (data.get("body") or {}).get("view", {}).get("value", "") or ""
        if not body_html:
            return None
        plain = _strip_html(body_html)
        if not plain:
            return None
        if len(plain) <= 500:
            return plain
        return plain[:500] + "…"
    except Exception as exc:
        print(
            f"[collect_confluence] body_excerpt fetch error for page {page_id}: {exc}",
            file=sys.stderr,
        )
        return None


def _strip_html(text: str) -> str:
    """Remove HTML tags, decode common HTML entities, and collapse whitespace."""
    # Remove tags
    text = re.sub(r"<[^>]+>", "", text)
    # Decode common entities
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " ")
    # Collapse runs of whitespace (including newlines) to a single space
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _fetch_versions(session, confluence_base: str, page_id: str) -> list:
    """Fetch the version history for a Confluence page.

    GET {confluence_base}/rest/api/content/{page_id}/version?limit=200

    Returns a list of version dicts, each with 'by' (user) and 'when' (date).
    """
    url = f"{confluence_base}/rest/api/content/{page_id}/version"
    data = session.get(url, params={"limit": 200})
    return data.get("results", [])


def _in_window_str(dt_str: str | None, window) -> bool:
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
