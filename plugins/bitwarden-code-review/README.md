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
│   ├── bitwarden-code-reviewer/
│   │   └── AGENT.md                          # Main review agent
│   └── pr-knowledge-extractor/
│       └── AGENT.md                          # Knowledge extraction agent
├── commands/
│   ├── advise-review/                        # Pre-review knowledge recall
│   ├── code-review/                          # Code review command
│   ├── code-review-local/                    # Local review command
│   └── retrospective-review/                 # Post-review knowledge capture
├── skills/
│   ├── avoiding-false-positives/             # False positive prevention
│   ├── classifying-review-findings/          # Severity classification
│   ├── detecting-existing-threads/           # Duplicate prevention
│   ├── posting-bitwarden-review-comments/    # Inline comment formatting
│   ├── posting-review-summary/               # Summary comment handling
│   ├── reviewing-incremental-changes/        # Re-review scoping
│   ├── capturing-review-knowledge/           # Knowledge capture workflow
│   ├── recalling-review-knowledge/           # Knowledge recall workflow
│   ├── bitwarden-server-review-knowledge/
│   ├── bitwarden-clients-review-knowledge/
│   ├── bitwarden-android-review-knowledge/
│   ├── bitwarden-ios-review-knowledge/
│   ├── bitwarden-ai-plugins-review-knowledge/
│   ├── bitwarden-sdk-internal-review-knowledge/
│   └── bitwarden-gh-actions-review-knowledge/
├── scripts/
│   └── get-review-threads.sh                 # GraphQL thread detection
├── tests/
│   └── TESTING.md                            # Test plan and validation
└── README.md                                 # This file
```

### Thread Detection

The agent prevents duplicate comments by detecting existing threads (including resolved ones) before posting. Matches by exact location, nearby lines (±5), and content similarity (>70%). See [skills/detecting-existing-threads/SKILL.md](./skills/detecting-existing-threads/SKILL.md) for implementation details.

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

## Code Review Institutional Knowledge

### Overview

The plugin includes a knowledge capture system that builds institutional memory from code reviews to prevent repeated mistakes and improve review quality.

**Skills**:
- `capturing-review-knowledge` - Document learnings from completed reviews
- `recalling-review-knowledge` - Retrieve past learnings before starting reviews

**Commands**:
- `/retrospective-review [PR#]` - Capture knowledge after completing code review
- `/advise-review` - Retrieve knowledge before starting code review

### Key Concepts

**Failed Detections**: Issues that were missed initially, caught late in review, or nearly overlooked. The most valuable type of knowledge.

**Repository Gotchas**: Architectural patterns, common mistakes, and technology-specific issues unique to a repository.

**Methodology Improvements**: Review strategies and techniques that proved effective or ineffective.

**Actionability Gate**: Only high-value learnings are captured to maintain signal-to-noise ratio.

### Usage Workflow

**Before a Code Review:**

```bash
/advise-review
```

Displays:
- Failed detections to watch for (issues caught late in past reviews)
- Repository-specific gotchas (architectural patterns and common mistakes)
- Effective review methodologies
- Knowledge freshness metadata

**For detailed usage**, see [recalling-review-knowledge skill documentation](skills/recalling-review-knowledge/README.md)

**After a Code Review:**

```bash
# After local review
/retrospective-review

# Or analyze specific PR
/retrospective-review 12345
```

The skill autonomously:
- Analyzes review comments for severity markers (❌ CRITICAL, ⚠️ IMPORTANT)
- Filters false positives (comments resolved without code changes)
- Extracts failed detections, repository patterns, and methodology insights
- Updates or creates SKILL file for the repository
- Presents extraction summary

**For detailed implementation**, see [capturing-review-knowledge skill documentation](skills/capturing-review-knowledge/README.md)

### Knowledge Storage

Per-repository knowledge is stored as SKILL files with YAML frontmatter:

```
skills/
├── {owner}-{repo}-review-knowledge/     # Per-repository knowledge
│   ├── SKILL.md                         # Unified knowledge file
│   └── references/
│       └── troubleshooting.md           # Error → Solution mappings
```

**Examples**:
- [skills/bitwarden-ai-plugins-review-knowledge/SKILL.md](skills/bitwarden-ai-plugins-review-knowledge/SKILL.md)
- [skills/bitwarden-server-review-knowledge/SKILL.md](skills/bitwarden-server-review-knowledge/SKILL.md)

### Best Practices

1. **Query before every review**: Run `/advise-review` to load context
2. **Capture immediately**: Run `/retrospective-review` right after review while fresh
3. **Review before committing**: Always check `git diff` before committing knowledge
4. **Share with team**: Push knowledge updates so everyone benefits
5. **Maintain quality**: Only capture actionable, high-value learnings

---

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
