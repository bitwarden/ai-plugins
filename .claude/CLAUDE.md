# Bitwarden AI Plugins Marketplace - Claude Instructions

This file contains behavioral instructions for Claude when working in this repository. All user-facing documentation is in README.md.

## Core Behavioral Guidelines

### When Users Ask About Available Plugins

- Search repository for plugin directories under `plugins/`
- Read `.claude-plugin/marketplace.json` for plugin metadata
- Read individual plugin READMEs for detailed capabilities
- Present findings clearly and suggest relevant plugins based on user needs

### When Contributing New Plugins

Use the `/plugin-dev:create-plugin` command for guided end-to-end plugin creation. It walks through discovery, planning, structure creation, implementation, validation, testing, and documentation.

When building individual components, use the plugin-dev skills for best-practice guidance:

- **Plugin structure**: Use the `plugin-dev:plugin-structure` skill for directory layout, manifest configuration, and auto-discovery setup
- **Agents**: Use the `plugin-dev:agent-development` skill for AGENT.md frontmatter, triggering descriptions, system prompts, and tool selection
- **Skills**: Use the `plugin-dev:skill-development` skill for SKILL.md structure, progressive disclosure, and description quality
- **Commands**: Use the `plugin-dev:command-development` skill for slash command frontmatter, arguments, and user interaction patterns
- **Hooks**: Use the `plugin-dev:hook-development` skill for event-driven automation, prompt-based hooks, and `${CLAUDE_PLUGIN_ROOT}` usage
- **MCP servers**: Use the `plugin-dev:mcp-integration` skill for Model Context Protocol server configuration and security
- **Settings**: Use the `plugin-dev:plugin-settings` skill for `.local.md` configuration patterns

After creating a plugin, always:

- Create plugin directory under `plugins/`
- Add entry to `.claude-plugin/marketplace.json`
- Ensure plugin has its own `.claude-plugin/plugin.json` manifest
- Add domain-specific terms to `.cspell.json`
- Run validation (see below)

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

### Validating Plugin Changes

After making any plugin changes, run the same validations that CI enforces. This catches issues before pushing.

#### 1. Run the validation scripts

These are fast, local, and require no special environment:

```bash
# Validate plugin structure (required files, plugin.json fields, frontmatter, changelog format)
./scripts/validate-plugin-structure.sh <plugin-name>

# Validate marketplace.json (entries, version/name consistency across files)
./scripts/validate-marketplace.sh <plugin-name>
```

Both scripts accept either a plugin name or a `plugins/<name>` path. Omit arguments to validate all plugins.

#### 2. Run the plugin-dev validator agent

Use the **plugin-validator** agent from `plugin-dev` for deeper structural and component checks:

- plugin.json manifest correctness and semantic versioning
- Agent AGENT.md frontmatter (name, description with `<example>` blocks, valid model/color)
- Skill SKILL.md frontmatter and required fields
- Hook JSON schema, event names, and `${CLAUDE_PLUGIN_ROOT}` usage
- MCP server configurations (valid types, HTTPS/WSS enforcement)
- No hardcoded credentials in any plugin files

Simply mention "validate my plugin" or "check plugin structure" and the plugin-validator agent will be triggered.

#### 3. Review skills with the skill-reviewer agent

When SKILL.md files are added or changed, use the **skill-reviewer** agent from `plugin-dev`:

- Description quality and trigger phrase specificity
- Content length (target 1,000-3,000 words) and writing style
- Progressive disclosure (core SKILL.md is lean, details in `references/`, examples in `examples/`)
- All referenced files actually exist

Simply mention "review my skill" or "check skill quality" to trigger it.

#### 4. Run security validation

Use the **reviewing-claude-config** skill from `claude-config-validator` to scan for:

- Committed secrets (API keys, tokens, passwords)
- Hardcoded credentials in code
- Permission scoping issues in settings files
- Dangerous command auto-approvals
- Overly broad file access permissions

This skill also validates CLAUDE.md files, agent configs, and command/prompt files for structure and quality.

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
- Validation scripts: ./scripts/README.md
- Plugin development guide: https://docs.claude.com/en/docs/claude-code/plugins-reference
- Bitwarden Contributing Guidelines: https://contributing.bitwarden.com
