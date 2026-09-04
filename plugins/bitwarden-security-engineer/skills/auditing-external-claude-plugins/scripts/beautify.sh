#!/usr/bin/env bash
# Beautifies a minified/bundled JS file using a js-beautify pinned in this
# script's own package.json/lockfile, rather than a version string embedded
# in SKILL.md, so Renovate can track and bump it like any other dependency.
# Prints the output file path as the last line of output.
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "usage: beautify.sh <input-file> [output-file]" >&2
  exit 2
fi

input=$1
# Default the output alongside the input rather than the caller's cwd, so an
# unspecified output path lands inside gather-evidence.sh's scratch directory
# instead of leaking a de-minified copy of adversarial content into the
# working repo.
output=${2:-$(dirname -- "$input")/pretty.js}
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

npm --prefix "$script_dir" install --registry https://registry.npmjs.org --no-audit --no-fund --silent
npx --prefix "$script_dir" --no-install js-beautify "$input" -o "$output"

echo "$output"
