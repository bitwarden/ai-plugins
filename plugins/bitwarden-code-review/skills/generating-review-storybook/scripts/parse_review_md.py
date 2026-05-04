#!/usr/bin/env python3
"""Extract verdict, finding counts, and finding items from Bitwarden review markdown.

Reads one or more review summary files (typically ``review-summary.md`` from
``bitwarden-code-review:code-review-local``) and emits the storybook verdict
shape: a JSON map of
``{key: {verdict, verdict_label, findings: {counts..., items: [...]}}}``.

The mapping from review file → stack key is supplied as ``key=path`` pairs.

Examples:
    python scripts/parse_review_md.py 2573=reviews/pr-2573.md 2576=reviews/pr-2576.md
    python scripts/parse_review_md.py --output verdicts.json a1b2c3=reviews/commit-a1b2c3.md

Verdict rules (in order):
    1. "**Overall Assessment:** APPROVE"          → approve
    2. "**Overall Assessment:** REQUEST CHANGES"  → block
    3. APPROVE present but ❌/⚠️ findings exist   → approve-fix
    4. Otherwise                                  → pending

Severity-emoji mapping covers ❌ CRITICAL / ⚠️ IMPORTANT / ♻️ DEBT / 🎨 SUGGESTED / ❓ QUESTION.

The output ``items`` list preserves the message text after the emoji, the
backtick-wrapped ``file:line`` location from the next sub-bullet, and any
remaining sub-bullet text as ``suggestion``.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Severity emoji → finding key. The first emoji in each list is the canonical
# form posted by the bitwarden-code-review skill; the second handles legacy
# variation-selector forms.
SEVERITY_PATTERNS: dict[str, list[str]] = {
    "critical": ["❌"],
    "important": ["⚠️", "⚠"],
    "debt": ["♻️", "♻"],
    "suggested": ["🎨"],
    "question": ["❓"],
}
EMOJI_DISPLAY = {
    "critical": "❌",
    "important": "⚠️",
    "debt": "♻️",
    "suggested": "🎨",
    "question": "❓",
}

VERDICT_LABELS = {
    "approve": "Approved",
    "approve-fix": "Approve with follow-up",
    "block": "Blocked",
    "pending": "Pending review",
}

LOCATION_RE = re.compile(r"`([^`]+)`")


def die(msg: str, code: int = 1) -> None:
    print(f"parse_review_md.py: {msg}", file=sys.stderr)
    sys.exit(code)


def detect_severity(body: str) -> tuple[str, str] | None:
    """Return (severity, message) if body starts with a severity emoji, else None."""
    for sev, emojis in SEVERITY_PATTERNS.items():
        for emoji in emojis:
            if body.startswith(emoji):
                rest = body[len(emoji):].lstrip()
                if rest.startswith(":"):
                    rest = rest[1:].lstrip()
                return sev, rest.strip()
    return None


def extract_findings(text: str) -> list[dict[str, str]]:
    """Walk markdown bullets and pull out (severity, message, location, suggestion)."""
    items: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw_line in text.splitlines():
        stripped = raw_line.lstrip()
        if not stripped.startswith("-"):
            continue
        indent = len(raw_line) - len(stripped)
        body = stripped[1:].lstrip()
        severity_match = detect_severity(body) if indent == 0 else None

        if severity_match is not None:
            if current is not None:
                items.append(current)
            severity, message = severity_match
            current = {
                "severity": severity,
                "emoji": EMOJI_DISPLAY[severity],
                "message": message,
                "location": "",
                "suggestion": "",
            }
            continue

        if current is None or indent < 2:
            continue

        # Sub-bullet: first one with a backtick block is the location, anything
        # else feeds into ``suggestion`` as a single string.
        loc_match = LOCATION_RE.search(body)
        if loc_match and not current["location"]:
            current["location"] = loc_match.group(1).strip()
            remainder = (body[: loc_match.start()] + body[loc_match.end():]).strip(" -")
            if remainder and not current["suggestion"]:
                current["suggestion"] = remainder
            continue

        if not current["suggestion"]:
            current["suggestion"] = body.strip()
        else:
            current["suggestion"] = f"{current['suggestion']} {body.strip()}".strip()

    if current is not None:
        items.append(current)
    return items


def count_by_severity(items: list[dict[str, str]]) -> dict[str, int]:
    counts = {sev: 0 for sev in SEVERITY_PATTERNS}
    for item in items:
        counts[item["severity"]] += 1
    return counts


OVERALL_RE = re.compile(
    r"\*\*Overall Assessment:\*\*\s*(APPROVE|REQUEST CHANGES|BLOCK|PENDING)",
    re.IGNORECASE,
)


def derive_verdict(text: str, counts: dict[str, int]) -> str:
    match = OVERALL_RE.search(text)
    if not match:
        return "pending"
    raw = match.group(1).upper()
    if raw in {"REQUEST CHANGES", "BLOCK"}:
        return "block"
    if raw == "APPROVE":
        if counts["critical"] or counts["important"]:
            return "approve-fix"
        return "approve"
    return "pending"


def parse_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        die(f"review file not found: {path}")
    text = path.read_text(encoding="utf-8")
    items = extract_findings(text)
    counts = count_by_severity(items)
    verdict = derive_verdict(text, counts)
    findings: dict[str, Any] = {**counts, "items": items}
    return {
        "verdict": verdict,
        "verdict_label": VERDICT_LABELS[verdict],
        "findings": findings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse Bitwarden review markdown into storybook verdicts.")
    parser.add_argument(
        "pairs",
        nargs="+",
        help="key=path pairs (e.g. 2573=reviews/pr-2573.md)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the JSON map to this file. Defaults to stdout.",
    )
    args = parser.parse_args()

    out: dict[str, dict[str, Any]] = {}
    for pair in args.pairs:
        if "=" not in pair:
            die(f"expected key=path, got: {pair}")
        key, _, raw_path = pair.partition("=")
        key = key.strip()
        if not key:
            die(f"empty key in pair: {pair}")
        out[key] = parse_file(Path(raw_path))

    payload = json.dumps(out, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
