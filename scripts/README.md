# Scripts

Utility scripts for maintaining the Bitwarden AI Plugins Marketplace.

## bump-plugin-version.sh

Automates version bumping across all required plugin files.

### Usage

```bash
./scripts/bump-plugin-version.sh <plugin-name> <new-version>
```

### Examples

```bash
# Bump patch version for a bug fix
./scripts/bump-plugin-version.sh bitwarden-code-review 1.3.4

# Bump minor version for new features
./scripts/bump-plugin-version.sh claude-retrospective 1.1.0

# Bump major version for breaking changes
./scripts/bump-plugin-version.sh claude-config-validator 2.0.0
```

### What It Does

The script automatically updates version numbers in:

1. **`.claude-plugin/marketplace.json`** - Marketplace registration
2. **`plugins/<plugin-name>/.claude-plugin/plugin.json`** - Plugin manifest
3. **`plugins/<plugin-name>/agents/*/AGENT.md`** - All agent YAML frontmatter (if agents exist)

### Features

- **Input validation**: Ensures plugin name and version format are valid
- **Existence checks**: Verifies plugin and files exist before making changes
- **Confirmation prompt**: Asks for confirmation before applying changes
- **Colored output**: Clear visual feedback with success/error indicators
- **Agent detection**: Automatically finds and updates all agent files
- **Helpful reminders**: Reminds you to update changelog after version bump

### After Running

After a successful version bump, you **must**:

1. Update `plugins/<plugin-name>/CHANGELOG.md` with an entry for the new version
2. Follow [Keep a Changelog](https://keepachangelog.com/) format
3. Commit all changes together in the same PR

### Requirements

- `jq` - JSON processor (install with `brew install jq` on macOS)
- `sed` - Stream editor (usually pre-installed)
- `bash` 4.0 or higher

### Error Handling

The script validates:

- Plugin name format (alphanumeric, hyphens, underscores only)
- Semantic version format (must be X.Y.Z)
- Plugin directory existence
- Required file existence
- JSON syntax after updates

If any validation fails, the script exits with an error message and no changes are made.
