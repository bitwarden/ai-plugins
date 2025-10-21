# Bitwarden AI Plugin Marketplace

Plugins and other tools for AI-assisted development.

## Usage

### Adding this marketplace to Claude Code

```bash
/plugin marketplace add bitwarden/ai-marketplace
```

### Installing plugins from this marketplace

Once the marketplace is added, you can install plugins using:
```bash
/plugin install plugin-name@bitwarden-marketplace
```

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

## Documentation

- [Claude Code Plugins Guide](https://docs.claude.com/en/docs/claude-code/plugins.md)
- [Plugin Reference](https://docs.claude.com/en/docs/claude-code/plugins-reference.md)
- [Plugin Marketplaces](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces.md)
