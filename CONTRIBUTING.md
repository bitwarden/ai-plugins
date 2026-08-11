# Contributing to Bitwarden AI Plugins

Every engineer who has solved a recurring problem, documented a pattern, or automated a workflow has something worth sharing. This marketplace is where those ideas become plugins that the whole team can use. This guide helps you figure out where your work fits, then walks through the mechanics of building and submitting it.

For general Bitwarden contribution practices, see our [Contributing Guidelines](https://contributing.bitwarden.com/contributing/).

## Where Does Your Claude Tooling Belong?

Plugins in this marketplace fall into three families. Repo-specific patterns usually belong closer to the code — see each repo's `.claude/CONTRIBUTING.md` for that. If your work is cross-repo and fits one of the families below, you're in the right place. If you're still unsure after reading them, raise a draft PR and maintainers will help find the right home.

### Persona Plugins

These encode how a specific engineering role works at Bitwarden — the conventions, review standards, and decision frameworks that generic AI doesn't know. They answer the question: _"How does a software engineer, security engineer, or DevOps engineer work **here**?"_

Personas map to the _work_, not the title — when you're designing a system you're doing architecture work, and the matching persona is for you. Most engineers will reach for more than one persona across a week because engineers wear many hats.

A persona plugin captures institutional knowledge that would otherwise live in someone's head or scattered across wiki pages. Persona plugins must clear three bars: the knowledge is institutional, domain-specific, and role-defining.

Example: `bitwarden-security-engineer`

### Tool Integration Plugins

These connect Claude Code to external services the team already uses, so Claude can read from and act on those tools. They answer the question: _"I want Claude to securely integrate to a service we use."_

If you find yourself context-switching between Claude Code and another tool to copy information back and forth, a tool integration plugin can bridge that gap.

Example: `bitwarden-atlassian-tools`

### Utility Plugins

These improve the Claude Code development experience itself — setup, configuration, workflow analysis. They help every engineer regardless of role or domain. They answer the question: _"How can working with Claude Code be better for everyone?"_

Examples: `bitwarden-init`

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

For detailed guidance on building each component, see the [Plugin Reference](https://code.claude.com/docs/en/plugins-reference).

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

### Bumping the version

Update the version in every place it appears:

- the plugin's `.claude-plugin/plugin.json`,
- its entry in the root `.claude-plugin/marketplace.json`,
- the plugin catalog table in the root `README.md`,
- any agent frontmatter (`AGENT.md`), if the plugin has agents.

A helper script that updates all of these at once (`bump-plugin-version.sh`) lives in [`bitwarden/gh-actions`](https://github.com/bitwarden/gh-actions/tree/main/validate-ai/scripts). Run it from a checkout of that repository. The script defaults `REPO_ROOT` to the parent of its own `scripts/` directory, which inside a gh-actions checkout is `validate-ai/` — so you must set `REPO_ROOT` to this repository or it will look for plugins in gh-actions and fail with "Plugin directory not found":

```bash
REPO_ROOT=/path/to/ai-plugins validate-ai/scripts/bump-plugin-version.sh <plugin-name> <new-version>
```

### Updating the changelog

After bumping the version, add an entry to `plugins/<plugin-name>/CHANGELOG.md` under the appropriate category:

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security improvements

See the [validate-ai scripts README](https://github.com/bitwarden/gh-actions/tree/main/validate-ai/scripts) for full documentation on the version bump script and validation tooling.

## Validating Changes

Plugin structure, marketplace consistency, and version-bump checks come from validation scripts (`validate-plugin-structure.sh`, `validate-marketplace.sh`) in [`bitwarden/gh-actions`](https://github.com/bitwarden/gh-actions/tree/main/validate-ai) under `validate-ai/scripts/`.

To run them locally before pushing, invoke them from a checkout of that repository with `REPO_ROOT` pointed at this one. Each script defaults `REPO_ROOT` to the parent of its own `scripts/` directory — `validate-ai/` inside a gh-actions checkout — so without the override it inspects gh-actions instead of this repository and fails on a path that isn't there (`validate-plugin-structure.sh` reports "Plugins directory not found", `validate-marketplace.sh` reports "marketplace.json not found at"). Each script accepts a plugin name or `plugins/<name>` path, and validates all plugins when given no arguments:

```bash
REPO_ROOT=/path/to/ai-plugins validate-ai/scripts/validate-plugin-structure.sh bitwarden-code-review
REPO_ROOT=/path/to/ai-plugins validate-ai/scripts/validate-marketplace.sh
```

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
