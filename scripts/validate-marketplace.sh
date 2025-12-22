#!/usr/bin/env bash
#
# Validate marketplace.json structure and consistency.
#
# This script checks that the marketplace.json file is valid and that all
# listed plugins actually exist in the plugins directory.
#
# Usage:
#   ./validate-marketplace.sh                         # Validate all plugins
#   ./validate-marketplace.sh plugin1 plugin2         # Validate specific plugins
#   ./validate-marketplace.sh plugins/plugin1         # Validate by path

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
MARKETPLACE_JSON="$REPO_ROOT/.claude-plugin/marketplace.json"

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

# Function to validate marketplace structure
validate_marketplace_structure() {
    local has_errors=0

    # Check required top-level fields
    if ! jq -e '.name' "$MARKETPLACE_JSON" >/dev/null 2>&1; then
        print_error "Missing required field: name"
        has_errors=1
    fi

    if ! jq -e '.owner' "$MARKETPLACE_JSON" >/dev/null 2>&1; then
        print_error "Missing required field: owner"
        has_errors=1
    else
        # Check owner has name field
        if ! jq -e '.owner.name' "$MARKETPLACE_JSON" >/dev/null 2>&1; then
            print_error "'owner' object missing required 'name' field"
            has_errors=1
        fi
    fi

    if ! jq -e '.plugins' "$MARKETPLACE_JSON" >/dev/null 2>&1; then
        print_error "Missing required field: plugins"
        has_errors=1
    else
        # Check plugins is an array
        local plugin_type
        plugin_type=$(jq -r '.plugins | type' "$MARKETPLACE_JSON" 2>/dev/null)
        if [[ "$plugin_type" != "array" ]]; then
            print_error "'plugins' must be an array"
            has_errors=1
        fi

        # Check plugins array is not empty
        local plugin_count
        plugin_count=$(jq '.plugins | length' "$MARKETPLACE_JSON")
        if [[ $plugin_count -eq 0 ]]; then
            print_error "'plugins' array is empty"
            has_errors=1
        fi
    fi

    return $has_errors
}

# Function to validate a single plugin entry
validate_plugin_entry() {
    local index="$1"
    local plugin_name
    plugin_name=$(jq -r ".plugins[$index].name // empty" "$MARKETPLACE_JSON")
    local has_errors=0

    # Check required fields
    if [[ -z "$plugin_name" ]]; then
        print_error "Plugin at index $index missing required field: name"
        has_errors=1
        plugin_name="plugin at index $index"
    fi

    local source
    source=$(jq -r ".plugins[$index].source // empty" "$MARKETPLACE_JSON")
    if [[ -z "$source" ]]; then
        print_error "Plugin '$plugin_name' missing required field: source"
        has_errors=1
    else
        # Validate source path format
        if [[ ! "$source" =~ ^\./plugins/ ]]; then
            print_error "Plugin '$plugin_name' source should start with './plugins/'"
            has_errors=1
        fi
    fi

    local description
    description=$(jq -r ".plugins[$index].description // empty" "$MARKETPLACE_JSON")
    if [[ -z "$description" ]]; then
        print_error "Plugin '$plugin_name' missing required field: description"
        has_errors=1
    fi

    local version
    version=$(jq -r ".plugins[$index].version // empty" "$MARKETPLACE_JSON")
    if [[ -z "$version" ]]; then
        print_error "Plugin '$plugin_name' missing required field: version"
        has_errors=1
    else
        # Validate version format
        if ! echo "$version" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
            print_error "Plugin '$plugin_name' has invalid version format: $version (must be X.Y.Z)"
            has_errors=1
        fi
    fi

    return $has_errors
}

# Function to check if plugin exists
check_plugin_exists() {
    local index="$1"
    local plugin_name
    plugin_name=$(jq -r ".plugins[$index].name // empty" "$MARKETPLACE_JSON")
    local source
    source=$(jq -r ".plugins[$index].source // empty" "$MARKETPLACE_JSON")
    local has_errors=0

    if [[ -z "$source" ]]; then
        return 0  # Already reported in validate_plugin_entry
    fi

    # Remove leading './' if present
    source="${source#./}"

    local plugin_path="$REPO_ROOT/$source"

    if [[ ! -e "$plugin_path" ]]; then
        print_error "Plugin directory does not exist: $plugin_path"
        return 1
    fi

    if [[ ! -d "$plugin_path" ]]; then
        print_error "Plugin source is not a directory: $plugin_path"
        return 1
    fi

    # Check for plugin.json
    local plugin_json="$plugin_path/.claude-plugin/plugin.json"
    if [[ ! -f "$plugin_json" ]]; then
        print_error "Plugin missing required file: $plugin_json"
        return 1
    fi

    return 0
}

# Function to check marketplace and plugin consistency
check_consistency() {
    local has_errors=0
    local plugin_count
    plugin_count=$(jq '.plugins | length' "$MARKETPLACE_JSON")

    for ((i=0; i<plugin_count; i++)); do
        local plugin_name
        plugin_name=$(jq -r ".plugins[$i].name // empty" "$MARKETPLACE_JSON")
        local source
        source=$(jq -r ".plugins[$i].source // empty" "$MARKETPLACE_JSON")
        local marketplace_version
        marketplace_version=$(jq -r ".plugins[$i].version // empty" "$MARKETPLACE_JSON")

        if [[ -z "$source" ]] || [[ -z "$plugin_name" ]]; then
            continue
        fi

        # Remove leading './'
        source="${source#./}"
        local plugin_json="$REPO_ROOT/$source/.claude-plugin/plugin.json"

        if [[ ! -f "$plugin_json" ]]; then
            continue  # Already reported in check_plugin_exists
        fi

        # Validate JSON syntax
        if ! jq empty "$plugin_json" 2>/dev/null; then
            print_error "Invalid JSON in $plugin_json"
            has_errors=1
            continue
        fi

        # Compare versions
        local plugin_version
        plugin_version=$(jq -r '.version // empty' "$plugin_json")
        if [[ -n "$marketplace_version" ]] && [[ -n "$plugin_version" ]]; then
            if [[ "$marketplace_version" != "$plugin_version" ]]; then
                print_error "Version mismatch for '$plugin_name': marketplace.json has '$marketplace_version', plugin.json has '$plugin_version'"
                has_errors=1
            fi
        fi

        # Compare names
        local plugin_json_name
        plugin_json_name=$(jq -r '.name // empty' "$plugin_json")
        if [[ -n "$plugin_json_name" ]] && [[ "$plugin_json_name" != "$plugin_name" ]]; then
            print_error "Name mismatch for '$plugin_name': marketplace.json has '$plugin_name', plugin.json has '$plugin_json_name'"
            has_errors=1
        fi
    done

    # Check if there are plugins in the directory not in the marketplace
    local plugins_dir="$REPO_ROOT/plugins"
    if [[ -d "$plugins_dir" ]]; then
        local missing_plugins=()

        for dir in "$plugins_dir"/*; do
            if [[ -d "$dir" ]] && [[ ! "$(basename "$dir")" =~ ^\. ]]; then
                local dir_name
                dir_name=$(basename "$dir")

                # Check if this plugin is in the marketplace
                local found
                found=$(jq -r --arg name "$dir_name" '.plugins[] | select(.name == $name) | .name' "$MARKETPLACE_JSON")

                if [[ -z "$found" ]]; then
                    missing_plugins+=("$dir_name")
                fi
            fi
        done

        if [[ "${#missing_plugins[@]}" -gt 0 ]]; then
            local missing_list
            missing_list=$(IFS=', '; echo "${missing_plugins[*]}")
            print_error "Plugins exist in 'plugins/' directory but are not listed in marketplace.json: $missing_list"
            has_errors=1
        fi
    fi

    return $has_errors
}

# Main execution
main() {
    print_header "🔍 Validating marketplace.json..."
    echo ""

    if [[ ! -f "$MARKETPLACE_JSON" ]]; then
        echo -e "${RED}❌ marketplace.json not found at: $MARKETPLACE_JSON${RESET}"
        exit 1
    fi

    # Validate JSON syntax
    if ! jq empty "$MARKETPLACE_JSON" 2>/dev/null; then
        echo -e "${RED}❌ Invalid JSON in marketplace.json${RESET}"
        exit 1
    fi

    # Build list of plugins to validate
    local target_plugins=()
    if [[ $# -gt 0 ]]; then
        # Arguments provided - extract plugin names
        for arg in "$@"; do
            # Remove leading ./ if present
            arg="${arg#./}"

            # Extract plugin name from various path formats
            if [[ "$arg" =~ ^plugins/([^/]+) ]]; then
                target_plugins+=("${BASH_REMATCH[1]}")
            elif [[ -d "$REPO_ROOT/plugins/$arg" ]]; then
                target_plugins+=("$arg")
            fi
        done

        # Remove duplicates
        readarray -t target_plugins < <(printf '%s\n' "${target_plugins[@]}" | sort -u)

        if [[ "${#target_plugins[@]}" -eq 0 ]]; then
            echo -e "${YELLOW}⚠️ No valid plugins found in arguments${RESET}"
            exit 0
        fi
    fi

    # Validate marketplace structure (always check this)
    print_section "📋 Checking marketplace structure..."
    if validate_marketplace_structure; then
        print_success "Structure is valid"
    fi
    echo ""

    # Validate individual plugin entries
    print_section "📦 Checking plugin entries..."
    local plugin_count
    plugin_count=$(jq '.plugins | length' "$MARKETPLACE_JSON" 2>/dev/null || echo "0")

    if [[ $plugin_count -gt 0 ]]; then
        for ((i=0; i<plugin_count; i++)); do
            local plugin_name
            plugin_name=$(jq -r ".plugins[$i].name // \"plugin at index $i\"" "$MARKETPLACE_JSON")

            # Skip plugins not in target list if specific plugins requested
            if [[ "${#target_plugins[@]}" -gt 0 ]]; then
                local found=0
                for target in "${target_plugins[@]}"; do
                    if [[ "$plugin_name" == "$target" ]]; then
                        found=1
                        break
                    fi
                done
                if [[ $found -eq 0 ]]; then
                    continue
                fi
            fi

            local entry_errors=0
            local exists_errors=0

            validate_plugin_entry "$i" || entry_errors=1
            check_plugin_exists "$i" || exists_errors=1

            if [[ $entry_errors -eq 0 ]] && [[ $exists_errors -eq 0 ]]; then
                print_success "$plugin_name"
            else
                echo -e "  ${RED}❌ $plugin_name${RESET}"
            fi
        done
    fi
    echo ""

    # Check consistency with actual plugins
    print_section "🔄 Checking consistency with plugin files..."

    # If specific plugins requested, only check those for consistency
    if [[ "${#target_plugins[@]}" -gt 0 ]]; then
        local has_errors=0
        for target_plugin in "${target_plugins[@]}"; do
            # Find the plugin index in marketplace.json
            local found_index=-1
            for ((i=0; i<plugin_count; i++)); do
                local plugin_name
                plugin_name=$(jq -r ".plugins[$i].name // empty" "$MARKETPLACE_JSON")
                if [[ "$plugin_name" == "$target_plugin" ]]; then
                    found_index=$i
                    break
                fi
            done

            if [[ $found_index -ge 0 ]]; then
                local source
                source=$(jq -r ".plugins[$found_index].source // empty" "$MARKETPLACE_JSON")
                local marketplace_version
                marketplace_version=$(jq -r ".plugins[$found_index].version // empty" "$MARKETPLACE_JSON")

                if [[ -n "$source" ]]; then
                    source="${source#./}"
                    local plugin_json="$REPO_ROOT/$source/.claude-plugin/plugin.json"

                    if [[ -f "$plugin_json" ]]; then
                        if ! jq empty "$plugin_json" 2>/dev/null; then
                            print_error "Invalid JSON in $plugin_json"
                            has_errors=1
                        else
                            # Compare versions
                            local plugin_version
                            plugin_version=$(jq -r '.version // empty' "$plugin_json")
                            if [[ -n "$marketplace_version" ]] && [[ -n "$plugin_version" ]]; then
                                if [[ "$marketplace_version" != "$plugin_version" ]]; then
                                    print_error "Version mismatch for '$target_plugin': marketplace.json has '$marketplace_version', plugin.json has '$plugin_version'"
                                    has_errors=1
                                fi
                            fi

                            # Compare names
                            local plugin_json_name
                            plugin_json_name=$(jq -r '.name // empty' "$plugin_json")
                            if [[ -n "$plugin_json_name" ]] && [[ "$plugin_json_name" != "$target_plugin" ]]; then
                                print_error "Name mismatch for '$target_plugin': marketplace.json has '$target_plugin', plugin.json has '$plugin_json_name'"
                                has_errors=1
                            fi
                        fi
                    fi
                fi
            fi
        done

        if [[ $has_errors -eq 0 ]]; then
            print_success "All checked plugins are consistent"
        fi
    else
        # No specific plugins - check all consistency
        if check_consistency; then
            print_success "All plugins are consistent"
        fi
    fi
    echo ""

    # Print summary
    echo ""
    print_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_header "📊 Validation Summary"
    print_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Total plugins in marketplace: $plugin_count"
    echo "Total errors found: $TOTAL_ERRORS"
    echo ""

    if [[ $TOTAL_ERRORS -eq 0 ]]; then
        echo -e "${GREEN}✅ marketplace.json is valid${RESET}"
        exit 0
    else
        echo -e "${RED}❌ marketplace.json validation failed with $TOTAL_ERRORS error(s)${RESET}"
        echo ""
        echo -e "${YELLOW}To fix these issues:${RESET}"
        echo "1. Review the error messages above"
        echo "2. Ensure all required fields are present (name, owner, plugins)"
        echo "3. Verify all plugin entries have: name, source, description, version"
        echo "4. Check that versions match between marketplace.json and plugin.json files"
        echo "5. Ensure all listed plugins exist in the plugins/ directory"
        echo "6. Run validation locally: ./scripts/validate-marketplace.sh"
        echo ""
        echo -e "${YELLOW}For more information, see: scripts/README.md${RESET}"
        exit 1
    fi
}

# Run main function
main "$@"
