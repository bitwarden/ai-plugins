# Contributing to Bitwarden Init Plugin

Thank you for your interest in contributing to the Bitwarden Init plugin!

## Development

This plugin provides a `/bw-init` slash command for initializing Claude Code configuration with Bitwarden's standardized template format.

## Making Changes

1. Make your changes to the plugin files
2. Update the version number in `.claude-plugin/plugin.json`
3. Add an entry to `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/) format
4. Test the plugin locally before submitting

## Testing Locally

```bash
claude --plugin-dir /path/to/bitwarden-ai-plugins/plugins/bitwarden-init
```

## Pull Requests

See the main [CONTRIBUTING.md](../../CONTRIBUTING.md) for general contribution guidelines.
