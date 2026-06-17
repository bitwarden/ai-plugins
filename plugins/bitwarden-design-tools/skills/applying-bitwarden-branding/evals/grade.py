#!/usr/bin/env python3
"""Deterministic, bias-free grader for the applying-bitwarden-branding evals.

Mechanical checks only — no judgment. The subjective dimensions (review
specificity, false-positive count, affirming the correct core) are deliberately
NOT scored here; they are left for a blind LLM grader, because that calibration
is exactly the part a script cannot do (see the eval README).

The canonical palette and the official-logo signatures are read from the skill's
LIVE bundled assets (../assets), not hardcoded, so the harness automatically
tracks canon and asset changes instead of drifting against a frozen copy.

Usage:
    grade.py [RUNS_DIR]      # default: ./runs

Expected layout of RUNS_DIR (one subdir per eval from evals.json):
    RUNS_DIR/<eval-name>/outputs/*.html   (apply evals)
    RUNS_DIR/<eval-name>/outputs/*.md     (review evals)

Eval-name substrings drive which checks run:
    "apply"      -> grade_apply (HTML)        "deck" also checks off-brand fonts
    "review-tp"  -> grade_review_tp (markdown, true-positive detection)
    "review-fp"  -> deferred to the blind LLM grader

Writes grading.json into each run dir and prints a summary table.
"""
import json
import re
import sys
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
ASSETS = EVALS_DIR.parent / "assets"
TOKENS = ASSETS / "bitwarden-tokens.css"
OFFBRAND_FONTS = ["big shoulders", "ibm plex"]


def norm_hex(h):
    h = h.lower()
    if len(h) == 4:  # #abc -> #aabbcc
        h = "#" + "".join(c * 2 for c in h[1:])
    return h


def load_canon():
    """Canonical palette from the live bundled tokens, plus short-form neutrals."""
    canon = {"#fff", "#000"}
    if TOKENS.is_file():
        for m in re.finditer(r"#[0-9a-fA-F]{3,8}\b", TOKENS.read_text()):
            canon.add(norm_hex(m.group(0)[:7]))
    return canon


def load_lockup_sigs():
    """Whitespace-stripped path-data signatures from each bundled SVG asset.
    Verbatim use of any official asset embeds one of these; a redrawn shield
    will not. Truncated so minor reformatting in the output does not break the
    match while staying long enough to be unique."""
    sigs = []
    for svg in sorted(ASSETS.glob("*.svg")):
        ds = re.findall(r'\bd\s*=\s*"([^"]+)"', svg.read_text())
        if not ds:
            continue
        longest = max(ds, key=len)
        stripped = re.sub(r"\s+", "", longest)
        if len(stripped) >= 40:
            sigs.append(stripped[:40])
    return sigs


CANON = load_canon()
LOCKUP_SIGS = load_lockup_sigs()


def strip_comments(html):
    """Remove HTML and CSS comments so commentary never skews the checks."""
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    html = re.sub(r"/\*.*?\*/", " ", html, flags=re.DOTALL)
    return html


def grade_apply(html, is_deck):
    html = strip_comments(html)
    low = html.lower()
    nospace = re.sub(r"\s+", "", html)
    hexes = [
        norm_hex(x)
        for x in re.findall(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b", html)
    ]
    off_palette = sorted(set(h for h in hexes if h not in CANON))
    radius36 = (
        bool(re.search(r"border-radius\s*:\s*[^;]*36px", low)) or "36px" in low
    )
    checks = {
        "loads_inter": bool(
            re.search(r"family=inter\b", low)
            or re.search(r"[\"']inter[\"']", low)
            or re.search(r"font-family\s*:[^;{}]*\binter\b", low)
        ),
        "uses_blue_primary": "#175ddc" in low,
        "uses_deep_blue": "#0c3276" in low,
        "official_lockup_not_redrawn": any(s in nospace for s in LOCKUP_SIGS),
        "radius_36": radius36,
        "valid_self_contained_html": (
            "<html" in low and "</html>" in low and "<body" in low
        ),
    }
    if is_deck:
        checks["no_offbrand_fonts"] = not any(f in low for f in OFFBRAND_FONTS)
    metrics = {
        "off_palette_hex_count": len(off_palette),
        "off_palette_hexes": off_palette[:30],
    }
    return checks, metrics


def grade_review_tp(md):
    low = md.lower()
    checks = {
        "detect_fonts": any(f in low for f in OFFBRAND_FONTS)
        or (
            "inter" in low
            and any(
                w in low for w in ["not", "missing", "absent", "never", "no inter"]
            )
        ),
        "detect_palette": any(
            w in low for w in ["#46e08a", "phosphor", "off-brand palette", "#175ddc"]
        )
        and any(
            w in low
            for w in ["not", "missing", "absent", "off-brand", "instead", "no "]
        ),
        "detect_missing_logo": any(w in low for w in ["logo", "lockup", "shield"])
        and any(w in low for w in ["missing", "absent", "no ", "not ", "none"]),
        "detect_radius": ("radius" in low) and ("36" in low),
    }
    metrics = {
        "approx_findings": low.count("###") + low.count("\n- ") + low.count("\n1.")
    }
    return checks, metrics


def main():
    runs = Path(sys.argv[1]) if len(sys.argv) > 1 else EVALS_DIR / "runs"
    if not runs.exists():
        print(f"No run outputs at {runs}. See README.md for the expected layout.")
        return
    if not CANON or len(CANON) < 5:
        print("WARNING: canonical palette could not be read from", TOKENS)
    rows = []
    for eval_dir in sorted(runs.iterdir()):
        if not eval_dir.is_dir():
            continue
        ev = eval_dir.name
        out = eval_dir / "outputs"
        files = list(out.glob("*")) if out.exists() else []
        html = next((f for f in files if f.suffix == ".html"), None)
        md = next((f for f in files if f.suffix == ".md"), None)
        rec = {"eval": ev, "produced": bool(files)}
        if "apply" in ev and html:
            c, m = grade_apply(html.read_text(errors="ignore"), is_deck="deck" in ev)
            rec["checks"], rec["metrics"] = c, m
            rec["pass_rate"] = round(sum(c.values()) / len(c), 2)
        elif "review-tp" in ev and md:
            c, m = grade_review_tp(md.read_text(errors="ignore"))
            rec["checks"], rec["metrics"] = c, m
            rec["pass_rate"] = round(sum(c.values()) / len(c), 2)
        elif "review-fp" in ev and md:
            rec["note"] = "false-positive scoring deferred to blind LLM grader"
        (eval_dir / "grading.json").write_text(json.dumps(rec, indent=2))
        rows.append(rec)
    print(f"{'eval':40} {'made':4} {'pass':5} detail")
    for r in sorted(rows, key=lambda x: x["eval"]):
        pr = r.get("pass_rate", "-")
        fails = [k for k, v in r.get("checks", {}).items() if not v]
        off_palette = r.get("metrics", {}).get("off_palette_hex_count")
        ex = f" off_palette={off_palette}" if off_palette is not None else ""
        note = f" ({r['note']})" if "note" in r else ""
        print(
            f"{r['eval']:40} {'y' if r['produced'] else 'N':4} "
            f"{str(pr):5} fails={fails}{ex}{note}"
        )


if __name__ == "__main__":
    main()
