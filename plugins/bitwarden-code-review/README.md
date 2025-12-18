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
3. **Classifies Findings**: Uses 5-tier severity system (CRITICAL, IMPORTANT, DEBT, SUGGESTED, QUESTION)
4. **Formats Output**: Posts inline comments and summary using mandatory templates

### Finding Classification

**Severity Levels** (most to least severe):

- ❌ **CRITICAL**: Code that will break, crash, expose data, or violate requirements (blocking)
- ⚠️ **IMPORTANT**: Missing error handling, edge cases, unclear behavior (should fix before merge)
- ♻️ **DEBT**: Code that duplicates patterns or violates conventions (technical debt)
- 🎨 **SUGGESTED**: Measurable improvements (complexity reduction 3+, eliminates bug classes)
- 💭 **QUESTION**: Questions about requirements or unclear intent

### Directory Structure

```
bitwarden-code-review/
├── .claude/
│   └── settings.json            # Security boundaries
├── .claude-plugin/
│   └── plugin.json              # Plugin metadata
├── agents/
│   └── bitwarden-code-reviewer/
│       └── AGENT.md             # Main review agent
├── commands/
│   └── code-review-local/       # Local review command
└── README.md                    # This file
```

### Thread Detection

The agent includes automatic duplicate comment prevention through direct GitHub API integration:

- **Implementation**: Agent autonomously constructs `gh pr` and `gh api` GraphQL queries based on execution context
- **Context Detection**: Automatically detects PR information from:
    - GitHub Actions environment variables (`GITHUB_EVENT_PATH`, `GITHUB_REPOSITORY`)
    - Slash command arguments or manual invocation
    - Gracefully skips detection for local reviews without PR context
- **Purpose**: Detects existing comment threads (including resolved ones) before creating new ones
- **Matching Logic**:
    - Exact match: Same file + same line number
    - Nearby match: Same file + line within ±5 lines
    - Content match: Existing comment body is similar (>70%)
- **Benefits**: Prevents duplicate comments, maintains conversation continuity, works universally across repository installations and invocation methods

## Security

### Permission Boundaries

The plugin includes a `.claude/settings.json` file that defines security boundaries by explicitly denying dangerous GitHub operations:

**Denied Operations:**

_Pull Request Modifications:_

- ❌ `gh pr merge/close/edit/lock/unlock/reopen/ready/checkout` - Cannot modify or checkout PRs

_Issue Modifications:_

- ❌ `gh issue create/close/reopen/edit/delete/lock/unlock/transfer/pin/unpin` - Cannot modify issues
- ✅ `gh issue view/list` - CAN read issues for context (not blocked)

_Repository Operations:_

- ❌ `gh repo edit/archive/delete/rename/sync/create/fork` - Cannot modify repository

_Release Operations:_

- ❌ `gh release` - Cannot create, modify, or delete releases

_Organization Operations:_

- ❌ `gh org` - Cannot modify org membership or settings

_Secrets and Workflows:_

- ❌ `gh secret` - Cannot access or modify repository secrets
- ❌ `gh workflow` - Cannot trigger or modify workflows

_CI/CD Operations:_

- ❌ `gh run rerun/cancel/delete/watch` - Cannot modify CI runs

_API Operations:_

- ❌ `gh api` DELETE/PATCH/PUT operations - Cannot modify or delete via API

**Allowed Operations:**

- ✅ Read PR metadata (`gh pr view`, `gh pr status`, `gh pr list`)
- ✅ Read code changes (`gh pr diff`, `git diff`)
- ✅ Read commit history (`git log`, `git show`)
- ✅ Read issues for context (`gh issue view`, `gh issue list`)
- ✅ View CI status (`gh pr checks`, `gh run view`, `gh run list`)
- ✅ Post review comments (`gh pr review`)
- ✅ Post summary comments (`gh pr comment`)
- ✅ Execute read-only GraphQL queries (`gh api graphql`)

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

```yaml
name: Code Review with Claude

on:
    pull_request:
        types: [opened, synchronize]

jobs:
    code-review:
        runs-on: ubuntu-latest
        steps:
            - uses: actions/checkout@v4

            - name: Run Code Review
              uses: anthropics/claude-code-action@v1
              with:
                  anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
                  github_token: ${{ secrets.GITHUB_TOKEN }}

                  # Add Bitwarden marketplace
                  plugin_marketplaces: |
                      https://github.com/bitwarden/ai-plugins.git

                  # Install code review plugin
                  plugins: |
                      bitwarden-code-review@bitwarden-marketplace

                  prompt: |
                      Review this pull request using the bitwarden-code-reviewer agent.
```

## Review Process

### Pre-Review Protocol

1. **Read Existing Context**
    - PR title and description
    - All existing comments and threads
    - Resolved threads and human responses
    - Identify initial review vs re-review

2. **Understand the Change**
    - Change type (bugfix, feature, refactor, dependency update)
    - Scope and impact analysis
    - Test alignment verification

3. **Assess PR Metadata**
    - Title clarity and specificity
    - Objective explanation
    - Screenshots/recordings for UI changes
    - JIRA reference in tracking section
    - Test plan documentation

### Review Execution

**Initial Review:**

- Complete analysis across security, correctness, breaking changes, performance, maintainability
- Follow priority order (security first)
- Verify completeness before posting

**Re-Review:**

- Review ONLY changed files/lines since last review
- Don't re-raise resolved issues
- Verify previous critical findings were fixed
- No new findings in unchanged code

### Output Format

**Inline Comments** (mandatory format):

```
❌ **CRITICAL**: SQL injection vulnerability in user query

<details>
<summary>Details and fix</summary>

Current code directly interpolates user input:
\`\`\`typescript
const query = `SELECT * FROM users WHERE email = '${email}'`;
\`\`\`

Use parameterized queries:
\`\`\`typescript
const query = 'SELECT * FROM users WHERE email = ?';
const result = await db.query(query, [email]);
\`\`\`

Direct string interpolation allows attackers to inject SQL commands, potentially exposing all user data.

Reference: OWASP SQL Injection Prevention
</details>
```

**Summary Comments**:

For PRs with issues:

```
**Overall Assessment:** REQUEST CHANGES

**Critical Issues**:
- src/auth.ts:45 - SQL injection vulnerability in user query

See inline comments for details.
```

For clean PRs:

```
**Overall Assessment:** APPROVE

Changes follow security best practices and include comprehensive test coverage.
```

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
