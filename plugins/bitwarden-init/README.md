# Bitwarden Init Plugin

Generates CLAUDE.md files using Bitwarden's standardized documentation template.

## What It Does

This plugin creates comprehensive CLAUDE.md files that document your codebase. It works in two phases:

1. **Phase 1**: Runs Anthropic's built-in `/init` to analyze your codebase and generate initial documentation
2. **Phase 2**: Extends the output with Bitwarden's template structure, adding standardized sections

## Installation

```bash
/plugin install bitwarden-init@bitwarden-marketplace
```

Restart Claude Code after installation.

## Commands

### `/bitwarden-init:init`

Generates a new CLAUDE.md file. Runs both phases automatically:
1. Anthropic's `/init` analyzes the codebase
2. `/enhance` restructures and extends the output

### `/bitwarden-init:enhance`

Enhances an existing CLAUDE.md file. Reads your current file, performs additional codebase research, and reorganizes content to match Bitwarden's template sections.

## Template Structure

The generated CLAUDE.md includes these sections:

- **Overview** - Project purpose, key concepts
- **Architecture & Patterns** - System diagrams, code organization, implementation patterns
- **Development Guide** - Step-by-step instructions with code templates
- **Data Models** - Types, validation schemas, domain entities
- **Security & Configuration** - Security rules, authentication, environment variables
- **Testing** - Test structure, writing tests, running tests
- **Code Style & Standards** - Formatting, naming conventions, pre-commit hooks
- **Anti-Patterns** - DO/DON'T lists
- **Deployment** - Build and deployment instructions
- **Troubleshooting** - Common issues and solutions
- **References** - Documentation links

## Requirements

- `claude` CLI in PATH
- Write permissions for CLAUDE.md

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

See [LICENSE.txt](../../LICENSE.txt).
