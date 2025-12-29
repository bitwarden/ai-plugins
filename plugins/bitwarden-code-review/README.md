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
- **Pattern Recognition**: Avoids false positives by recognizing framework conventions and intentional patterns
- **Comprehensive First Reviews**: Finds all critical issues in the first pass to avoid incremental feedback

## Architecture

### Code Review Agent

The plugin provides a single agent (`bitwarden-code-reviewer`) that:

1. **Reads PR Context**: Gathers PR metadata, existing comments, and resolved threads
2. **Analyzes Changes**: Understands change scope and impact, then adapts review depth based on observed complexity and risk
3. **Classifies Findings**: Invokes `classifying-review-findings` skill to categorize issues using a 5-tier severity system
4. **Formats Output**: Invokes `posting-bitwarden-review-comments` skill to format and post inline comments and summaries

### Skills

The agent leverages specialized skills:

- **`classifying-review-findings`**: Determines severity levels and validates finding criteria
- **`posting-bitwarden-review-comments`**: Formats inline PR comments following Bitwarden standards
- **`posting-review-summary`**: Posts or updates summary comments (handles sticky comment vs local file)
- **`detecting-existing-threads`**: Prevents duplicate comments by detecting existing threads
- **`reviewing-incremental-changes`**: Scopes re-reviews to only new changes
- **`avoiding-false-positives`**: Validates findings against framework patterns and conventions

### Finding Classification

**Severity Levels** (most to least severe):

- ❌ **CRITICAL**: Code that will break, crash, expose data, or violate requirements (blocking)
- ⚠️ **IMPORTANT**: Missing error handling, edge cases, unclear behavior (should fix before merge)
- ♻️ **DEBT**: Code that duplicates patterns or violates conventions (technical debt)
- 🎨 **SUGGESTED**: Measurable improvements (complexity reduction 3+, eliminates bug classes)
- ❓ **QUESTION**: Questions about requirements or unclear intent

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
│   └── code-review-local/                    # Local review command
├── skills/
│   ├── avoiding-false-positives/
│   │   └── SKILL.md                          # False positive prevention
│   ├── classifying-review-findings/
│   │   └── SKILL.md                          # Severity classification
│   ├── detecting-existing-threads/
│   │   └── SKILL.md                          # Duplicate prevention
│   ├── posting-bitwarden-review-comments/
│   │   └── SKILL.md                          # Inline comment formatting
│   ├── posting-review-summary/
│   │   └── SKILL.md                          # Summary comment handling
│   └── reviewing-incremental-changes/
│       └── SKILL.md                          # Re-review scoping
├── tests/
│   └── TESTING.md                            # Test plan and validation
└── README.md                                 # This file
```

### Thread Detection

The agent prevents duplicate comments by detecting existing threads (including resolved ones) before posting. Matches by exact location, nearby lines (±5), and content similarity (>70%). See [agents/bitwarden-code-reviewer/AGENT.md](./agents/bitwarden-code-reviewer/AGENT.md) for implementation details.

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

## Review Process

The agent follows a structured review process:

1. **Pre-Review**: Reads PR context, existing comments, and resolved threads
2. **Skill Loading**: Invokes `classifying-review-findings` and `posting-bitwarden-review-comments` skills
3. **Analysis**: Reviews security, correctness, breaking changes, performance, and maintainability
4. **Classification**: Categorizes findings using the 5-tier severity system
5. **Output**: Formats and posts inline comments and summary

For detailed process documentation, see [agents/bitwarden-code-reviewer/AGENT.md](./agents/bitwarden-code-reviewer/AGENT.md).

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
