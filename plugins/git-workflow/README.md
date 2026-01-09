# Git Workflow Plugin

A Claude Code plugin that provides a streamlined, automated git workflow for committing changes, pushing to remote, and creating pull requests with intelligently generated messages.

## Overview

The Git Workflow plugin simplifies the development workflow by automating repetitive git operations into a single command. It analyzes your code changes to generate semantic commit messages and pull request descriptions that follow your repository's conventions and PR template.

Perfect for developers who want to maintain high-quality commit history and PR documentation without the manual overhead.

## Features

- **Single-command workflow** - Execute commit, push, and PR creation in one step
- **Smart commit messages** - Auto-generates semantic commit messages following conventional commits format
- **PR template integration** - Automatically follows your repository's `.github/PULL_REQUEST_TEMPLATE.md` structure
- **Protected branch detection** - Prevents accidental commits to main/master/develop branches
- **Auto-staging** - Automatically stages modified tracked files
- **Branch management** - Creates feature branches when needed
- **PR updates** - Supports updating existing PRs with new commits
- **Interactive prompts** - Asks for tracking tickets and other essential information
- **Error prevention** - Validates environment before making changes

## Installation

Add the Bitwarden AI Plugin Marketplace to Claude Code:

```bash
/plugin marketplace add bitwarden/ai-plugins
```

Install the git-workflow plugin:

```bash
/plugin install git-workflow@bitwarden-marketplace
```

Restart Claude Code for the plugin to become active.

## Usage

### Basic Usage

Simply run the slash command from within your git repository:

```
/commit-push-pr
```

The command will:
1. Validate your environment
2. Stage all modified tracked files
3. Analyze changes and generate a commit message
4. Create a commit
5. Push to remote
6. Create or update a pull request

### Example Workflow

```bash
# Make some changes to your code
# Open Claude Code
/commit-push-pr
```

**Example output**:
```
✅ Workflow Complete

Commit: f3a7bc2 feat(auth): add SSO login support
Branch: feature/add-sso-login
Push: created new branch
PR: created - https://github.com/bitwarden/vault/pull/1234
```

## Requirements

Before using this plugin, ensure you have:

- **Git** - Installed and configured
- **GitHub CLI (`gh`)** - Installed and authenticated
  ```bash
  gh auth login
  ```
- **Repository setup** - Inside a git repository with a configured remote
- **Changes to commit** - Modified tracked files

## How It Works

### 1. Pre-flight Validation

The command first validates:
- Not on a protected branch (main/master/develop)
- Changes exist to commit
- Git remote is configured
- GitHub CLI is authenticated

### 2. Commit Message Generation

Analyzes your changes using:
- `git diff HEAD` - What changed
- `git status` - Which files were modified
- `git log` - Recent commit style

Generates a semantic commit message:
```
<type>(<scope>): <subject>

Optional body explaining WHY

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Commit types**:
- `feat` - New feature
- `fix` - Bug fix
- `refactor` - Code restructuring
- `docs` - Documentation
- `test` - Tests
- `chore` - Build/config changes
- `style` - Formatting

### 3. Branch Handling

- **On main**: Automatically creates a feature branch with a descriptive name
- **On feature branch**: Uses the existing branch
- **New branch**: Pushes with `-u` to create remote tracking
- **Existing branch**: Pushes additional commits

### 4. Pull Request Creation

#### With PR Template

If `.github/PULL_REQUEST_TEMPLATE.md` exists:

**🎟️ Tracking**
- Prompts for ticket/issue number
- Formats as link if URL provided
- Optional - can be skipped

**📔 Objective**
- Auto-generated from commit analysis
- Focuses on WHY and business value
- 2-3 sentences summarizing purpose

**⏰ Reminders before review**
- Copied unchanged from template
- Developer checklist

**🦮 Reviewer guidelines**
- Copied unchanged from template
- Emoji conventions for review comments

#### Without PR Template

Uses fallback structure:
- Summary (from commits)
- Changes (from diff stats)
- Test plan (inferred from changes)

### 5. PR Updates

If a PR already exists for the branch:
- Pushes the new commit
- Asks if you want to update the PR body
- Updates only if you confirm

## PR Template Integration

This plugin is designed to work seamlessly with the Bitwarden PR template structure. The generated PR body follows the template format while auto-populating sections based on code analysis.

### Template Sections

**Auto-populated**:
- 🎟️ Tracking (via user prompt)
- 📔 Objective (from commit analysis)

**Preserved from template**:
- ⏰ Reminders before review
- 🦮 Reviewer guidelines

**Added**:
- Claude attribution footer

## Interactive Prompts

### Tracking Ticket Prompt

When creating a new PR:
```
Do you have a tracking ticket or GitHub issue for this PR?
[Enter URL/number or skip]
```

Provide:
- Full GitHub issue URL: `https://github.com/org/repo/issues/123`
- Issue number: `#123`
- Jira ticket: `PROJ-456`
- Or press Enter to skip

### PR Update Prompt

When PR exists:
```
PR already exists: https://github.com/org/repo/pull/123
Update PR body with latest changes?
- Yes, update PR body
- No, keep existing
```

## Troubleshooting

### Error: Cannot commit to protected branch

**Problem**: You're on main, master, or develop branch.

**Solution**: The command will automatically create a feature branch if you're on main. If you see this error on a different protected branch, manually create a feature branch first:

```bash
git checkout -b feature/your-feature-name
```

### Error: No changes to commit

**Problem**: Working directory is clean - no modified tracked files.

**Solution**: Make some changes to tracked files before running the command. If you have new untracked files, stage them first:

```bash
git add new-file.ts
```

### Error: GitHub CLI not authenticated

**Problem**: The `gh` CLI is not authenticated.

**Solution**: Authenticate with GitHub:

```bash
gh auth login
```

Follow the prompts to authenticate via browser or token.

### Error: No git remote configured

**Problem**: Repository doesn't have a remote URL configured.

**Solution**: Add a remote:

```bash
git remote add origin https://github.com/org/repo.git
```

### PR creation failed but commit succeeded

**Problem**: The commit and push succeeded, but PR creation failed.

**Solution**: The commit is safely pushed. Create the PR manually:

```bash
gh pr create
```

Or retry the `/commit-push-pr` command - it will detect the existing commits and just create the PR.

## Best Practices

### When to Use This Command

**Good for**:
- Feature development with single-purpose changes
- Bug fixes with clear scope
- Quick iterations with multiple commits
- Standard workflow automation

**Not ideal for**:
- Complex multi-commit work requiring careful history curation
- When you need precise control over commit message wording
- Experimental changes you're not ready to push
- When you want to review staged changes before committing

### Tips

- **Untracked files**: New files won't be committed automatically. Add them with `git add <file>` first if needed.
- **Partial commits**: To commit only specific files, stage them manually before running the command.
- **Multiple commits**: For multiple logical commits, use regular git commands, then use `/commit-push-pr` for the final commit that creates the PR.
- **Commit message style**: The command learns from your repository's recent commits to match the existing style.
- **Draft PRs**: This command creates regular PRs. For draft PRs, use `gh pr create --draft` manually.

## Security

This plugin only executes read operations and standard git workflow commands:
- Allowed: `git add`, `git commit`, `git push`, `gh pr create`, `gh pr edit`, `gh pr view`
- Prevents: Force pushes, hard resets, destructive operations
- Validates: Protected branches, authentication, remote configuration

## Examples

### Example 1: New Feature Branch

```bash
# You're on main, make some changes
/commit-push-pr
```

Result:
- Creates `feature/add-user-settings` branch
- Commits with: `feat(settings): add user preferences page`
- Pushes to origin
- Creates PR with auto-generated description

### Example 2: Continuing Work

```bash
# Already on feature/refactor-auth, make more changes
/commit-push-pr
```

Result:
- Stays on `feature/refactor-auth`
- Commits with: `refactor(auth): simplify token validation logic`
- Pushes to existing remote branch
- Updates existing PR (if requested)

### Example 3: Bug Fix

```bash
# On feature/fix-login-redirect, fix a bug
/commit-push-pr
```

Result:
- Commits with: `fix(auth): correct redirect after login timeout`
- Pushes to origin
- Creates PR with proper bug fix description

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

To report issues or suggest improvements:
- GitHub Issues: https://github.com/bitwarden/ai-plugins/issues
- Bitwarden Contributing Guidelines: https://contributing.bitwarden.com

## Version History

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## License

This plugin is maintained by Bitwarden and distributed as part of the Bitwarden AI Plugin Marketplace.

## Resources

- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- [Claude Code Plugins Guide](https://docs.claude.com/en/docs/claude-code/plugins.md)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [GitHub CLI Documentation](https://cli.github.com/manual/)
