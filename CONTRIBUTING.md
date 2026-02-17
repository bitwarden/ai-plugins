# Contributing to Bitwarden AI Plugins

This guide covers everything you need to create, modify, and submit plugins for the Bitwarden AI Plugin Marketplace.

For general Bitwarden contribution practices, see our [Contributing Guidelines](https://contributing.bitwarden.com/contributing/).

## Plugin Structure

Each plugin lives under `plugins/` and follows this layout:

```
plugins/your-plugin-name/
├── .claude-plugin/
│   └── plugin.json          (required manifest)
├── commands/                (slash commands - optional)
├── agents/                  (subagents - optional)
├── skills/                  (agent skills - optional)
├── hooks/                   (event handlers - optional)
├── CHANGELOG.md             (required)
├── README.md                (required)
└── .mcp.json               (MCP servers - optional)
```

For detailed guidance on building each component, see the [Plugin Reference](https://docs.claude.com/en/docs/claude-code/plugins-reference.md).

## Adding a New Plugin

1. Create your plugin directory under `plugins/`
2. Add an entry to `.claude-plugin/marketplace.json`:

```json
{
  "name": "your-plugin-name",
  "source": "./plugins/your-plugin-name",
  "description": "Brief description of your plugin",
  "version": "1.0.0"
}
```

3. Create your `.claude-plugin/plugin.json` manifest
4. Add a `README.md` and `CHANGELOG.md`
5. Add any domain-specific terms to `.cspell.json`
6. [Validate your plugin](#validating-changes) before submitting

## Plugin Requirements

All plugins must include:

- **Comprehensive README** - Clear description of capabilities, usage, and examples
- **Proper error handling** - Fail gracefully with helpful error messages
- **Security best practices** - No credential exposure, input validation on all untrusted data
- **Test coverage** - Unit tests for core functionality, integration tests for external dependencies
- **Semantic versioning** - Follow [semver](https://semver.org/) for all version numbers
- **Changelog** - Document all changes in [Keep a Changelog](https://keepachangelog.com/) format

## Versioning and Changelog

All plugin changes **must** include a version bump and changelog entry in the same PR.

### Determining the version bump

- **MAJOR (X.0.0)**: Breaking changes or incompatible modifications
- **MINOR (0.X.0)**: New features or backward-compatible additions
- **PATCH (0.0.X)**: Bug fixes, documentation updates, or security patches

### Using the version bump script

A helper script updates the version across all required files (marketplace.json, plugin.json, and agent frontmatter):

```bash
./scripts/bump-plugin-version.sh <plugin-name> <new-version>
```

### Updating the changelog

After bumping the version, add an entry to `plugins/<plugin-name>/CHANGELOG.md` under the appropriate category:

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security improvements

See [scripts/README.md](scripts/README.md) for full documentation on the version bump script and validation tooling.

## Validating Changes

Run the same checks that CI enforces before pushing:

```bash
# Validate plugin structure (required files, frontmatter, changelog format)
./scripts/validate-plugin-structure.sh <plugin-name>

# Validate marketplace.json (entries, version/name consistency)
./scripts/validate-marketplace.sh <plugin-name>
```

Both scripts accept a plugin name or `plugins/<name>` path. Omit arguments to validate all plugins. See [scripts/README.md](scripts/README.md) for details.

## Code Quality

- Use `.editorconfig` settings for consistent formatting
- Validate spelling against `.cspell.json` and add domain-specific terms as needed
- Ensure all pre-commit hooks pass before submitting
- Follow existing patterns in the repository

## Security

This is a Bitwarden-maintained repository with high security standards:

- **Never commit credentials or API keys** - Use environment variables or secure configuration
- **Review all external dependencies for vulnerabilities**
- **Follow principle of least privilege** - Request only necessary permissions
- **Validate all inputs as untrusted**
- **Fail safely** - Handle errors without compromising security

## Review Process

- All contributions require review from repository maintainers (see `.github/CODEOWNERS`)
- Automated checks validate structure, versioning consistency, and compliance
- Follow [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com) for all submissions
