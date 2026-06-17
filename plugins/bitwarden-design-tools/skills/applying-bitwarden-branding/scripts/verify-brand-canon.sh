#!/usr/bin/env bash
#
# verify-brand-canon.sh
#
# Drift detector for the bundled Bitwarden palette tokens. Compares the bundled
# values in assets/bitwarden-tokens.css against the authoritative source,
# bitwarden/brand (brand-colors/palette.scss), and reports any drift along with
# the correct live value to use.
#
# This script never modifies the bundle. If it reports drift, use the printed
# "correct" values in the deliverable being branded. Refreshing the bundled
# tokens themselves is a separate change to the bitwarden-design-tools plugin
# (a marketplace PR), not something to do mid-session.
#
# Run it before building a deliverable when network is available.
#
# Exit codes:
#   0  bundle matches the source
#   1  drift detected (correct values printed)
#   2  could not fetch the source (offline / upstream moved); bundle untouched
#
# Requires: curl.

set -euo pipefail

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

echo "Checking bundled brand tokens against bitwarden/brand ..."
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
    echo "WARN: \$${src_name} not found upstream (palette schema may have changed)"
    drift=1
    continue
  fi
  if [ "$live" != "$have" ]; then
    printf 'DRIFT  %-16s bundled %-9s correct %-9s  ($%s)\n' "$var" "${have:-none}" "$live" "$src_name"
    drift=1
  fi
done <<EOF
$MAP
EOF

if [ "$drift" -ne 0 ]; then
  echo "" >&2
  echo "Bundled brand tokens are out of date. Use the 'correct' values above in" >&2
  echo "the deliverable you are branding. Do not edit the bundle here: refreshing" >&2
  echo "assets/bitwarden-tokens.css is a separate change to the bitwarden-design-tools" >&2
  echo "plugin (open a marketplace PR)." >&2
  exit 1
fi

echo "OK: bundled palette matches bitwarden/brand."
