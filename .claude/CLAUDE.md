# Bitwarden AI Plugins Marketplace - Claude Instructions

This file contains behavioral instructions for Claude when working in this repository. All user-facing documentation is in README.md.

## Core Behavioral Guidelines

### When Users Ask About Available Plugins

- Search repository for plugin directories under `plugins/`
- Read `.claude-plugin/marketplace.json` for plugin metadata
- Read individual plugin READMEs for detailed capabilities
- Present findings clearly and suggest relevant plugins based on user needs

### When Contributing New Plugins

- Always follow the plugin structure documented in README.md
- Create plugin directory under `plugins/`
- Add entry to `.claude-plugin/marketplace.json`
- Ensure plugin has its own `.claude-plugin/plugin.json` manifest
- Add domain-specific terms to `.cspell.json`

### When Modifying Existing Plugins

**CRITICAL**: All plugin changes MUST include a version bump and changelog entry.

When making ANY changes to a plugin (code, documentation, configuration, scripts, agents):

1. **Determine the semantic version bump**:
    - MAJOR (X.0.0): Breaking changes, incompatible API changes
    - MINOR (0.X.0): New features, backward-compatible additions
    - PATCH (0.0.X): Bug fixes, documentation updates, security patches

2. **Use the version bump script**:

    ```bash
    ./scripts/bump-plugin-version.sh <plugin-name> <new-version>
    ```

    This automatically updates all three required files:
    - `.claude-plugin/marketplace.json`
    - `plugins/<plugin-name>/.claude-plugin/plugin.json`
    - `plugins/<plugin-name>/agents/*/AGENT.md` (if agents exist)

3. **Add changelog entry**:
    - Update `plugins/<plugin-name>/CHANGELOG.md`
    - Use Keep a Changelog format
    - Document what changed and why
    - Place entry under appropriate category (Added, Changed, Fixed, Security, etc.)

4. **Include version bump in PR**:
    - Version bump and changelog changes must be part of the same PR as the code changes
    - This ensures version history is accurate and traceable

**Never commit plugin changes without updating the version and changelog.**

### Plugin Requirements Enforcement

Ensure all plugins include:

- Comprehensive README documentation
- Proper error handling and validation
- Security best practices (no credentials, input validation)
- Test coverage
- Semantic versioning

## Security Enforcement

This is a Bitwarden-maintained repository with high security standards. Enforce:

- **Never commit credentials or API keys**
- **Review all external dependencies for vulnerabilities**
- **Follow principle of least privilege**
- Validate all inputs as untrusted
- Ensure plugins fail safely and degrade gracefully

## Implementation Guidelines

### When Implementing Plugin Features

- Follow existing patterns in the repository
- Write comprehensive documentation before implementation
- Add detailed comments explaining complex logic
- Consider cross-platform compatibility (Windows, macOS, Linux)
- Consider performance implications for large-scale operations

### When Testing Plugins

- Write unit tests for core functionality
- Include integration tests for external dependencies
- Test error scenarios and edge cases
- Verify security controls work as intended

### Code Quality

- Use `.editorconfig` settings for consistent formatting
- Validate spelling against `.cspell.json`
- Ensure pre-commit hooks pass
- Provide clear, helpful error messages

## Resources

- Repository README: ./README.md
- Bitwarden Contributing Guidelines: https://contributing.bitwarden.com
