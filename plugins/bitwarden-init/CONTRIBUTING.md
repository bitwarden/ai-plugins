# Contributing to Bitwarden Init Plugin

Thank you for your interest in contributing to the Bitwarden Init plugin!

## Development

This plugin provides two slash commands for generating and enhancing CLAUDE.md files with Bitwarden's standardized template:

- `/bitwarden-init:init` - Generates a new CLAUDE.md file (runs both phases automatically)
- `/bitwarden-init:enhance` - Enhances an existing CLAUDE.md file with Bitwarden's template structure

## Making Changes

When making ANY changes to the plugin (code, documentation, configuration, scripts, agents):

1. **Determine the semantic version bump**:
   - MAJOR (X.0.0): Breaking changes, incompatible API changes
   - MINOR (0.X.0): New features, backward-compatible additions
   - PATCH (0.0.X): Bug fixes, documentation updates, security patches

2. **Use the version bump script** from the repository root:
   ```bash
   ./scripts/bump-plugin-version.sh bitwarden-init <new-version>
   ```
   This automatically updates all required files including `.claude-plugin/plugin.json`

3. **Add an entry to `CHANGELOG.md`** following [Keep a Changelog](https://keepachangelog.com/) format

4. Test the plugin locally before submitting

## Testing Locally

```bash
claude --plugin-dir /path/to/bitwarden-ai-plugins/plugins/bitwarden-init
```

Test both commands:
- `/bitwarden-init:init` - Verify it runs both phases and generates a complete CLAUDE.md
- `/bitwarden-init:enhance` - Verify it enhances an existing CLAUDE.md with the template structure

## Pull Requests

- Version bump and changelog changes must be part of the same PR as code changes
- See the main [CONTRIBUTING.md](../../CONTRIBUTING.md) for general contribution guidelines
