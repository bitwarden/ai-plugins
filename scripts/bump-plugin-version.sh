#!/bin/bash
# bump-plugin-version.sh
# Automates version bumping for plugins in the Bitwarden AI Plugins Marketplace
# Updates version across marketplace.json, plugin.json, and all agent AGENT.md files
#
# Usage: ./scripts/bump-plugin-version.sh <plugin-name> <new-version>
# Example: ./scripts/bump-plugin-version.sh bitwarden-code-review 1.3.4

set -euo pipefail

# Color output for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to display usage information
usage() {
    cat << EOF
Usage: $0 <plugin-name> <new-version>

Bump the version of a plugin across all required files.

Arguments:
  plugin-name    Name of the plugin (e.g., bitwarden-code-review)
  new-version    New semantic version (e.g., 1.3.4)

Examples:
  $0 bitwarden-code-review 1.3.4
  $0 claude-retrospective 2.0.0

This script updates:
  - .claude-plugin/marketplace.json
  - plugins/<plugin-name>/.claude-plugin/plugin.json
  - plugins/<plugin-name>/agents/*/AGENT.md (all agent files)

After running this script, remember to:
  1. Update plugins/<plugin-name>/CHANGELOG.md
  2. Commit all changes together
EOF
}

# Validate arguments
if [ $# -ne 2 ]; then
    print_error "Invalid number of arguments"
    usage
    exit 1
fi

PLUGIN_NAME="$1"
NEW_VERSION="$2"

# Validate plugin name (alphanumeric, hyphens, underscores)
if ! [[ "$PLUGIN_NAME" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    print_error "Plugin name must contain only alphanumeric characters, hyphens, and underscores"
    exit 1
fi

# Validate semantic version format (X.Y.Z)
if ! [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "Version must follow semantic versioning format (X.Y.Z)"
    print_info "Examples: 1.0.0, 1.3.4, 2.0.0"
    exit 1
fi

# Get repository root (script is in scripts/, root is parent)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Define file paths
MARKETPLACE_JSON="$REPO_ROOT/.claude-plugin/marketplace.json"
PLUGIN_JSON="$REPO_ROOT/plugins/$PLUGIN_NAME/.claude-plugin/plugin.json"
PLUGIN_DIR="$REPO_ROOT/plugins/$PLUGIN_NAME"

# Validate that plugin directory exists
if [ ! -d "$PLUGIN_DIR" ]; then
    print_error "Plugin directory not found: $PLUGIN_DIR"
    print_info "Available plugins:"
    ls -1 "$REPO_ROOT/plugins" 2>/dev/null | sed 's/^/  - /'
    exit 1
fi

# Validate that required files exist
if [ ! -f "$MARKETPLACE_JSON" ]; then
    print_error "Marketplace file not found: $MARKETPLACE_JSON"
    exit 1
fi

if [ ! -f "$PLUGIN_JSON" ]; then
    print_error "Plugin manifest not found: $PLUGIN_JSON"
    exit 1
fi

# Check for required commands
for cmd in jq sed; do
    if ! command -v "$cmd" &> /dev/null; then
        print_error "Required command '$cmd' not found. Please install it first."
        exit 1
    fi
done

# Get current versions for confirmation
CURRENT_MARKETPLACE_VERSION=$(jq -r ".plugins[] | select(.name == \"$PLUGIN_NAME\") | .version" "$MARKETPLACE_JSON")
CURRENT_PLUGIN_VERSION=$(jq -r '.version' "$PLUGIN_JSON")

if [ -z "$CURRENT_MARKETPLACE_VERSION" ] || [ "$CURRENT_MARKETPLACE_VERSION" = "null" ]; then
    print_error "Plugin '$PLUGIN_NAME' not found in marketplace.json"
    exit 1
fi

# Display what will be updated
print_info "Plugin: $PLUGIN_NAME"
print_info "Current version: $CURRENT_PLUGIN_VERSION"
print_info "New version: $NEW_VERSION"
echo ""

# Confirm with user
read -p "Proceed with version bump? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Version bump cancelled"
    exit 0
fi

# Update marketplace.json
print_info "Updating marketplace.json..."
if jq ".plugins |= map(if .name == \"$PLUGIN_NAME\" then .version = \"$NEW_VERSION\" else . end)" \
    "$MARKETPLACE_JSON" > "$MARKETPLACE_JSON.tmp"; then
    mv "$MARKETPLACE_JSON.tmp" "$MARKETPLACE_JSON"
    print_success "Updated marketplace.json"
else
    print_error "Failed to update marketplace.json"
    rm -f "$MARKETPLACE_JSON.tmp"
    exit 1
fi

# Update plugin.json
print_info "Updating plugin.json..."
if jq ".version = \"$NEW_VERSION\"" "$PLUGIN_JSON" > "$PLUGIN_JSON.tmp"; then
    mv "$PLUGIN_JSON.tmp" "$PLUGIN_JSON"
    print_success "Updated plugin.json"
else
    print_error "Failed to update plugin.json"
    rm -f "$PLUGIN_JSON.tmp"
    exit 1
fi

# Update all AGENT.md files
AGENT_DIR="$PLUGIN_DIR/agents"
if [ -d "$AGENT_DIR" ]; then
    print_info "Searching for agent files..."

    # Find all AGENT.md files
    AGENT_FILES=$(find "$AGENT_DIR" -type f -name "AGENT.md")

    if [ -n "$AGENT_FILES" ]; then
        AGENT_COUNT=0
        while IFS= read -r agent_file; do
            print_info "Updating $(basename "$(dirname "$agent_file")")/AGENT.md..."

            # Update version in YAML frontmatter
            # This handles the frontmatter between --- markers
            if sed -i.bak "/^---$/,/^---$/ s/^version: .*/version: $NEW_VERSION/" "$agent_file"; then
                rm -f "$agent_file.bak"
                print_success "Updated $agent_file"
                ((AGENT_COUNT++))
            else
                print_error "Failed to update $agent_file"
                rm -f "$agent_file.bak"
                exit 1
            fi
        done <<< "$AGENT_FILES"

        print_success "Updated $AGENT_COUNT agent file(s)"
    else
        print_info "No agent files found (this is okay if plugin has no agents)"
    fi
else
    print_info "No agents directory found (this is okay if plugin has no agents)"
fi

# Summary
echo ""
print_success "Version bump complete!"
echo ""
print_info "Files updated:"
print_info "  ✓ .claude-plugin/marketplace.json"
print_info "  ✓ plugins/$PLUGIN_NAME/.claude-plugin/plugin.json"
if [ -n "${AGENT_FILES:-}" ]; then
    print_info "  ✓ Agent AGENT.md files"
fi
echo ""
print_warning "Don't forget to:"
print_info "  1. Update plugins/$PLUGIN_NAME/CHANGELOG.md"
print_info "  2. Add changelog entry under appropriate category (Added, Changed, Fixed, Security, etc.)"
print_info "  3. Commit all changes together with your code changes"
echo ""
print_info "Example changelog entry:"
cat << EOF
  ## [$NEW_VERSION] - $(date +%Y-%m-%d)

  ### Changed
  - Your description here
EOF
