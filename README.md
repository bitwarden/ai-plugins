# Bitwarden AI Plugin Marketplace

A curated collection of plugins for AI-assisted development at Bitwarden. Enables discovery and distribution of quality-controlled plugins for use with Claude Code.

## Available Plugins

| Plugin                                                              | Version | Description                                                                                        |
| ------------------------------------------------------------------- | ------- | -------------------------------------------------------------------------------------------------- |
| [atlassian-reader](plugins/atlassian-reader/)                       | 1.2.0   | Read-only access to Jira issues, epics, sprints, boards, and Confluence pages from Atlassian Cloud |
| [bitwarden-atlassian-tools](plugins/bitwarden-atlassian-tools/)     | 1.1.0   | Read-only Atlassian access: Jira issues, JQL search, Confluence pages, CQL search, attachments    |
| [bitwarden-code-review](plugins/bitwarden-code-review/)             | 1.8.0   | Autonomous code review agent following Bitwarden engineering standards with GitHub integration     |
| [bitwarden-init](plugins/bitwarden-init/)                           | 1.1.0   | Initialize and enhance CLAUDE.md files with Bitwarden's standardized template format               |
| [bitwarden-security-engineer](plugins/bitwarden-security-engineer/) | 0.2.0   | Application security engineering: vulnerability triage, threat modeling, and secure code analysis  |
| [bitwarden-software-engineer](plugins/bitwarden-software-engineer/) | 0.3.0   | Full-stack engineering assistant for Bitwarden client, server, and database development patterns   |
| [claude-config-validator](plugins/claude-config-validator/)         | 1.1.0   | Validates Claude Code configuration files for security, structure, and quality                     |
| [claude-retrospective](plugins/claude-retrospective/)               | 1.1.0   | Analyze Claude Code sessions to identify successful patterns and improvement opportunities         |

## Usage

### Adding this marketplace to Claude Code

```bash
# Short form (GitHub owner/repo)
/plugin marketplace add bitwarden/ai-plugins

# Full GitHub URL
/plugin marketplace add https://github.com/bitwarden/ai-plugins
```

After adding the marketplace, restart Claude Code for the changes to take effect.

You can also use `/plugin` interactively to manage marketplaces and plugins through a guided interface.

### Installing plugins

Once the marketplace is added, install plugins using:

```bash
/plugin install plugin-name@bitwarden-marketplace
```

Plugins are installed to `~/.claude/plugins/` by default. Restart Claude Code after installing for the plugin to become active.

### Keeping plugins up to date

Third-party marketplaces don't auto-update by default. To enable automatic updates, open `/plugin`, go to **Marketplaces**, select this marketplace, and choose **Enable auto-update**. Claude Code will then refresh marketplace data and update installed plugins at startup.

You can also update manually at any time:

```bash
/plugin marketplace update bitwarden-marketplace
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for plugin development guidelines, structure requirements, versioning rules, and the review process.

## Documentation

- [Claude Code Plugins Guide](https://docs.claude.com/en/docs/claude-code/plugins.md)
- [Plugin Reference](https://docs.claude.com/en/docs/claude-code/plugins-reference.md)
- [Plugin Marketplaces](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces.md)
- [Validation Scripts](scripts/README.md)
