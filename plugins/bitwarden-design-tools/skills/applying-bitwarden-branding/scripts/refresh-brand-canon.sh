#!/usr/bin/env bash
#
# refresh-brand-canon.sh
#
# Drift guard for the bundled Bitwarden palette tokens. Compares the bundled
# values in assets/bitwarden-tokens.css against the authoritative source,
# bitwarden/brand (brand-colors/palette.scss), and either reports drift
# (--verify) or rewrites the bundle to match (--refresh).
#
# The bundle is the reliable runtime default; this script is how it stays fresh.
# Run it in CI (scheduled and on plugin PRs) and optionally before building a
# deliverable when you have network access.
#
# Usage:
#   refresh-brand-canon.sh            verify (default): exit 1 if the bundle drifted
#   refresh-brand-canon.sh --verify   same as above
#   refresh-brand-canon.sh --refresh  rewrite assets/bitwarden-tokens.css from source
#
# Degrades safely: no network or an upstream 404 leaves the bundle untouched and
# exits non-zero so callers can fall back to the bundle.
#
# Requires: curl.

set -euo pipefail

MODE="${1:---verify}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOKENS="$SKILL_DIR/assets/bitwarden-tokens.css"
SRC_URL="https://api.github.com/repos/bitwarden/brand/contents/brand-colors/palette.scss"

# palette.scss variable name : tokens.css custom property
MAP="
bitwarden-blue:--bw-blue
deep-blue:--bw-deep-blue
teal-highlight:--bw-teal
light-teal-highlight:--bw-light-teal
tertiary-green:--bw-green
tertiary-yellow:--bw-yellow
tertiary-red:--bw-red
"

if [ ! -f "$TOKENS" ]; then
  echo "ERROR: bundled tokens not found at $TOKENS" >&2
  exit 2
fi

echo "Fetching authoritative palette from bitwarden/brand ..."
SCSS="$(curl -fsSL -H 'Accept: application/vnd.github.raw' "$SRC_URL")" || {
  echo "ERROR: could not fetch palette.scss (offline or upstream moved). Bundle unchanged." >&2
  exit 2
}

drift=0
while IFS= read -r pair; do
  [ -z "$pair" ] && continue
  src_name="${pair%%:*}"
  var="${pair##*:}"
  live="$(printf '%s\n' "$SCSS" | grep -iE "\\\$${src_name}[[:space:]]*:" | grep -oiE '#[0-9a-f]{6}' | head -1 | tr 'A-F' 'a-f' || true)"
  have="$(grep -iE "^[[:space:]]*${var}[[:space:]]*:" "$TOKENS" | grep -oiE '#[0-9a-f]{6}' | head -1 | tr 'A-F' 'a-f' || true)"

  if [ -z "$live" ]; then
    echo "WARN: '$src_name' not found upstream (palette schema may have changed)"
    drift=1
    continue
  fi
  if [ "$live" != "$have" ]; then
    echo "DRIFT: $var  bundled=${have:-none}  source=$live  ($src_name)"
    drift=1
    if [ "$MODE" = "--refresh" ]; then
      sed -i.bak -E "s|(${var}[[:space:]]*:[[:space:]]*)#[0-9a-fA-F]{6}|\\1${live}|" "$TOKENS" && rm -f "$TOKENS.bak"
      echo "  refreshed $var to $live"
    fi
  fi
done <<EOF
$MAP
EOF

if [ "$MODE" = "--refresh" ]; then
  echo "Refresh complete. Review the diff and add a CHANGELOG entry before committing."
  exit 0
fi

if [ "$drift" -ne 0 ]; then
  echo "Brand-canon drift detected. Run with --refresh to sync, then review the diff." >&2
  exit 1
fi

echo "OK: bundled palette matches bitwarden/brand."
