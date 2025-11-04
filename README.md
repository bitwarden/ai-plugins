# Bitwarden AI Plugin Marketplace

A curated collection of plugins and tools designed for AI-assisted development. This marketplace enables discovery and distribution of quality-controlled, well-maintained plugins for use with Claude Code and other AI development tools.

## Usage

### Prerequisites

This marketplace is hosted in a private GitHub repository and requires GitHub authentication to access.

#### Setting up GitHub Authentication for Claude Code

Choose one of the following authentication methods:

**Option 1: GitHub CLI (Recommended)**

1. Install GitHub CLI if not already installed:
   ```bash
   # macOS
   brew install gh

   # Windows
   winget install --id GitHub.cli

   # Linux
   # See https://github.com/cli/cli/blob/trunk/docs/install_linux.md
   ```

2. Authenticate with GitHub:
   ```bash
   gh auth login
   ```
   Follow the prompts to authenticate via browser or token.

**Option 2: Personal Access Token**

1. Generate a GitHub Personal Access Token (classic):
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Give it a descriptive name (e.g., "Claude Code Marketplace Access")
   - Select the `repo` scope (this grants access to private repositories)
   - Generate and copy the token

2. Configure Claude Code with your GitHub token:
   ```bash
   export GITHUB_TOKEN=your_token_here
   ```

   Or add it to your shell configuration file (~/.zshrc, ~/.bashrc, etc.) to persist across sessions:
   ```bash
   echo 'export GITHUB_TOKEN=your_token_here' >> ~/.zshrc
   source ~/.zshrc
   ```

### Adding this marketplace to Claude Code

You can add this marketplace using either the short form or full URL:

```bash
# Short form (GitHub owner/repo)
/plugin marketplace add bitwarden/ai-marketplace

# Full GitHub URL
/plugin marketplace add https://github.com/bitwarden/ai-marketplace
```

**Note:** After adding the marketplace, you will need to restart Claude Code for the changes to take effect.

**Tip:** You can also use `/plugin` interactively to manage marketplaces and plugins through a guided interface.

### Installing plugins from this marketplace

Once the marketplace is added, you can install plugins using:
```bash
/plugin install plugin-name@bitwarden-marketplace
```

Plugins are installed by default to `~/.claude/plugins/` on your local system.

**Note:** After installing a plugin, you will need to restart Claude Code for the plugin to become active.

## Contributing Plugins

To add a plugin to this marketplace:

1. Create your plugin following the [official Claude plugin structure](https://docs.claude.com/en/docs/claude-code/plugins-reference.md)
2. Place the plugin in the `plugins/` directory
3. Add an entry to `.claude-plugin/marketplace.json` in the `plugins` array:

```json
{
  "name": "your-plugin-name",
  "source": "./plugins/your-plugin-name",
  "description": "Brief description of your plugin",
  "version": "1.0.0",
  "author": {
    "name": "Your Name",
    "email": "your.email@bitwarden.com"
  },
  "keywords": ["keyword1", "keyword2"],
  "category": "utility"
}
```

## Plugin Structure

Each plugin should follow this structure:

```
plugins/your-plugin-name/
├── .claude-plugin/
│   └── plugin.json          (required manifest)
├── commands/                (slash commands - optional)
├── agents/                  (subagents - optional)
├── skills/                  (Agent Skills - optional)
├── hooks/                   (event handlers - optional)
└── .mcp.json               (MCP servers - optional)
```

## Plugin Requirements

All plugins contributed to this marketplace **must** include:

- **Comprehensive README documentation** - Clear description of capabilities, usage, and examples
- **Proper error handling and validation** - Plugins should fail gracefully with helpful error messages
- **Security best practices** - No credential exposure, input validation on all untrusted data
- **Test coverage** - Unit tests for core functionality and integration tests for external dependencies
- **Semantic versioning** - Follow [semver](https://semver.org/) format for version numbers
- **Claude Code compatibility** - Ensure plugins work reliably with Claude Code and similar AI development tools

## Code Quality Standards

To maintain consistency and quality across all plugins:

- Use `.editorconfig` settings for consistent formatting
- Validate spelling against `.cspell.json` and add domain-specific terms as needed
- Ensure all pre-commit hooks pass before submitting pull requests
- Provide clear, helpful error messages for users
- Follow existing patterns in the repository

## Security Considerations

This is a Bitwarden-maintained repository with high security standards. All plugins must adhere to:

- **Never commit credentials or API keys** - Use environment variables or secure configuration methods
- **Review all external dependencies for vulnerabilities** - Regularly audit and update dependencies
- **Follow principle of least privilege** - Request only necessary permissions and access
- **Validate all inputs as untrusted** - Never assume external input is safe
- **Fail safely and degrade gracefully** - Plugins should handle errors without compromising security

## Best Practices

When developing plugins, follow these best practices:

1. **Documentation First** - Write comprehensive documentation before implementation
2. **Security by Default** - Assume all inputs are untrusted and validate accordingly
3. **Fail Safely** - Plugins should degrade gracefully on errors rather than crash
4. **Version Compatibility** - Clearly document version requirements and compatibility
5. **Performance** - Consider performance implications for large-scale operations
6. **User Experience** - Provide clear error messages and helpful feedback

## Review Process

- All contributions require review from repository maintainers (see `.github/CODEOWNERS`)
- Automated checks validate code quality, security, and compliance
- Human reviewers provide feedback and approve merged changes
- Follow [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com) for all submissions

## Documentation

- [Claude Code Plugins Guide](https://docs.claude.com/en/docs/claude-code/plugins.md)
- [Plugin Reference](https://docs.claude.com/en/docs/claude-code/plugins-reference.md)
- [Plugin Marketplaces](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces.md)
