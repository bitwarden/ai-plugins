#!/usr/bin/env bash
# Clones the plugin at a pinned commit and, if it launches an npm-based MCP
# server, pulls that package's registry metadata, tarball, and audit data.
# Prints the scratch directory path as the last line of output.
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "usage: gather-evidence.sh <repo-url> <commit-sha>" >&2
  exit 2
fi

repo_url=$1
commit_sha=$2
scratch=$(mktemp -d /tmp/plugin-audit.XXXXXXXX)

case "$repo_url" in
  https://*|git@*) ;;
  *) echo "Refusing to clone unsupported URL scheme: $repo_url" >&2; exit 1 ;;
esac

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
    echo "MULTIPLE_NPM_PACKAGES_DETECTED: .mcp.json matched more than one name@version spec; only $pkg_spec was audited. Inspect the rest manually." >&2
  fi
fi

if [ -n "$pkg_spec" ]; then
  pkg_dir="$scratch/pkg"
  mkdir -p "$pkg_dir"
  (cd "$pkg_dir" && npm view --registry https://registry.npmjs.org --json -- "$pkg_spec" > "$pkg_dir/view.json") \
    || echo "NPM_VIEW_FAILED: npm view could not resolve $pkg_spec." >&2
  (cd "$pkg_dir" && npm pack --registry https://registry.npmjs.org -- "$pkg_spec") \
    || echo "NPM_PACK_FAILED: npm pack could not fetch a tarball for $pkg_spec." >&2
  tgz=$(find "$pkg_dir" -maxdepth 1 -name '*.tgz' | head -1 || true)
  if [ -n "$tgz" ]; then
    openssl dgst -sha512 -binary "$tgz" | openssl base64 -A > "$pkg_dir/tarball.sha512" \
      || echo "TARBALL_HASH_UNAVAILABLE: could not hash $tgz." >&2

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
      curl -sS "https://registry.npmjs.org/-/npm/v1/attestations/${encoded}@${pkg_spec##*@}" -o "$pkg_dir/attestations.json" \
        || echo "ATTESTATIONS_UNAVAILABLE: request for $pkg_spec's attestations failed (network error, not a 404)." >&2

      # A published tarball almost never ships its own lockfile, so `npm audit`
      # fails with ENOLOCK unless the package happens to bundle one. Generate a
      # lockfile from package.json first so audit has a dependency tree to
      # check; if that also fails, say so explicitly rather than leave an error
      # object in audit.json that looks like a clean "no vulnerabilities" result.
      if [ -f "$pkg_dir/package/npm-shrinkwrap.json" ] || [ -f "$pkg_dir/package/package-lock.json" ] \
        || (cd "$pkg_dir/package" && npm install --package-lock-only --ignore-scripts --registry https://registry.npmjs.org > /dev/null 2>&1); then
        (cd "$pkg_dir/package" && npm audit --registry https://registry.npmjs.org --json > "$pkg_dir/audit.json") || true
      else
        echo "NPM_AUDIT_UNAVAILABLE: could not produce or generate a lockfile for $pkg_spec, npm audit did not run." >&2
      fi
    else
      echo "TARBALL_EXTRACT_FAILED: $tgz did not extract cleanly; inspect it manually." >&2
    fi
  fi
else
  # No single pinned npm@version spec found in .mcp.json (or no .mcp.json at
  # all). This does not mean there is nothing to audit: the server may be
  # declared via plugin.json's mcpServers field, use a semver range instead
  # of a pin, run multiple servers, or not be npm-based at all. Say so
  # explicitly so the caller investigates manually rather than assuming this
  # script covered it.
  echo "NO_NPM_PACKAGE_DETECTED: no pinned name@version spec found in .mcp.json. Check plugin.json's mcpServers field and inspect the server's dependency manifest directly." >&2
fi

echo "$scratch"
