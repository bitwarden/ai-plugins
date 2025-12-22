# Scripts

Utility scripts for maintaining the Bitwarden AI Plugins Marketplace.

## Table of Contents

- [bump-plugin-version.sh](#bump-plugin-versionsh) - Automate version bumping
- [validate-plugin-structure.sh](#validate-plugin-structuresh) - Validate plugin structure
- [validate-marketplace.sh](#validate-marketplacesh) - Validate marketplace.json
- [GitHub Actions Integration](#github-actions-integration)
- [Local Development Workflow](#local-development-workflow)

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

---

## validate-plugin-structure.sh

Validates the structure and content of individual plugins.

### Usage

```bash
bash scripts/validate-plugin-structure.sh
# or
./scripts/validate-plugin-structure.sh
```

### Checks Performed

- **Plugin directory structure** - Verifies required directories exist
- **Required files** - Checks for:
  - `.claude-plugin/plugin.json` - Plugin manifest
  - `README.md` - Plugin documentation
  - `CHANGELOG.md` - Version history
- **Optional directories** - Validates `commands/`, `agents/`, `skills/`, `hooks/`
- **Agent definitions** - Ensures each agent has `AGENT.md` with valid YAML frontmatter
- **Skill definitions** - Ensures each skill has `SKILL.md` with valid YAML frontmatter
- **Command definitions** - Checks for `.md` files in command directories
- **README content** - Warns if missing key sections (description, usage, installation)
- **CHANGELOG format** - Warns if not following Keep a Changelog format

### Output

The script provides colored output:

- 🔍 Blue headers for sections
- ✅ Green for successful validations
- ❌ Red for errors (will fail the check)
- ⚠️ Yellow for warnings (won't fail the check)

### Exit Codes

- `0` - All validations passed
- `1` - One or more validations failed

### Example Output

```
🔍 Validating plugin structure...

📦 Validating bitwarden-code-review...
  ✅ Structure is valid

📦 Validating claude-config-validator...
  ❌ Missing required file: CHANGELOG.md
  ⚠️ CHANGELOG.md does not exist

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Validation Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total plugins checked: 2
Total errors: 1
Total warnings: 1

❌ Plugin validation failed
```

---

## validate-marketplace.sh

Validates the `marketplace.json` file and checks consistency with actual plugins.

### Usage

```bash
bash scripts/validate-marketplace.sh
# or
./scripts/validate-marketplace.sh
```

### Checks Performed

- **Marketplace structure** - Validates required fields:
  - `name` - Marketplace identifier
  - `owner` - Owner information (must have `name` field)
  - `plugins` - Array of plugin entries
- **Plugin entries** - Checks each plugin has:
  - `name` - Plugin identifier
  - `source` - Path to plugin directory
  - `description` - Plugin description
  - `version` - Semantic version (X.Y.Z)
- **Plugin existence** - Verifies plugin directories actually exist
- **Version consistency** - Ensures versions match between:
  - `marketplace.json`
  - `plugin.json` files
- **Name consistency** - Ensures names match in marketplace and plugin manifests
- **Completeness** - Warns if plugins exist but aren't listed in marketplace

### Output

The script provides colored output:

- 🔍 Blue headers for sections
- ✅ Green for successful validations
- ❌ Red for errors

### Exit Codes

- `0` - All validations passed
- `1` - One or more validations failed

### Example Output

```
🔍 Validating marketplace.json...

📋 Checking marketplace structure...
  ✅ Structure is valid

📦 Checking plugin entries...
  ✅ claude-retrospective
  ✅ claude-config-validator
  ✅ bitwarden-code-review

🔄 Checking consistency with plugin files...
  ✅ All plugins are consistent

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Validation Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total plugins in marketplace: 3
Total errors found: 0

✅ marketplace.json is valid
```

---

## Plugin Requirements Reference

### Required Files

Every plugin must include:

1. **`.claude-plugin/plugin.json`** - Plugin manifest with:

   ```json
   {
     "name": "plugin-name",
     "version": "X.Y.Z",
     "description": "Plugin description",
     "author": {
       "name": "Author Name"
     }
   }
   ```

2. **`README.md`** - Documentation including:
   - Description/overview
   - Usage examples
   - Installation instructions

3. **`CHANGELOG.md`** - Version history following [Keep a Changelog](https://keepachangelog.com/) format

### Version Format

All versions must follow semantic versioning:

- Format: `MAJOR.MINOR.PATCH` (e.g., `1.0.0`, `2.3.4`)
- Numbers only (no 'v' prefix)
- Must be consistent across all files

See [Semantic Versioning](https://semver.org/) for guidelines:

- **MAJOR** - Breaking changes
- **MINOR** - New features, backward-compatible
- **PATCH** - Bug fixes, documentation updates

### Agent Requirements

If your plugin includes agents, each `AGENT.md` must have valid YAML frontmatter:

```yaml
---
name: agent-name
description: Agent description
version: X.Y.Z
tools:
  - tool1
  - tool2
---
```

### Skill Requirements

If your plugin includes skills, each `SKILL.md` must have valid YAML frontmatter:

```yaml
---
name: skill-name
description: Skill description
---
```

### Security Requirements

- ❌ No hardcoded credentials or API keys
- ❌ No committed `.env` files
- ✅ Proper input validation in scripts
- ✅ Use environment variables for sensitive data

---

## Troubleshooting

### Common Issues

**"Missing required file: plugin.json"**

- Ensure `.claude-plugin/plugin.json` exists in your plugin directory
- Check the file path matches the expected structure

**"Invalid version format"**

- Use semantic versioning: `1.0.0` not `v1.0` or `1.0`
- No prefixes or suffixes allowed

**"Version mismatch"**

- Ensure versions match in:
  - `plugin.json`
  - `marketplace.json`
  - `AGENT.md` files (if agents exist)
- Use the version bump script: `./scripts/bump-plugin-version.sh plugin-name X.Y.Z`

**"Missing YAML frontmatter"**

- Ensure files start with `---` and end with `---`
- Include all required fields
- Validate YAML syntax at [YAML Lint](https://www.yamllint.com/)

**"Invalid JSON"**

- Validate JSON syntax using `jq`:
  ```bash
  jq empty your-file.json
  ```
- Or use an online validator like [JSONLint](https://jsonlint.com/)

**"Plugin exists but not in marketplace"**

- Add an entry to `.claude-plugin/marketplace.json`
- Ensure the `source` path is correct

---

## Resources

### Official Documentation

- [Claude Code Plugins Reference](https://docs.claude.com/en/docs/claude-code/plugins-reference) - Official plugin API reference
- [Plugin Marketplaces](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces) - Marketplace structure
- [Plugin Structure](https://claude-plugins.dev/skills/@anthropics/claude-code/plugin-structure) - Plugin organization

### Standards & Best Practices

- [Keep a Changelog](https://keepachangelog.com/) - Changelog format
- [Semantic Versioning](https://semver.org/) - Version numbering
- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com) - Contribution standards

### Best Practices from Research

Based on research into Claude Code plugin validation and best practices:

1. **Automated validation** - Run lints and tests that gate every change; CI runs should be non-destructive first ([Claude Code Plugin Best Practices](https://skywork.ai/blog/claude-code-plugin-best-practices-large-codebases-2025/))

2. **Hooks for quality checks** - Automate type checks, security validation, and code formatting using hooks ([Claude Code: Part 8 - Hooks](https://www.letanure.dev/blog/2025-08-06--claude-code-part-8-hooks-automated-quality-checks))

3. **Security scanning** - Scan generated code for vulnerabilities and validate against security policies ([Claude Desktop Developer Best Practices](https://skywork.ai/blog/ai-agent/claude-desktop-developer-best-practices-automation-plugins-2025/))

4. **Progressive constraints** - Start in read-only mode; allow writes only after tests pass ([Claude Code 2.0 Best Practices](https://skywork.ai/blog/claude-code-2-0-best-practices-ai-coding-workflow-2025/))

5. **Schema validation** - Validate against official marketplace schema at https://anthropic.com/claude-code/marketplace.schema.json ([Plugin marketplaces](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces))

---

## Contributing

When modifying validation scripts:

1. Test locally before committing
2. Document any new validation checks in this README
3. Update workflow file if adding new checks
4. Follow existing patterns for consistency
5. Consider backwards compatibility

For questions or issues, refer to the main [repository README](../README.md) or contact the maintainers.
