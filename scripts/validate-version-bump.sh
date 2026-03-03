#!/usr/bin/env bash
#
# Validate that changed plugins include a version bump.
#
# When plugin component files (agents, skills, hooks) are modified, the plugin
# version must be bumped in plugin.json and the CHANGELOG.md must be updated.
# This enforces the repository policy that all plugin changes include a version
# bump and changelog entry.
#
# Usage:
#   ./validate-version-bump.sh <base-ref> plugin1 [plugin2 ...]
#   ./validate-version-bump.sh origin/main plugins/plugin1 plugins/plugin2
#
# Arguments:
#   base-ref    Git ref to compare against (e.g., origin/main)
#   plugin...   One or more plugin names or paths to check

set -uo pipefail

# Colors for output
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
BLUE='\033[94m'
BOLD='\033[1m'
RESET='\033[0m'

# Counters
TOTAL_ERRORS=0

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PLUGINS_DIR="$REPO_ROOT/plugins"

# Source shared path sanitization library
source "$SCRIPT_DIR/lib/path-sanitization.sh"

# Function to print colored output
print_header() {
    echo -e "${BOLD}$1${RESET}"
}

print_section() {
    echo -e "${BLUE}$1${RESET}"
}

print_success() {
    echo -e "  ${GREEN}✅ $1${RESET}"
}

print_error() {
    echo -e "  ${RED}❌ $1${RESET}"
    ((TOTAL_ERRORS++))
}

print_warning() {
    echo -e "  ${YELLOW}⚠️ $1${RESET}"
}

# Function to extract version from plugin.json at a given git ref
# Args:
#   $1 - git ref (e.g., origin/main)
#   $2 - plugin name
# Returns:
#   Version string on stdout, or empty if not found
get_version_at_ref() {
    local ref="$1"
    local plugin_name="$2"
    local plugin_json_path="plugins/$plugin_name/.claude-plugin/plugin.json"

    # Try to read the file at the given ref
    local content
    if content=$(git show "$ref:$plugin_json_path" 2>/dev/null); then
        echo "$content" | jq -r '.version // empty' 2>/dev/null
    fi
}

# Function to check if CHANGELOG.md was modified for a plugin
# Args:
#   $1 - base ref
#   $2 - plugin name
# Returns:
#   0 if modified, 1 if not
changelog_was_modified() {
    local base_ref="$1"
    local plugin_name="$2"
    local changelog_path="plugins/$plugin_name/CHANGELOG.md"

    git diff --name-only "$base_ref...HEAD" -- "$changelog_path" | grep -q .
}

# Function to compare semver strings
# Returns 0 if new_version > old_version, 1 otherwise
is_version_bumped() {
    local old_version="$1"
    local new_version="$2"

    if [[ "$old_version" == "$new_version" ]]; then
        return 1
    fi

    # Split versions into components
    local old_major old_minor old_patch
    IFS='.' read -r old_major old_minor old_patch <<< "$old_version"
    local new_major new_minor new_patch
    IFS='.' read -r new_major new_minor new_patch <<< "$new_version"

    # Compare major.minor.patch
    if (( new_major > old_major )); then
        return 0
    elif (( new_major == old_major )); then
        if (( new_minor > old_minor )); then
            return 0
        elif (( new_minor == old_minor )); then
            if (( new_patch > old_patch )); then
                return 0
            fi
        fi
    fi

    return 1
}

# Function to validate version bump for a single plugin
validate_plugin_version_bump() {
    local base_ref="$1"
    local plugin_name="$2"
    local has_errors=0

    # Get version at base ref
    local base_version
    base_version=$(get_version_at_ref "$base_ref" "$plugin_name")

    # Get current version
    local plugin_json="$PLUGINS_DIR/$plugin_name/.claude-plugin/plugin.json"
    local current_version=""
    if [[ -f "$plugin_json" ]]; then
        current_version=$(jq -r '.version // empty' "$plugin_json" 2>/dev/null)
    fi

    if [[ -z "$base_version" ]]; then
        # New plugin — no base version to compare against
        print_success "$plugin_name: New plugin (no base version to compare)"
        return 0
    fi

    if [[ -z "$current_version" ]]; then
        print_error "$plugin_name: Could not read current version from plugin.json"
        return 1
    fi

    # Check if version was bumped
    if is_version_bumped "$base_version" "$current_version"; then
        print_success "$plugin_name: Version bumped $base_version -> $current_version"
    else
        print_error "$plugin_name: Version not bumped (still $base_version). Plugin component files were changed — run ./scripts/bump-plugin-version.sh $plugin_name <new-version>"
        has_errors=1
    fi

    # Check if CHANGELOG.md was updated
    if changelog_was_modified "$base_ref" "$plugin_name"; then
        print_success "$plugin_name: CHANGELOG.md updated"
    else
        print_error "$plugin_name: CHANGELOG.md not updated. Add an entry describing what changed."
        has_errors=1
    fi

    return $has_errors
}

# Main execution
main() {
    print_header "🔍 Validating version bumps for changed plugins..."
    echo ""

    if [[ $# -lt 2 ]]; then
        echo -e "${RED}Usage: $0 <base-ref> <plugin1> [plugin2 ...]${RESET}"
        echo ""
        echo "Arguments:"
        echo "  base-ref    Git ref to compare against (e.g., origin/main)"
        echo "  plugin...   One or more plugin names or plugins/ paths"
        exit 1
    fi

    local base_ref="$1"
    shift

    # Validate base ref exists
    if ! git rev-parse --verify "$base_ref" >/dev/null 2>&1; then
        echo -e "${RED}❌ Invalid base ref: $base_ref${RESET}"
        exit 1
    fi

    # Parse plugin arguments
    local plugins=()
    for arg in "$@"; do
        local plugin_name=""

        # Extract plugin name from path formats like "plugins/foo" or just "foo"
        arg="${arg#./}"
        if [[ "$arg" =~ ^plugins/([a-zA-Z0-9_-]+)$ ]]; then
            plugin_name="${BASH_REMATCH[1]}"
        elif [[ "$arg" =~ ^[a-zA-Z0-9_-]+$ ]]; then
            plugin_name="$arg"
        else
            print_warning "Skipping invalid plugin argument: $arg"
            continue
        fi

        if [[ -d "$PLUGINS_DIR/$plugin_name" ]]; then
            plugins+=("$plugin_name")
        else
            print_warning "Plugin directory not found: $plugin_name"
        fi
    done

    # Remove duplicates
    if [[ "${#plugins[@]}" -gt 0 ]]; then
        array_from_lines plugins < <(printf '%s\n' "${plugins[@]}" | sort -u)
    fi

    if [[ "${#plugins[@]}" -eq 0 ]]; then
        echo -e "${YELLOW}⚠️ No valid plugins to check${RESET}"
        exit 0
    fi

    # Validate each plugin
    for plugin_name in "${plugins[@]}"; do
        print_section "📦 Checking $plugin_name..."
        validate_plugin_version_bump "$base_ref" "$plugin_name" || true
        echo ""
    done

    # Print summary
    print_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_header "📊 Version Bump Validation Summary"
    print_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Plugins checked: ${#plugins[@]}"
    echo "Total errors: $TOTAL_ERRORS"
    echo ""

    if [[ $TOTAL_ERRORS -eq 0 ]]; then
        echo -e "${GREEN}✅ All changed plugins have proper version bumps${RESET}"
        exit 0
    else
        echo -e "${RED}❌ Version bump validation failed with $TOTAL_ERRORS error(s)${RESET}"
        echo ""
        echo -e "${YELLOW}To fix these issues:${RESET}"
        echo "1. Determine the appropriate version bump (major, minor, or patch)"
        echo "2. Run: ./scripts/bump-plugin-version.sh <plugin-name> <new-version>"
        echo "3. Add a changelog entry under the appropriate category"
        echo "4. Commit the version bump alongside your changes"
        echo ""
        echo -e "${YELLOW}For more information, see: scripts/README.md${RESET}"
        exit 1
    fi
}

# Run main function
main "$@"
