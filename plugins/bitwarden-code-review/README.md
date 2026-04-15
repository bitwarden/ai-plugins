# Bitwarden Code Review Plugin

Comprehensive AI-powered code review agent following Bitwarden engineering standards.

## Overview

This plugin provides an autonomous code review agent that conducts thorough, professional code reviews following Bitwarden's organizational standards. The agent focuses on security, correctness, and high-value feedback while maintaining a high signal-to-noise ratio.

## Features

- **Autonomous Review Agent**: Single agent handles all code review tasks without manual invocation
- **Organizational Standards**: Consistent review process, finding classification, and comment formatting across all repositories
- **Thread Detection**: Prevents duplicate comments by detecting existing threads before posting
- **Security-First Approach**: Prioritizes security vulnerabilities, data exposure, and authentication issues
- **Structured Thinking**: Uses explicit reasoning blocks to improve review quality and consistency
- **Confidence Scoring**: Pre-filters findings with a 0-100 confidence score (≥75 threshold) before validation to reduce false positives

## Architecture

### Code Review Agent

The plugin provides a single agent (`bitwarden-code-reviewer`) that follows a linear 7-step review process — from context gathering through validation to posting. See [`AGENT.md`](./agents/bitwarden-code-reviewer/AGENT.md) for the full flow.

### Skills

The agent leverages specialized skills:

- **`classifying-review-findings`**: Determines severity levels and validates finding criteria
- **`posting-bitwarden-review-comments`**: Formats inline PR comments following Bitwarden standards
- **`posting-review-summary`**: Posts or updates summary comments (handles sticky comment vs local file)
- **`avoiding-false-positives`**: Validates findings against framework patterns and conventions

### Finding Classification

See [`classifying-review-findings`](./skills/classifying-review-findings/SKILL.md) for the 5-tier severity system and classification criteria.

### Directory Structure

```
bitwarden-code-review/
├── .claude/
│   └── settings.json                         # Security boundaries
├── .claude-plugin/
│   └── plugin.json                           # Plugin metadata
├── agents/
│   └── bitwarden-code-reviewer/
│       └── AGENT.md                          # Main review agent
├── commands/
│   ├── code-review/                          # Code review command
│   └── code-review-local/                    # Local review command
├── skills/
│   ├── avoiding-false-positives/
│   │   └── SKILL.md                          # False positive prevention
│   ├── classifying-review-findings/
│   │   └── SKILL.md                          # Severity classification
│   ├── posting-bitwarden-review-comments/
│   │   └── SKILL.md                          # Inline comment formatting
│   └── posting-review-summary/
│       └── SKILL.md                          # Summary comment handling
├── tests/
│   └── TESTING.md                            # Test plan and validation
└── README.md                                 # This file
```

## Security

### Permission Boundaries

The plugin includes a `.claude/settings.json` file that defines security boundaries by explicitly denying dangerous GitHub operations.

### Recommended Project Configuration

When using this plugin in your repositories, **copy the security settings** to your project's `.claude/settings.json`. This ensures the code review agent cannot perform destructive operations in your project, following the **principle of least privilege**.

## Usage

### Automatic Invocation

The agent is automatically invoked by Claude when:

- User mentions "review", "PR", or "pull request"
- User requests code review feedback
- User analyzes code changes

### Manual Invocation

```bash
# Invoke the review agent explicitly
Use the bitwarden-code-reviewer agent to review this PR
```

### In GitHub Actions

See the production implementation: [bitwarden/gh-actions `_review-code.yml`](https://github.com/bitwarden/gh-actions/blob/main/.github/workflows/_review-code.yml)

## Installation

Available through Bitwarden's internal Claude Code marketplace:

```bash
# Add the Bitwarden marketplace (if not already added)
/plugin marketplace add https://github.com/bitwarden/ai-plugins

# Install the code review plugin
/plugin install bitwarden-code-review@bitwarden-marketplace

# Restart Claude Code
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on updating this plugin.

## License

Bitwarden

## Maintainers

- @team-ai-sme

## Support

For issues or questions:

- Internal: #ai-discussions Slack channel
- GitHub Issues: [bitwarden/ai-plugins](https://github.com/bitwarden/ai-plugins/issues)
