# `/code-review-local` - Local Code Review Command

## Overview

The `/code-review-local` slash command invokes the `bitwarden-code-reviewer` agent to perform comprehensive code reviews of GitHub pull requests, writing the review findings to **local files** instead of posting them to GitHub. This enables offline review workflows, preview capabilities before posting, and integration with custom review processes.

## Usage

```bash
/code-review-local [PR#] | [PR URL]
```

### Arguments

- **`[PR#]`** (optional): Pull request number (e.g., `123`)
- **`[PR URL]`** (optional): Full GitHub PR URL (e.g., `https://github.com/bitwarden/clients/pull/123`)
- **No arguments**: The command will ask you to provide a PR number or URL interactively

### Examples

```bash
# Review by PR number
/code-review-local 123

# Review by full URL
/code-review-local https://github.com/bitwarden/mobile/pull/4567

# Interactive mode (will prompt for PR info)
/code-review-local
```

## Output Files

The command generates two markdown files in your current working directory:

### 1. `review-summary.md`

Contains the overall summary comment that would be posted with `gh pr comment`.

**Format for PRs with issues:**
```markdown
**Overall Assessment:** REQUEST CHANGES

**Critical Issues**:
- [file:line] - [brief description]

See inline comments for details.
```

**Format for clean PRs:**
```markdown
**Overall Assessment:** APPROVE

[One neutral sentence describing what was reviewed]
```

### 2. `review-inline-comments.md`

Contains all inline review comments with file and line references that would be posted with `gh pr review --comment`.

**Format:**
```markdown
## [file-path]:[line-number]

[Emoji] **[SEVERITY]**: [One-line description]

<details>
<summary>Details and fix</summary>

[Full details, code examples, rationale]
</details>

---
```

**Note**: If no inline comments are needed (clean PR), this file will be empty or contain only the approval message.

## Review Severity Categories

The agent uses Bitwarden's standard emoji classification system:

- **❌ Critical**: Security vulnerabilities, data loss risks, breaking changes
- **⚠️ Important**: Bugs, incorrect logic, maintainability concerns
- **♻️ Refactoring**: Code quality improvements, technical debt
- **🎨 Style/Convention**: Formatting, naming, minor conventions
- **💭 Question/Discussion**: Clarifications, suggestions for discussion

## What the Command Does

1. **Fetches PR data** from GitHub using `gh pr view` and related commands
2. **Analyzes changes** following Bitwarden engineering standards
3. **Checks for repository-specific guidelines** (e.g., `.claude/prompts/review-code.md`)
4. **Applies standard review protocol**:
   - Reads existing comments to avoid duplicates
   - Assesses PR metadata and context
   - Evaluates code against security, correctness, and maintainability standards
5. **Generates structured review findings** with proper formatting
6. **Writes output to local files** (never posts to GitHub)

## Use Cases

### Preview Before Posting
Review the generated files before manually posting to GitHub:

```bash
/code-review-local 123
# Review the generated files
cat review-summary.md
cat review-inline-comments.md
# Manually post if satisfied
gh pr comment 123 --body-file review-summary.md
gh pr review 123 --comment --body-file review-inline-comments.md
```

### Offline Review Workflow
Perform code reviews without immediate GitHub access:

```bash
# Review while offline or in restricted environment
/code-review-local 456
# Later, post the reviews when ready
```

### Custom Review Integration
Integrate with custom tooling or approval processes:

```bash
# Generate review
/code-review-local 789
# Process with custom scripts
python process_review.py review-summary.md review-inline-comments.md
```

### Training and Learning
Use the output to understand code review best practices:

```bash
# Generate review to learn from the agent's analysis
/code-review-local 101
# Study the findings and reasoning
```

## Technical Details

- **Model**: Uses `sonnet` model for balanced performance and quality
- **Agent**: Invokes `bitwarden-code-reviewer` specialized agent
- **GitHub Access**: Read-only via `gh` CLI (requires authentication)
- **No Posting**: Deliberately does not post to GitHub-output is file-only

## Requirements

- GitHub CLI (`gh`) installed and authenticated
- Access to the target repository
- `bitwarden-code-review` plugin installed

## Related Documentation

- [Bitwarden Code Review Plugin README](../../README.md)
- [Bitwarden Code Reviewer Agent](../../agents/bitwarden-code-reviewer/AGENT.md)
- [Base Review Guidelines](../../.claude/prompts/base-review-guidelines.md)

## Troubleshooting

### "PR not found" error
- Verify the PR number or URL is correct
- Ensure you have access to the repository
- Check that `gh` CLI is authenticated: `gh auth status`

### Empty review files
- Verify the PR has actual changes to review
- Check that the PR is not already merged/closed
- Ensure repository-specific guidelines are accessible

### "Permission denied" errors
- Verify repository access permissions
- Re-authenticate with `gh auth login`
- Check that the repository allows code review access
