#!/usr/bin/env bash
# Clones the plugin at a pinned commit and, if it launches an npm-based MCP
# server, pulls that package's registry metadata, tarball, and audit data.
# Ends by printing an inventory of what it gathered, keyed by SCRATCH_DIR.
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "usage: gather-evidence.sh <repo-url> <commit-sha>" >&2
  exit 2
fi

repo_url=$1
commit_sha=$2

case "$repo_url" in
  https://*|git@*) ;;
  *) echo "Refusing to clone unsupported URL scheme: $repo_url" >&2; exit 1 ;;
esac

scratch=$(mktemp -d /tmp/plugin-audit.XXXXXXXX)
# Any failure below aborts before the inventory prints, so the caller never
# learns the scratch path and cannot remove it. Delete it here rather than
# leave a partial clone of adversarial code on disk.
trap 'rc=$?; if [ "$rc" -ne 0 ]; then rm -rf -- "$scratch"; fi; exit "$rc"' EXIT

# Markers name evidence that could not be collected. Each goes to stderr as
# it happens and into the inventory at the end, so a gap is visible whether
# the caller reads the stream or only the summary. The inventory carries the
# marker name alone: the message can quote a package spec taken from the
# audited repo, and that text does not belong in trusted script output.
not_collected=""
mark() {
  not_collected="${not_collected:+$not_collected }$1"
  echo "$1: $2" >&2
}

# core.symlinks=false is written into the new repo's config, so both this
# clone and the checkout below materialize a committed symlink as a plain
# file holding its target path. Nothing in the audited tree can then
# redirect a later read (`Read`, `grep`, `strings`) at a file outside the
# scratch directory, such as the runner's .git/config or /proc/self/environ.
git clone -c core.symlinks=false -- "$repo_url" "$scratch/repo"
git -C "$scratch/repo" checkout --detach "$commit_sha" --
git -C "$scratch/repo" log -1 --format='%H %aI %an <%ae> %s' > "$scratch/commit-info.txt"
git -C "$scratch/repo" shortlog -sne --all > "$scratch/authors.txt"

# Inventory what was neutralized. A committed symlink whose target escapes
# the repo is evidence, not a curiosity, so the caller gets it as a file.
: > "$scratch/symlinks.txt"
git -C "$scratch/repo" ls-files -s | grep '^120000 ' | cut -f2- | while IFS= read -r link; do
  printf '%s -> %s\n' "$link" "$(cat -- "$scratch/repo/$link" 2>/dev/null)"
done >> "$scratch/symlinks.txt" || true

mcp_json="$scratch/repo/.mcp.json"
pkg_specs=""
pkg_spec=""
if [ -f "$mcp_json" ]; then
  pkg_specs=$(grep -oE '@?[a-zA-Z0-9_.-]+(/[a-zA-Z0-9_.-]+)?@[0-9][a-zA-Z0-9_.-]*' "$mcp_json" || true)
  pkg_spec=$(printf '%s\n' "$pkg_specs" | head -1)
  if [ "$(printf '%s\n' "$pkg_specs" | grep -c '.')" -gt 1 ]; then
    mark MULTIPLE_NPM_PACKAGES_DETECTED ".mcp.json matched more than one name@version spec; only $pkg_spec was audited. Inspect the rest manually."
  fi
fi

if [ -n "$pkg_spec" ]; then
  pkg_dir="$scratch/pkg"
  mkdir -p "$pkg_dir"
  # npm writes a JSON error object to stdout when it cannot resolve a spec,
  # so a failed view leaves a plausible-looking file behind. Remove it: the
  # marker says the evidence is missing, and nothing should remain on disk
  # that a later read could mistake for registry metadata.
  (cd "$pkg_dir" && npm view --registry https://registry.npmjs.org --json -- "$pkg_spec" > "$pkg_dir/view.json") \
    || { rm -f "$pkg_dir/view.json"; mark NPM_VIEW_FAILED "npm view could not resolve $pkg_spec."; }
  (cd "$pkg_dir" && npm pack --registry https://registry.npmjs.org -- "$pkg_spec") \
    || mark NPM_PACK_FAILED "npm pack could not fetch a tarball for $pkg_spec."
  tgz=$(find "$pkg_dir" -maxdepth 1 -name '*.tgz' | head -1 || true)
  if [ -n "$tgz" ]; then
    openssl dgst -sha512 -binary "$tgz" | openssl base64 -A > "$pkg_dir/tarball.sha512" \
      || mark TARBALL_HASH_UNAVAILABLE "could not hash the published tarball."

    if tar -xzf "$tgz" -C "$pkg_dir"; then
      # tar refuses to write *through* an existing symlink, but it will
      # happily create a symlink member pointing anywhere. Same exposure as
      # the clone above, so record the targets and then remove the links.
      : > "$pkg_dir/symlinks.txt"
      find "$pkg_dir" -type l | while IFS= read -r link; do
        printf '%s -> %s\n' "$link" "$(readlink -- "$link")"
      done >> "$pkg_dir/symlinks.txt" || true
      find "$pkg_dir" -type l -delete

      pkg_no_version=${pkg_spec%@*}
      encoded=$(printf '%s' "$pkg_no_version" | sed 's/\//%2F/')
      # A missing attestation answers 404, which means the package is
      # unsigned: a security-relevant result, not a transport error. -f turns
      # it into a failure so the registry's error body is never saved as if
      # it were attestation data, and --max-time keeps a stalled connection
      # from hanging the audit indefinitely.
      curl -fsS --max-time 60 "https://registry.npmjs.org/-/npm/v1/attestations/${encoded}@${pkg_spec##*@}" -o "$pkg_dir/attestations.json" \
        || { rm -f "$pkg_dir/attestations.json"; mark ATTESTATIONS_UNAVAILABLE "no attestations retrieved; treat the package as unsigned unless proven otherwise."; }

      # A published tarball almost never ships its own lockfile, so `npm audit`
      # fails with ENOLOCK unless the package happens to bundle one. Generate a
      # lockfile from package.json first so audit has a dependency tree to
      # check; if that also fails, say so explicitly rather than leave an error
      # object in audit.json that looks like a clean "no vulnerabilities" result.
      if [ -f "$pkg_dir/package/npm-shrinkwrap.json" ] || [ -f "$pkg_dir/package/package-lock.json" ] \
        || (cd "$pkg_dir/package" && npm install --package-lock-only --ignore-scripts --registry https://registry.npmjs.org > /dev/null 2>&1); then
        (cd "$pkg_dir/package" && npm audit --registry https://registry.npmjs.org --json > "$pkg_dir/audit.json") || true
      else
        mark NPM_AUDIT_UNAVAILABLE "could not produce or generate a lockfile, npm audit did not run."
      fi
    else
      mark TARBALL_EXTRACT_FAILED "the published tarball did not extract cleanly; inspect it manually."
    fi
  fi
else
  # No single pinned npm@version spec found in .mcp.json (or no .mcp.json at
  # all). This does not mean there is nothing to audit: the server may be
  # declared via plugin.json's mcpServers field, use a semver range instead
  # of a pin, run multiple servers, or not be npm-based at all. Say so
  # explicitly so the caller investigates manually rather than assuming this
  # script covered it.
  mark NO_NPM_PACKAGE_DETECTED "no pinned name@version spec found in .mcp.json. Check plugin.json's mcpServers field and inspect the server's dependency manifest directly."
fi

# Describe what is actually on disk, so the caller does not have to carry a
# second copy of this layout. Every label here is a fixed string or a count;
# nothing derived from the audited repo is echoed, since script output reads
# as more trustworthy than the file contents it describes.
count_lines() {
  if [ -f "$1" ]; then wc -l < "$1" | tr -d ' '; else echo 0; fi
}

# A failed fetch can still leave a zero-byte file behind (the redirect
# creates it before the command runs), so evidence files must be non-empty
# to be advertised as collected. The symlink inventories are the exception:
# an empty one is a positive result worth stating.
row() {
  local path="$scratch/$1"
  case "$1" in
    */) if [ -d "$path" ]; then printf '%-22s %s\n' "$1" "$2"; fi ;;
    *) if [ -s "$path" ]; then printf '%-22s %s\n' "$1" "$2"; fi ;;
  esac
}

row_any() {
  if [ -e "$scratch/$1" ]; then
    printf '%-22s %s\n' "$1" "$2"
  fi
}

echo
echo "=== gather-evidence.sh inventory ==="
echo "SCRATCH_DIR=$scratch"
row "repo/" "clone at the pinned commit"
row "commit-info.txt" "sha, date, author, subject"
row "authors.txt" "all-time author tallies"
row_any "symlinks.txt" "committed symlinks neutralized to plain files: $(count_lines "$scratch/symlinks.txt")"
row "pkg/view.json" "npm registry metadata"
if [ -n "$(find "$scratch/pkg" -maxdepth 1 -name '*.tgz' 2>/dev/null | head -1)" ]; then
  printf '%-22s %s\n' "pkg/<name>.tgz" "published tarball"
fi
row "pkg/tarball.sha512" "sha512 of the published tarball"
row "pkg/package/" "extracted tarball contents"
row_any "pkg/symlinks.txt" "packaged symlinks removed: $(count_lines "$scratch/pkg/symlinks.txt")"
row "pkg/attestations.json" "npm provenance attestations"
row "pkg/audit.json" "npm audit output"
if [ -n "$not_collected" ]; then
  echo "NOT COLLECTED: $not_collected"
fi
