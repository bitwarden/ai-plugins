#!/usr/bin/env python3
"""Generate a code-review storybook from a JSON config.

Reads the bundled template under ../assets/template/, performs
sentinel-bracketed block substitution and small token replacement, and
writes the rendered storybook to the output directory.

Usage:
    python scripts/scaffold.py --config /tmp/storybook.json --output /tmp/out

The config schema is documented in references/data-schema.md.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import sys
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "template"

VALID_VERDICTS = {"approve", "approve-fix", "block", "pending"}
VERDICT_LABELS = {
    "approve": "Approved",
    "approve-fix": "Approve with follow-up",
    "block": "Blocked",
    "pending": "Pending review",
}
VERDICT_BADGE_CLASS = {
    "approve": "badge-approve",
    "approve-fix": "badge-approve-fix",
    "block": "badge-block",
    "pending": "badge-pending",
}


def die(msg: str, code: int = 1) -> None:
    print(f"scaffold.py: {msg}", file=sys.stderr)
    sys.exit(code)


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    s = _SLUG_RE.sub("-", text.lower()).strip("-")
    return s or "stack"


def default_output_root() -> Path:
    base = os.environ.get("CLAUDE_PLUGIN_DATA")
    if base:
        return Path(base) / "storybooks"
    return Path.home() / ".claude" / "plugin-data" / "bitwarden-code-review" / "storybooks"


def resolve_output(explicit: Path | None, slug: str) -> Path:
    if explicit is not None:
        return explicit
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return default_output_root() / f"{slug}-{stamp}"


# ---------- config validation ----------

def load_config(path: Path) -> dict[str, Any]:
    if not path.is_file():
        die(f"config not found: {path}")
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"config is not valid JSON: {e}")

    if not isinstance(config, dict):
        die("config must be a JSON object")
    if not isinstance(config.get("stack"), list) or not config["stack"]:
        die("config.stack must be a non-empty array")

    config.setdefault("title", "Stack review")
    config.setdefault("doc_title", config["title"])
    config.setdefault("brand_meta", config["title"])
    config.setdefault("summary", "")
    config.setdefault("storage_prefix", "review-storybook-v1")
    config.setdefault("gh_repo", "bitwarden/server")
    config.setdefault("estimated_minutes", None)
    config.setdefault("merge_plan", [])
    config.setdefault("slug", slugify(config["title"]))

    for idx, item in enumerate(config["stack"]):
        if not isinstance(item, dict):
            die(f"stack[{idx}] must be an object")
        if not item.get("key"):
            die(f"stack[{idx}].key is required (PR number or commit short-sha)")
        item["key"] = str(item["key"])
        item.setdefault("kind", "pr")
        if item["kind"] not in {"pr", "commit"}:
            die(f"stack[{idx}].kind must be 'pr' or 'commit'")
        item.setdefault("title", item["key"])
        item.setdefault("ticket", "")
        item.setdefault("description", "")
        verdict = item.setdefault("verdict", "pending")
        if verdict not in VALID_VERDICTS:
            die(f"stack[{idx}].verdict must be one of {sorted(VALID_VERDICTS)}")
        item.setdefault("verdict_label", VERDICT_LABELS[verdict])
        findings = item.setdefault("findings", {})
        for k in ("critical", "important", "debt", "suggested", "question"):
            findings.setdefault(k, 0)
        items = findings.setdefault("items", [])
        for entry in items:
            entry.setdefault("severity", "question")
            entry.setdefault("message", "")
            entry.setdefault("location", "")
            entry.setdefault("suggestion", "")
        item.setdefault("files_changed", 0)
        item.setdefault("lines_changed", 0)
        item.setdefault("diff_b64", "")
        item.setdefault("diff_path", "")

    return config


# ---------- template substitution ----------

BLOCK_RE = re.compile(
    r"<!--\s*__BW_BLOCK_START__\s+(?P<name>[\w-]+)\s*-->.*?<!--\s*__BW_BLOCK_END__\s+(?P=name)\s*-->",
    re.DOTALL,
)
JS_BLOCK_RE = re.compile(
    r"//\s*__BW_BLOCK_START__\s+(?P<name>[\w-]+)\n.*?//\s*__BW_BLOCK_END__\s+(?P=name)",
    re.DOTALL,
)


def replace_html_block(template: str, name: str, replacement: str) -> str:
    found = {"hit": False}

    def sub(m: re.Match) -> str:
        if m.group("name") == name:
            found["hit"] = True
            return replacement
        return m.group(0)

    out = BLOCK_RE.sub(sub, template)
    if not found["hit"]:
        die(f"HTML block '{name}' not found in template")
    return out


def replace_js_block(template: str, name: str, replacement: str) -> str:
    found = {"hit": False}

    def sub(m: re.Match) -> str:
        if m.group("name") == name:
            found["hit"] = True
            return replacement
        return m.group(0)

    out = JS_BLOCK_RE.sub(sub, template)
    if not found["hit"]:
        die(f"JS block '{name}' not found in template")
    return out


def replace_tokens(text: str, tokens: dict[str, str]) -> str:
    for key, value in tokens.items():
        text = text.replace(key, value)
    return text


# ---------- HTML generation ----------

def generate_cover(config: dict[str, Any]) -> str:
    stack = config["stack"]
    pr_count = len(stack)
    total_lines = sum(int(it.get("lines_changed") or 0) for it in stack)
    minutes = config.get("estimated_minutes")
    if not minutes:
        minutes = max(1, round(total_lines / 50) + pr_count)

    eyebrow = escape(f"Stack review · {pr_count} {'PR' if pr_count == 1 else 'PRs'}")
    title = escape(config["title"])
    summary = escape(config["summary"]) if config["summary"] else (
        f"{pr_count} change{'s' if pr_count != 1 else ''} packaged for review. "
        "Verdicts and findings populate as each PR is reviewed."
    )

    triage_rows = []
    for item in stack:
        key = escape(item["key"])
        title_text = escape(item["title"])
        ticket = escape(item.get("ticket") or "")
        verdict = item["verdict"]
        verdict_label = escape(item.get("verdict_label") or VERDICT_LABELS[verdict])
        badge_cls = VERDICT_BADGE_CLASS[verdict]
        ticket_html = f' · <span class="mono small">{ticket}</span>' if ticket else ""
        kind_label = "PR" if item["kind"] == "pr" else "commit"
        triage_rows.append(
            f'<li class="triage-row">'
            f'<span class="triage-key mono">{kind_label} {key}</span>'
            f'<span class="triage-title">{title_text}{ticket_html}</span>'
            f'<span class="triage-status {badge_cls}">{verdict_label}</span>'
            f"</li>"
        )

    totals = {"critical": 0, "important": 0, "debt": 0, "suggested": 0, "question": 0}
    for item in stack:
        for k in totals:
            totals[k] += int(item["findings"].get(k, 0))

    aside_rows = []
    for label, key, css in (
        ("Critical", "critical", "danger"),
        ("Important", "important", "warning"),
        ("Debt", "debt", "info"),
        ("Suggested", "suggested", "info"),
        ("Question", "question", "info"),
    ):
        value = totals[key]
        cell = str(value) if value else "—"
        color = f"var(--{css})" if value else "var(--ink-faint)"
        aside_rows.append(
            f'<div style="display: flex; justify-content: space-between; padding: 8px 0; '
            f'border-bottom: 1px dashed var(--rule);">'
            f'<span style="color: var(--ink-mute);">{label}</span>'
            f'<span style="color: {color}; font-variant-numeric: tabular-nums;">{cell}</span>'
            f"</div>"
        )

    return f"""<!-- __BW_BLOCK_START__ cover -->
<section class="page" id="page-1" data-page-key="cover">
  <div class="cover-hero-mark" aria-hidden="true">
    <svg class="brand-shield" viewBox="0 0 24 28" style="width: 44px; height: 52px;">
      <path class="shield-fill" d="M12 0C5.373 0 0 1.79 0 4v11c0 7.18 5.373 12.18 12 13 6.627-.82 12-5.82 12-13V4c0-2.21-5.373-4-12-4z"/>
      <path class="shield-glyph" d="M12 4.5c-3.59 0-7 1-7 2.4v8.1c0 4.55 3.41 7.7 7 8.5 3.59-.8 7-3.95 7-8.5V6.9c0-1.4-3.41-2.4-7-2.4zm5 10.5c0 3.5-2.55 5.95-5 6.6V6.5c2.45 0 5 .68 5 1.4V15z"/>
    </svg>
    <span style="font-family: 'Inter', sans-serif; font-weight: 700; font-size: 28px; color: var(--accent); letter-spacing: -0.022em;">Bitwarden</span>
  </div>
  <span class="eyebrow">{eyebrow}</span>
  <h1 class="display display-xl" style="margin: 24px 0 0;">{title}</h1>
  <p class="lead" style="margin-top: 28px;">{summary}</p>

  <div class="resume-banner" id="resume-banner" hidden>
    <div class="resume-text">
      <strong>Resume where you left off.</strong>
      <span id="resume-detail" class="small" style="display:block;color:var(--ink-soft);margin-top:2px;"></span>
    </div>
    <button class="btn btn-primary" id="resume-btn">Resume →</button>
  </div>

  <div class="cover-grid" style="margin-top: 56px;">
    <div>
      <span class="eyebrow">Triage list</span>
      <h2 class="display display-m" style="margin: 12px 0 8px;">Decide each in order. Skip with verdict pending.</h2>
      <ul class="triage-list" id="triage-list" role="list">
        {''.join(triage_rows)}
      </ul>
      <div style="margin-top: 32px; display: flex; gap: 12px; flex-wrap: wrap;">
        <button class="btn btn-primary" id="start-btn">Start review →</button>
        <button class="btn btn-ghost" id="merge-plan-btn">See merge plan</button>
      </div>
    </div>

    <aside>
      <div class="cover-aside">
        <span class="eyebrow">Verdicts &amp; findings</span>
        <h3 class="display display-m" style="margin: 12px 0 18px;">Stack rollup</h3>
        <div style="display: flex; flex-direction: column; gap: 10px; font-size: 13px;">
          {''.join(aside_rows)}
        </div>
      </div>
    </aside>
  </div>

  <div class="cover-stat-grid">
    <div class="cover-stat">
      <div class="cover-stat-num">{pr_count}</div>
      <div class="cover-stat-label">{'PR' if pr_count == 1 else 'PRs'} in stack</div>
    </div>
    <div class="cover-stat">
      <div class="cover-stat-num">~{total_lines}</div>
      <div class="cover-stat-label">Lines changed</div>
    </div>
    <div class="cover-stat">
      <div class="cover-stat-num">~{minutes}<span style="font-size: 16px; color: var(--ink-mute); font-weight: 400; margin-left: 4px;">min</span></div>
      <div class="cover-stat-label">Estimated read time</div>
    </div>
  </div>

  <p class="small" style="margin-top: 56px; color: var(--ink-faint); text-align: center;">
    Built locally — no GitHub or Jira data was fetched at runtime. Inline comments and decisions persist in your
    browser only. Use <kbd>→</kbd> and <kbd>←</kbd> to navigate, <kbd>Esc</kbd> to close any open editor.
  </p>
</section>
<!-- __BW_BLOCK_END__ cover -->"""


def generate_pr_pages(config: dict[str, Any]) -> str:
    sections = []
    for idx, _item in enumerate(config["stack"], start=2):
        sections.append(f'<section class="page" id="page-{idx}"></section>')
    return (
        "<!-- __BW_BLOCK_START__ pr-pages -->\n"
        + "\n".join(sections)
        + "\n<!-- __BW_BLOCK_END__ pr-pages -->"
    )


def generate_merge_plan(config: dict[str, Any], merge_page: int) -> str:
    items = config.get("merge_plan") or [
        {
            "title": f"#{it['key']} — {it['title']}",
            "body": it.get("description") or "Merge order to be decided after review.",
        }
        for it in config["stack"]
    ]
    steps = []
    for entry in items:
        title = escape(entry.get("title") or "")
        body = escape(entry.get("body") or "")
        zone = entry.get("zone")
        zone_html = (
            f'<div class="step-zone">↳ {escape(zone)}</div>' if zone else ""
        )
        steps.append(
            f'<li class="step-item">'
            f'<div class="step-num"></div>'
            f'<div class="step-content">'
            f"<h3>{title}</h3>"
            f"<p>{body}</p>"
            f"{zone_html}"
            f"</div></li>"
        )

    return f"""<!-- __BW_BLOCK_START__ merge-plan -->
<section class="page" id="page-{merge_page}" data-page-key="merge">
  <span class="eyebrow">Page {merge_page} · Merge plan</span>
  <h1 class="display display-l" style="margin: 16px 0 0;">Recommended integration sequence</h1>
  <p class="lead" style="margin-top: 24px;">
    Work through the stack in order. Hold any PR with an unresolved blocker; merge the rest as their reviews land.
  </p>

  <ol class="step-list" style="margin-top: 48px;">
    {''.join(steps)}
  </ol>

  <div class="decision-widget">
    <h3 class="decision-title">Final disposition</h3>
    <p class="decision-sub">Use the running tally above each page; this is space for an overall note.</p>
    <div class="page-comments" style="border: none; padding: 0; margin: 0;">
      <label for="merge-comment-final">Overall reviewer note (optional)</label>
      <textarea class="comment-textarea" id="merge-comment-final" data-page-comment="merge"
        placeholder="e.g., 'Approved 1 → 2 → 3 once dependency ships; 4 holds for design.'"></textarea>
    </div>
  </div>

  <p class="small" style="margin-top: 64px; text-align: center; color: var(--ink-faint);">
    End of stack · Use <strong>Export notes</strong> in the toolbar to copy all decisions and comments as Markdown.
  </p>
</section>
<!-- __BW_BLOCK_END__ merge-plan -->"""


# ---------- data.js generation ----------

def generate_data_js(config: dict[str, Any]) -> str:
    pages_data: dict[str, dict[str, Any]] = {}
    diffs: dict[str, str] = {}

    for item in config["stack"]:
        key = item["key"]
        pages_data[key] = {
            "key": key,
            "kind": item["kind"],
            "title": item["title"],
            "ticket": item.get("ticket") or "",
            "description": item.get("description") or "",
            "verdict": item["verdict"],
            "verdictLabel": item.get("verdict_label") or VERDICT_LABELS[item["verdict"]],
            "findings": item["findings"],
            "filesChanged": int(item.get("files_changed") or 0),
            "linesChanged": int(item.get("lines_changed") or 0),
        }
        diff_b64 = item.get("diff_b64") or ""
        if not diff_b64 and item.get("diff_path"):
            try:
                raw = Path(item["diff_path"]).read_text(encoding="utf-8")
                diff_b64 = base64.b64encode(raw.encode("utf-8")).decode("ascii")
            except OSError as e:
                die(f"unable to read diff_path for {key}: {e}")
        diffs[key] = diff_b64

    return (
        "// data.js — generated by scaffold.py. Do not hand-edit.\n"
        f"window.REVIEW_DATA = {json.dumps(pages_data, indent=2)};\n"
        f"window.DIFFS = {json.dumps(diffs, indent=2)};\n"
    )


# ---------- main ----------

def render_index(config: dict[str, Any]) -> str:
    template = (TEMPLATE_ROOT / "index.html.tmpl").read_text(encoding="utf-8")
    merge_page = len(config["stack"]) + 2

    template = replace_html_block(template, "cover", generate_cover(config))
    template = replace_html_block(template, "pr-pages", generate_pr_pages(config))
    template = replace_html_block(template, "merge-plan", generate_merge_plan(config, merge_page))

    return replace_tokens(
        template,
        {
            "__BW_DOC_TITLE__": escape(config["doc_title"]),
            "__BW_BRAND_META__": escape(config["brand_meta"]),
            "__BW_MERGE_PAGE__": str(merge_page),
        },
    )


def render_app_js(config: dict[str, Any]) -> str:
    template = (TEMPLATE_ROOT / "assets" / "app.js.tmpl").read_text(encoding="utf-8")
    stack_keys = [item["key"] for item in config["stack"]]
    total_pages = len(stack_keys) + 2  # cover + per-PR + merge

    config_block = (
        "// __BW_BLOCK_START__ stack-config\n"
        f"const STACK_ORDER = {json.dumps(stack_keys)};\n"
        f"const TOTAL_PAGES = {total_pages};\n"
        f"const STORAGE_PREFIX = {json.dumps(config['storage_prefix'])};\n"
        "// __BW_BLOCK_END__ stack-config"
    )
    template = replace_js_block(template, "stack-config", config_block)
    return replace_tokens(template, {"__BW_GH_REPO__": config["gh_repo"]})


def write_storybook(config: dict[str, Any], output: Path) -> None:
    if not TEMPLATE_ROOT.is_dir():
        die(f"template directory missing: {TEMPLATE_ROOT}")

    output.mkdir(parents=True, exist_ok=True)
    assets_out = output / "assets"
    assets_out.mkdir(exist_ok=True)

    (output / "index.html").write_text(render_index(config), encoding="utf-8")
    (assets_out / "app.js").write_text(render_app_js(config), encoding="utf-8")
    (assets_out / "data.js").write_text(generate_data_js(config), encoding="utf-8")

    template_assets = TEMPLATE_ROOT / "assets"
    for name in ("styles.css", "bw-shield.svg"):
        src = template_assets / name
        if not src.is_file():
            die(f"template asset missing: {src}")
        shutil.copyfile(src, assets_out / name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a code-review storybook.")
    parser.add_argument("--config", required=True, type=Path, help="Path to JSON config")
    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "Output directory. Defaults to "
            "$CLAUDE_PLUGIN_DATA/storybooks/<slug>-<timestamp>/."
        ),
    )
    args = parser.parse_args()

    config = load_config(args.config)
    output = resolve_output(args.output, config["slug"])
    write_storybook(config, output)

    print(f"Wrote storybook to {output}")
    print(f"  Stack:   {len(config['stack'])} items")
    print(f"  Open:    file://{output.resolve()}/index.html")


if __name__ == "__main__":
    main()
