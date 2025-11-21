# Bitwarden Code Review Plugin

Comprehensive AI-powered code review agent following Bitwarden engineering standards with support for repository-specific customization.

## Overview

This plugin provides an autonomous code review agent that conducts thorough, professional code reviews following Bitwarden's organizational standards. The agent focuses on security, correctness, and high-value feedback while maintaining a high signal-to-noise ratio.

## Features

- **Autonomous Review Agent**: Single agent handles all code review tasks without manual invocation
- **Organizational Standards**: Consistent review process, finding classification, and comment formatting across all repositories
- **Repository-Specific Customization**: Teams can add technology-specific requirements without modifying the plugin
- **Thread Detection**: Prevents duplicate comments by detecting existing threads before posting
- **Security-First Approach**: Prioritizes security vulnerabilities, data exposure, and authentication issues
- **Structured Thinking**: Uses explicit reasoning blocks to improve review quality and consistency
- **Pattern Recognition**: Avoids false positives by recognizing framework conventions and intentional patterns
- **Comprehensive First Reviews**: Finds all critical issues in the first pass to avoid incremental feedback

## Architecture

### Code Review Agent

The plugin provides a single agent (`bitwarden-code-reviewer`) that:

1. **Reads PR Context**: Gathers PR metadata, existing comments, and resolved threads
2. **Loads Repository Guidelines**: Checks for `.claude/prompts/review-code.md` and integrates custom requirements
3. **Analyzes Changes**: Understands change scope and impact, then adapts review depth based on observed complexity and risk
4. **Classifies Findings**: Uses 5-tier severity system (CRITICAL, IMPORTANT, DEBT, SUGGESTED, QUESTION)
5. **Formats Output**: Posts inline comments and summary using mandatory templates

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

## Repository-Specific Customization

Repositories can provide **additional** review guidelines that supplement (but never override) the base organizational standards.

**Location**: `.claude/prompts/review-code.md` in the repository being reviewed

**Purpose**:
- Add technology stack-specific focus areas
- Define additional team coding conventions
- Specify extra repository-specific security checks
- Request focus on particular patterns
- Provide team context and preferences

**How It Works**:
1. Agent automatically checks for `.claude/prompts/review-code.md`
2. If found, reads and integrates guidelines with base standards
3. **Base guidelines always take precedence** - conflicts are resolved by ignoring conflicting repo directives
4. If not found, uses base guidelines only

**Important: Base Guidelines Cannot Be Overridden**

Repository guidelines are strictly **additive**. They can:
- ✅ Add new patterns to check
- ✅ Add technology-specific requirements
- ✅ Request additional focus areas
- ✅ Provide team context

Repository guidelines CANNOT:
- ❌ Weaken security requirements
- ❌ Change severity classifications
- ❌ Modify comment format requirements
- ❌ Override professional standards
- ❌ Skip mandatory checks

**Example Repository Guidelines**:

```markdown
# Repository-Specific Review Guidelines

## Technology Focus
- Heavily scrutinize React hook dependency arrays
- Validate all GraphQL queries use proper fragments
- Ensure all Suspense boundaries have error boundaries

## Additional Security Checks
- All authentication flows must include CSRF protection
- Flag any direct DOM manipulation for XSS review
- Verify all API calls use our axios wrapper (includes auth)

## Additional Code Conventions
- Flag TODO comments as technical debt
- Prefer named exports over default exports
- Component files must co-locate tests (ComponentName.test.tsx)

## Focus Areas
- Prioritize performance review in this performance-critical codebase
- Extra scrutiny on authentication and session management code
```

**Benefits**:
- No plugin modification needed for repo-specific needs
- Guidelines versioned with repository code
- Easy team collaboration on review standards
- Organizational standards remain enforced
- Teams can add requirements without weakening base standards

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

4. **Load Repository Guidelines**
   - Check for `.claude/prompts/review-code.md`
   - Integrate with base standards
   - Apply conflict resolution (base guidelines win)

### Review Execution

**Initial Review:**
- Complete analysis across security, correctness, breaking changes, performance, maintainability
- Follow priority order (security first)
- Stop after 3+ critical issues for fixes
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
