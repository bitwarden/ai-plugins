#!/usr/bin/env bash
#
# Validate Claude Code plugin structure and requirements.
#
# This script checks that all plugins in the marketplace follow the required
# structure and contain necessary files.
#
# Usage:
#   ./validate-plugin-structure.sh                    # Validate all plugins
#   ./validate-plugin-structure.sh plugin1 plugin2    # Validate specific plugins
#   ./validate-plugin-structure.sh plugins/plugin1    # Validate by path

set -uo pipefail

# Colors for output
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
BLUE='\033[94m'
BOLD='\033[1m'
RESET='\033[0m'

# Counters
TOTAL_PLUGINS=0
TOTAL_ERRORS=0
TOTAL_WARNINGS=0

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
    ((TOTAL_WARNINGS++))
}

# Function to validate plugin structure
validate_plugin_structure() {
    local plugin_path="$1"
    local plugin_name
    plugin_name=$(basename "$plugin_path")
    local has_errors=0

    # Check required files
    if [[ ! -f "$plugin_path/.claude-plugin/plugin.json" ]]; then
        print_error "Missing required file: .claude-plugin/plugin.json"
        has_errors=1
    fi

    if [[ ! -f "$plugin_path/README.md" ]]; then
        print_error "Missing required file: README.md"
        has_errors=1
    fi

    if [[ ! -f "$plugin_path/CHANGELOG.md" ]]; then
        print_error "Missing required file: CHANGELOG.md"
        has_errors=1
    fi

    # Check optional directories are actually directories if they exist
    for dir in commands agents skills hooks; do
        if [[ -e "$plugin_path/$dir" ]] && [[ ! -d "$plugin_path/$dir" ]]; then
            print_error "$dir exists but is not a directory"
            has_errors=1
        fi
    done

    # Validate agent directories have AGENT.md files
    if [[ -d "$plugin_path/agents" ]]; then
        for agent_dir in "$plugin_path/agents"/*; do
            if [[ -d "$agent_dir" ]]; then
                local agent_name
                agent_name=$(basename "$agent_dir")
                if [[ ! -f "$agent_dir/AGENT.md" ]]; then
                    print_error "Agent directory $agent_name missing AGENT.md"
                    has_errors=1
                fi
            fi
        done
    fi

    # Validate skill directories have SKILL.md files
    if [[ -d "$plugin_path/skills" ]]; then
        for skill_dir in "$plugin_path/skills"/*; do
            if [[ -d "$skill_dir" ]]; then
                local skill_name
                skill_name=$(basename "$skill_dir")
                if [[ ! -f "$skill_dir/SKILL.md" ]]; then
                    print_error "Skill directory $skill_name missing SKILL.md"
                    has_errors=1
                fi
            fi
        done
    fi

    # Validate command directories have .md files
    if [[ -d "$plugin_path/commands" ]]; then
        for command_dir in "$plugin_path/commands"/*; do
            if [[ -d "$command_dir" ]]; then
                local command_name
                command_name=$(basename "$command_dir")
                if ! find "$command_dir" -maxdepth 1 -name "*.md" -print -quit | grep -q .; then
                    print_error "Command directory $command_name has no .md files"
                    has_errors=1
                fi
            fi
        done
    fi

    return $has_errors
}

# Function to validate plugin.json
validate_plugin_json() {
    local plugin_path="$1"
    local plugin_json="$plugin_path/.claude-plugin/plugin.json"
    local has_errors=0

    if [[ ! -f "$plugin_json" ]]; then
        return 0  # Already reported in structure validation
    fi

    # Validate JSON syntax
    if ! jq empty "$plugin_json" 2>/dev/null; then
        print_error "Invalid JSON syntax in plugin.json"
        return 1
    fi

    # Check required fields
    local name
    name=$(jq -r '.name // empty' "$plugin_json")
    local version
    version=$(jq -r '.version // empty' "$plugin_json")
    local description
    description=$(jq -r '.description // empty' "$plugin_json")
    local author
    author=$(jq -r '.author // empty' "$plugin_json")

    if [[ -z "$name" ]]; then
        print_error "Missing required field in plugin.json: name"
        has_errors=1
    fi

    if [[ -z "$version" ]]; then
        print_error "Missing required field in plugin.json: version"
        has_errors=1
    elif ! echo "$version" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
        print_error "Invalid version format: $version (must be X.Y.Z)"
        has_errors=1
    fi

    if [[ -z "$description" ]]; then
        print_error "Missing required field in plugin.json: description"
        has_errors=1
    fi

    if [[ -z "$author" ]] || [[ "$author" == "null" ]]; then
        print_error "Missing required field in plugin.json: author"
        has_errors=1
    fi

    return $has_errors
}

# Function to validate README content
validate_readme_content() {
    local plugin_path="$1"
    local readme="$plugin_path/README.md"

    if [[ ! -f "$readme" ]]; then
        print_warning "README.md does not exist"
        return 0
    fi

    local content
    content=$(tr '[:upper:]' '[:lower:]' < "$readme")

    # Check for key sections (warnings only)
    if ! echo "$content" | grep -qE "(description|overview|about)"; then
        print_warning "README should include a description/overview section"
    fi

    if ! echo "$content" | grep -qE "(usage|example|getting started)"; then
        print_warning "README should include usage examples"
    fi

    if ! echo "$content" | grep -qE "(install|installation|setup)"; then
        print_warning "README should include installation instructions"
    fi
}

# Function to validate CHANGELOG format
validate_changelog_format() {
    local plugin_path="$1"
    local changelog="$plugin_path/CHANGELOG.md"
    local has_errors=0

    if [[ ! -f "$changelog" ]]; then
        print_warning "CHANGELOG.md does not exist"
        return 0
    fi

    local content
    content=$(cat "$changelog")

    # Check for Keep a Changelog format (warnings only)
    if ! echo "$content" | grep -qE "##\s+\["; then
        if ! echo "$content" | grep -q "## Unreleased"; then
            print_warning "CHANGELOG should follow Keep a Changelog format"
        fi
    fi

    # Check for standard categories
    if echo "$content" | grep -qE "##\s+\[" || echo "$content" | grep -q "## Unreleased"; then
        if ! echo "$content" | grep -qE "###\s+(Added|Changed|Deprecated|Removed|Fixed|Security)"; then
            print_warning "CHANGELOG should use standard categories (Added, Changed, Fixed, etc.)"
        fi
    fi

    # Check version consistency with plugin.json
    local plugin_json="$plugin_path/.claude-plugin/plugin.json"
    if [[ -f "$plugin_json" ]]; then
        local plugin_version
        plugin_version=$(jq -r '.version // empty' "$plugin_json" 2>/dev/null)

        if [[ -n "$plugin_version" ]]; then
            # Extract first version from CHANGELOG (format: ## [X.Y.Z])
            local changelog_version
            changelog_version=$(grep -E '^##\s+\[[0-9]+\.[0-9]+\.[0-9]+\]' "$changelog" | head -1 | sed -E 's/^##[[:space:]]+\[([0-9]+\.[0-9]+\.[0-9]+)\].*/\1/')

            if [[ -n "$changelog_version" ]] && [[ "$changelog_version" != "$plugin_version" ]]; then
                print_error "CHANGELOG version ($changelog_version) doesn't match plugin.json version ($plugin_version)"
                has_errors=1
            elif [[ -z "$changelog_version" ]] && echo "$content" | grep -qE "##\s+\["; then
                print_warning "CHANGELOG has version entries but first version could not be parsed"
            fi
        fi
    fi

    return $has_errors
}

# Function to validate AGENT.md frontmatter
validate_agent_frontmatter() {
    local agent_file="$1"
    local plugin_name="$2"
    local agent_name
    agent_name=$(basename "$(dirname "$agent_file")")
    local has_errors=0

    # Check for YAML frontmatter
    if ! grep -q "^---$" "$agent_file"; then
        print_error "Agent $plugin_name/$agent_name: Missing YAML frontmatter"
        return 1
    fi

    # Extract frontmatter (between first two --- markers)
    # Use awk for more robust YAML frontmatter extraction
    local frontmatter
    frontmatter=$(awk '/^---$/{if(++n==2){exit}}n==1' "$agent_file")

    if [[ -z "$frontmatter" ]]; then
        print_error "Agent $plugin_name/$agent_name: Empty frontmatter"
        return 1
    fi

    # Check required fields
    if ! echo "$frontmatter" | grep -q "^name:"; then
        print_error "Agent $plugin_name/$agent_name: Missing required field: name"
        has_errors=1
    fi

    if ! echo "$frontmatter" | grep -q "^description:"; then
        print_error "Agent $plugin_name/$agent_name: Missing required field: description"
        has_errors=1
    fi

    # Validate tools field is present and looks like an array
    if echo "$frontmatter" | grep -q "^tools:"; then
        # Check if the next line starts with a dash (array item)
        local tools_line
        tools_line=$(echo "$frontmatter" | grep -n "^tools:" | cut -d: -f1)
        if [[ -n "$tools_line" ]]; then
            local next_line=$((tools_line + 1))
            local next_content
            next_content=$(echo "$frontmatter" | sed -n "${next_line}p")
            if [[ -n "$next_content" ]] && [[ ! "$next_content" =~ ^[[:space:]]*- ]]; then
                print_error "Agent $plugin_name/$agent_name: 'tools' field must be an array"
                has_errors=1
            fi
        fi
    fi

    return $has_errors
}

# Function to validate SKILL.md frontmatter
validate_skill_frontmatter() {
    local skill_file="$1"
    local plugin_name="$2"
    local skill_name
    skill_name=$(basename "$(dirname "$skill_file")")
    local has_errors=0

    # Check for YAML frontmatter
    if ! grep -q "^---$" "$skill_file"; then
        print_error "Skill $plugin_name/$skill_name: Missing YAML frontmatter"
        return 1
    fi

    # Extract frontmatter (between first two --- markers)
    # Use awk for more robust YAML frontmatter extraction
    local frontmatter
    frontmatter=$(awk '/^---$/{if(++n==2){exit}}n==1' "$skill_file")

    if [[ -z "$frontmatter" ]]; then
        print_error "Skill $plugin_name/$skill_name: Empty frontmatter"
        return 1
    fi

    # Check required fields
    if ! echo "$frontmatter" | grep -q "^name:"; then
        print_error "Skill $plugin_name/$skill_name: Missing required field: name"
        has_errors=1
    fi

    if ! echo "$frontmatter" | grep -q "^description:"; then
        print_error "Skill $plugin_name/$skill_name: Missing required field: description"
        has_errors=1
    fi

    return $has_errors
}

# Main execution
main() {
    print_header "🔍 Validating plugin structure..."
    echo ""

    if [[ ! -d "$PLUGINS_DIR" ]]; then
        echo -e "${RED}❌ Plugins directory not found: $PLUGINS_DIR${RESET}"
        exit 1
    fi

    # Get list of plugin directories
    local plugins=()

    # If arguments provided, validate only those plugins
    if [[ $# -gt 0 ]]; then
        echo "DEBUG: Received $# argument(s): $*"
        for arg in "$@"; do
            echo "DEBUG: Processing argument: '$arg'"
            # Use shared sanitization function to safely parse plugin path
            local sanitized_path
            if sanitized_path=$(sanitize_plugin_path "$arg" "$PLUGINS_DIR" 2>&1); then
                echo "DEBUG: ✓ Sanitized to: '$sanitized_path'"
                plugins+=("$sanitized_path")
            else
                echo "DEBUG: ✗ Failed to sanitize argument '$arg'"
                echo "DEBUG:   Output from sanitize_plugin_path: $sanitized_path"
            fi
        done

        # Remove duplicates (only if we have plugins)
        if [[ "${#plugins[@]}" -gt 0 ]]; then
            array_from_lines plugins < <(printf '%s\n' "${plugins[@]}" | sort -u)
        fi

        if [[ "${#plugins[@]}" -eq 0 ]]; then
            echo -e "${YELLOW}⚠️ No valid plugin directories found in arguments${RESET}"
            exit 0
        fi
    else
        # No arguments - validate all plugins
        for dir in "$PLUGINS_DIR"/*; do
            if [[ -d "$dir" ]] && [[ ! "$(basename "$dir")" =~ ^\. ]]; then
                plugins+=("$dir")
            fi
        done

        if [[ "${#plugins[@]}" -eq 0 ]]; then
            echo -e "${YELLOW}⚠️ No plugins found in $PLUGINS_DIR${RESET}"
            exit 0
        fi

        # Sort plugins
        array_from_lines plugins < <(printf '%s\n' "${plugins[@]}" | sort)
    fi

    # Validate each plugin
    for plugin_path in "${plugins[@]}"; do
        local plugin_name
        plugin_name=$(basename "$plugin_path")
        print_section "📦 Validating $plugin_name..."

        ((TOTAL_PLUGINS++))

        local plugin_has_errors=0

        # Run validations
        validate_plugin_structure "$plugin_path" || plugin_has_errors=1
        validate_plugin_json "$plugin_path" || plugin_has_errors=1
        validate_readme_content "$plugin_path" || true
        validate_changelog_format "$plugin_path" || plugin_has_errors=1

        # Validate agents if they exist
        if [[ -d "$plugin_path/agents" ]]; then
            for agent_file in "$plugin_path/agents"/*/AGENT.md; do
                if [[ -f "$agent_file" ]]; then
                    validate_agent_frontmatter "$agent_file" "$plugin_name" || plugin_has_errors=1
                fi
            done
        fi

        # Validate skills if they exist
        if [[ -d "$plugin_path/skills" ]]; then
            for skill_file in "$plugin_path/skills"/*/SKILL.md; do
                if [[ -f "$skill_file" ]]; then
                    validate_skill_frontmatter "$skill_file" "$plugin_name" || plugin_has_errors=1
                fi
            done
        fi

        if [[ $plugin_has_errors -eq 0 ]]; then
            print_success "Structure is valid"
        fi

        echo ""
    done

    # Print summary
    echo ""
    print_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_header "📊 Validation Summary"
    print_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Total plugins checked: $TOTAL_PLUGINS"
    echo "Total errors: $TOTAL_ERRORS"
    echo "Total warnings: $TOTAL_WARNINGS"
    echo ""

    if [[ $TOTAL_ERRORS -eq 0 ]]; then
        echo -e "${GREEN}✅ All plugins passed structure validation${RESET}"
        exit 0
    else
        echo -e "${RED}❌ Plugin validation failed with $TOTAL_ERRORS error(s)${RESET}"
        echo ""
        echo -e "${YELLOW}To fix these issues:${RESET}"
        echo "1. Review the error messages above for each plugin"
        echo "2. Add missing required files (plugin.json, README.md, CHANGELOG.md)"
        echo "3. Ensure all agent/skill directories contain their respective .md files"
        echo "4. Run validation locally: ./scripts/validate-plugin-structure.sh"
        echo ""
        echo -e "${YELLOW}For more information, see: scripts/README.md${RESET}"
        exit 1
    fi
}

# Run main function
main "$@"
