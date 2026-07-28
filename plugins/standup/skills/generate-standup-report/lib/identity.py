"""
identity.py -- Atlassian accountId resolver

Resolves an Atlassian display name or email address to an accountId via the
Jira REST API. Never hardcodes account IDs -- always resolves at runtime.

Resolution order:
  1. GET /rest/api/3/myself -- if displayName or emailAddress matches, use it
  2. GET /rest/api/3/user/search?query=<input> -- exact displayName match
  3. GET /rest/api/3/user/search?query=<first word> -- broader fallback
  4. Raise IdentityResolutionError

The lib.atlassian import is deferred to the __main__ block so that
IdentityResolutionError and AtlassianIdentity can be imported by other modules
without JIRA_API_TOKEN being present in the environment.
"""

import json
import sys
from dataclasses import dataclass


class IdentityResolutionError(Exception):
    """Raised when an Atlassian user cannot be resolved from a name or email."""

    def __init__(self, name_or_email: str):
        self.name_or_email = name_or_email
        super().__init__(
            f"Could not resolve Atlassian identity for: {name_or_email!r}"
        )


@dataclass
class AtlassianIdentity:
    """Resolved Atlassian user identity."""

    account_id: str
    display_name: str
    email: str


def resolve_atlassian_identity(session, name_or_email: str) -> AtlassianIdentity:
    """Resolve a display name or email to an Atlassian accountId.

    Steps through up to 4 resolution strategies, logging progress to stderr
    at each step. Raises IdentityResolutionError if no match is found.

    Args:
        session: An AtlassianSession instance.
        name_or_email: Display name (e.g. "Ada Lovelace") or email.
    """
    normalized_target = name_or_email.strip().lower()

    # Step 1: GET /myself
    try:
        print(f"[identity] Step 1: checking /myself for {name_or_email!r}...", file=sys.stderr)
        myself = session.get("/rest/api/3/myself")
        if (
            myself.get("displayName", "").lower() == normalized_target
            or myself.get("emailAddress", "").lower() == normalized_target
        ):
            print(
                f"[identity] Matched via /myself: {myself.get('displayName')} ({myself.get('accountId')})",
                file=sys.stderr,
            )
            return AtlassianIdentity(
                account_id=myself["accountId"],
                display_name=myself.get("displayName", ""),
                email=myself.get("emailAddress", ""),
            )
        print(
            f"[identity] /myself returned {myself.get('displayName')!r} -- no match",
            file=sys.stderr,
        )
    except Exception as exc:
        print(f"[identity] Step 1 failed: {exc}", file=sys.stderr)

    # Step 2: user/search with full name_or_email
    try:
        print(f"[identity] Step 2: searching /user/search?query={name_or_email!r}...", file=sys.stderr)
        candidates = _user_search(session, name_or_email)
        match = _pick_match(candidates, normalized_target)
        if match:
            print(f"[identity] Step 2 match: {match.display_name} ({match.account_id})", file=sys.stderr)
            return match
        print(f"[identity] Step 2: {len(candidates)} candidate(s), no exact match", file=sys.stderr)
    except Exception as exc:
        print(f"[identity] Step 2 failed: {exc}", file=sys.stderr)

    # Step 3: broader fallback -- first word of name
    first_word = name_or_email.strip().split()[0] if name_or_email.strip() else name_or_email
    if first_word != name_or_email:
        try:
            print(f"[identity] Step 3: broader search with first word {first_word!r}...", file=sys.stderr)
            candidates = _user_search(session, first_word)
            match = _pick_match(candidates, normalized_target)
            if match:
                print(f"[identity] Step 3 match: {match.display_name} ({match.account_id})", file=sys.stderr)
                return match
            print(f"[identity] Step 3: {len(candidates)} candidate(s), no exact match", file=sys.stderr)
        except Exception as exc:
            print(f"[identity] Step 3 failed: {exc}", file=sys.stderr)

    raise IdentityResolutionError(name_or_email)


def _user_search(session, query: str) -> list:
    """Search for Atlassian users matching a query string.

    Returns a list of raw user dicts from the API. Exceptions are caught
    and re-raised so callers can decide how to handle them.
    """
    return session.get("/rest/api/3/user/search", params={"query": query})


def _pick_match(candidates: list, normalized_target: str) -> "AtlassianIdentity | None":
    """Pick the first candidate whose displayName matches the normalized target.

    Returns None if no match is found.
    """
    for candidate in candidates:
        display = candidate.get("displayName", "")
        email = candidate.get("emailAddress", "")
        if (
            display.lower() == normalized_target
            or email.lower() == normalized_target
        ):
            return AtlassianIdentity(
                account_id=candidate["accountId"],
                display_name=display,
                email=email,
            )
    return None


# ---------------------------------------------------------------------------
# __main__ entry point (deferred lib.atlassian import)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    # Deferred import: lib.atlassian requires JIRA_API_TOKEN
    import os
    import sys as _sys

    _skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _skill_root not in _sys.path:
        _sys.path.insert(0, _skill_root)

    from lib.atlassian import AtlassianSession  # noqa: E402

    parser = argparse.ArgumentParser(
        description="Resolve an Atlassian display name or email to accountId."
    )
    parser.add_argument("name_or_email", help="Display name or email to resolve")
    args = parser.parse_args()

    session = AtlassianSession()
    try:
        identity = resolve_atlassian_identity(session, args.name_or_email)
        print(
            json.dumps(
                {
                    "account_id": identity.account_id,
                    "display_name": identity.display_name,
                    "email": identity.email,
                },
                indent=2,
            )
        )
    except IdentityResolutionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
