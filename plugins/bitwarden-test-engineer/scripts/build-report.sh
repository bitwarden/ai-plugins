#!/usr/bin/env bash
#
# build-report.sh — assemble a self-contained HTML report for the
# bitwarden-test-engineer plugin by splicing the canonical stylesheet into a
# model-authored content fragment.
#
# The model writes a fragment whose <style> element contains a single sentinel
# line; this script replaces that sentinel with references/report-style.css
# verbatim. That keeps the ~400-line stylesheet out of model output entirely
# (no token cost, no drift between the two reports) while the model authors only
# the report's actual content.
#
# Usage (single report):
#   build-report.sh --kind <test-stack|test-coverage> --slug <slug> \
#                   --date <YYYY-MM-DD> <fragment-html-file>
#
# Usage (combined two-tab page):
#   build-report.sh --kind test-combined --slug <slug> --date <YYYY-MM-DD> \
#                   --current <coverage-report.html> \
#                   --recommended <test-stack-report.html>
#
# The combined mode assembles ONE page with two CSS-only tabs — "Current
# coverage" (the assessing-test-coverage report) and "Recommended coverage" (the
# analyzing-test-stack report) — from the two already-built standalone report
# files. It reuses each report's <header>/<main>, namespaces the section ids so
# the two bodies coexist in one document (cur-* / rec-*), and splices the
# stylesheet in once. The two source reports are read, not modified, and their
# standalone files remain; the combined page is an additional deliverable.
#
# Writes the report into a per-change directory, creating it if needed, and
# prints the final path to stdout:
#
#   test-engineer-report-<slug>-<date>/coverage.html      (--kind test-coverage)
#   test-engineer-report-<slug>-<date>/recommended.html   (--kind test-stack)
#   test-engineer-report-<slug>-<date>/combined.html       (--kind test-combined)
#
# The directory name derives only from --slug/--date, so all three of a run's
# reports land in the same folder. Re-running the same change on the same date
# refreshes the report in place (the prior file is overwritten).
#
# Input files are left untouched; delete any temporary fragment yourself.

set -euo pipefail

SENTINEL='/* @@BITWARDEN_REPORT_STYLESHEET@@ */'
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSS_FILE="${SCRIPT_DIR}/../references/report-style.css"

KIND=""
SLUG=""
DATE=""
FRAGMENT=""
CURRENT=""
RECOMMENDED=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --kind) KIND="${2:-}"; shift 2 ;;
    --slug) SLUG="${2:-}"; shift 2 ;;
    --date) DATE="${2:-}"; shift 2 ;;
    --current) CURRENT="${2:-}"; shift 2 ;;
    --recommended) RECOMMENDED="${2:-}"; shift 2 ;;
    -h|--help)
      grep '^#' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    --*) echo "build-report.sh: unknown option '$1'" >&2; exit 2 ;;
    *) FRAGMENT="$1"; shift ;;
  esac
done

# --- validate common inputs --------------------------------------------------
case "$KIND" in
  test-stack|test-coverage|test-combined) ;;
  *) echo "build-report.sh: --kind must be 'test-stack', 'test-coverage', or 'test-combined' (got '${KIND}')" >&2; exit 2 ;;
esac

if [[ -z "$SLUG" ]]; then
  echo "build-report.sh: --slug is required (a short kebab-case change identifier)" >&2
  exit 2
fi
if [[ ! "$SLUG" =~ ^[a-zA-Z0-9._-]+$ ]]; then
  echo "build-report.sh: --slug '${SLUG}' must be kebab-case (letters, digits, dot, dash, underscore)" >&2
  exit 2
fi
if [[ ! "$DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "build-report.sh: --date must be YYYY-MM-DD (got '${DATE}')" >&2
  exit 2
fi
if [[ ! -f "$CSS_FILE" ]]; then
  echo "build-report.sh: stylesheet not found at '${CSS_FILE}'" >&2
  exit 1
fi

OUTDIR="test-engineer-report-${SLUG}-${DATE}"
case "$KIND" in
  test-coverage) BASENAME="coverage.html" ;;
  test-stack)    BASENAME="recommended.html" ;;
  test-combined) BASENAME="combined.html" ;;
esac
mkdir -p "$OUTDIR"
OUT="${OUTDIR}/${BASENAME}"

# Splice the canonical stylesheet in place of the sentinel line. awk reads the
# CSS file line by line, so no shell escaping ever touches the CSS content.
splice_css() {
  awk -v css="$CSS_FILE" -v sentinel="$SENTINEL" '
    index($0, sentinel) {
      while ((getline line < css) > 0) print line
      close(css)
      next
    }
    { print }
  '
}

if [[ "$KIND" == "test-combined" ]]; then
  # --- combined two-tab page -------------------------------------------------
  for f in "$CURRENT" "$RECOMMENDED"; do
    if [[ -z "$f" || ! -f "$f" ]]; then
      echo "build-report.sh: --kind test-combined needs --current and --recommended report files (missing: '${f}')" >&2
      exit 2
    fi
    if ! grep -q '<main' "$f"; then
      echo "build-report.sh: '${f}' does not look like a built report (no <main> element)" >&2
      exit 1
    fi
  done

  # Pull the inclusive <header>…</header> or <main>…</main> region from a report.
  # Only scan from <body> onward: the finished reports carry the whole stylesheet
  # inlined in <head>, and a CSS comment can legitimately mention "<main>" etc. —
  # gating on <body> keeps those from being mistaken for the real element.
  extract_region() {
    awk -v startTag="$2" -v endTag="$3" '
      /<body[ >]/ { inBody = 1 }
      !inBody { next }
      index($0, startTag) { f = 1 }
      f { print }
      index($0, endTag) { if (f) exit }
    ' "$1"
  }

  # Namespace the normative section ids (and their in-page anchor links) so the
  # two report bodies can share one document without colliding on #overview etc.
  IDS='overview|summary|evidence|coverage|recommendations|gaps'
  prefix_ids() {
    sed -E \
      -e "s/ id=\"(${IDS})\"/ id=\"$1-\1\"/g" \
      -e "s/href=\"#(${IDS})\"/href=\"#$1-\1\"/g"
  }

  {
    cat <<HTML
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Test Engineering Report — ${SLUG}</title>
    <style>
      ${SENTINEL}
    </style>
  </head>
  <body>
HTML
    # Shared masthead: reuse the recommendation report's header, relabel its
    # eyebrow so the page reads as the combined deliverable, not one report.
    extract_region "$RECOMMENDED" "<header" "</header>" \
      | sed -E 's#(<p class="eyebrow">)[^<]*(</p>)#\1Test Engineering Report\2#'
    cat <<'HTML'
    <input class="tab-input" type="radio" name="report-view" id="tab-current" checked />
    <input class="tab-input" type="radio" name="report-view" id="tab-recommended" />
    <nav class="tablist" aria-label="Report views">
      <label for="tab-current">Current coverage</label>
      <label for="tab-recommended">Recommended coverage</label>
    </nav>
    <section class="tabpanel" data-panel="current" aria-label="Current coverage">
HTML
    extract_region "$CURRENT" "<main" "</main>" | prefix_ids cur
    cat <<'HTML'
    </section>
    <section class="tabpanel" data-panel="recommended" aria-label="Recommended coverage">
HTML
    extract_region "$RECOMMENDED" "<main" "</main>" | prefix_ids rec
    # The reused masthead carries id="top"; emit the back-to-top control once for
    # the whole page. Each standalone report's own control sits after its </main>,
    # outside the extracted region, so the combined page would otherwise have none.
    cat <<'HTML'
    </section>
    <a class="to-top" href="#top" aria-label="Back to top">Top</a>
  </body>
</html>
HTML
  } | splice_css > "$OUT"

  echo "$OUT"
  exit 0
fi

# --- single report (test-stack | test-coverage) ------------------------------
if [[ -z "$FRAGMENT" || ! -f "$FRAGMENT" ]]; then
  echo "build-report.sh: fragment HTML file not found: '${FRAGMENT}'" >&2
  exit 2
fi
if ! grep -qF "$SENTINEL" "$FRAGMENT"; then
  echo "build-report.sh: fragment '${FRAGMENT}' has no stylesheet sentinel." >&2
  echo "  Put exactly this line inside the <style> element: ${SENTINEL}" >&2
  exit 1
fi

splice_css < "$FRAGMENT" > "$OUT"

echo "$OUT"
