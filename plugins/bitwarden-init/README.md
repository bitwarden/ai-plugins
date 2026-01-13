# Bitwarden Init Plugin

Initialize Claude Code configuration with Bitwarden's standardized template format.

## Overview

This plugin provides a `/init` slash command that generates a CLAUDE.md file following Bitwarden's organizational standards. The command analyzes your codebase and creates comprehensive context documentation organized into six standardized sections.

## Installation

### From Bitwarden Marketplace

```bash
/plugin install bitwarden-init@bitwarden-marketplace
```

After installation, restart Claude Code to activate the plugin.

## Usage

### Initialize a Repository

Navigate to your repository in Claude Code and run:

```bash
/bitwarden-init:init
```

This will:
1. Analyze your codebase structure, languages, and patterns
2. Generate a CLAUDE.md file in the repository root
3. Organize content into Bitwarden's standardized template format

### Template Structure

The generated CLAUDE.md file includes these sections:

- **Overview**: Business domain, key concepts, user types, integration points
- **Architecture & Patterns**: Structure, module boundaries, design patterns, external services
- **Stack Best Practices**: Language idioms, framework patterns, error handling, testing
- **Anti-Patterns**: Common mistakes, security concerns, performance pitfalls
- **Data Models**: Domain entities, DTOs, validation rules, database patterns
- **Configuration, Security, and Authentication**: Environment management, secrets, auth flows, compliance

## Benefits

- **Standardization**: Consistent documentation format across all Bitwarden repositories
- **Onboarding**: New team members can quickly understand codebase patterns
- **AI Context**: Provides Claude with comprehensive project context for better assistance
- **Best Practices**: Captures organizational standards and conventions in one place

## Customization

After running `/bitwarden-init:init`, you can:
- Refine the generated content to add project-specific details
- Update sections as the codebase evolves
- Add additional context that Claude should know about your project

## Requirements

- Claude Code (latest version recommended)
- Repository with code to analyze

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines on contributing to this plugin.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## License

See [LICENSE.txt](../../LICENSE.txt) for licensing information.
