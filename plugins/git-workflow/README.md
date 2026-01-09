# Git Workflow Plugin

A Claude Code plugin that streamlines the git workflow by automating commit, push, and PR creation in a single command.

## Overview

The Git Workflow plugin automates the complete git workflow: it creates a commit with an auto-generated message, pushes to remote, and creates a pull request following your repository's PR template.

## Features

- **Single-command workflow** - Commit, push, and create PR in one step
- **Auto-generated commit messages** - Analyzes changes to create semantic commit messages
- **PR template integration** - Follows `.github/PULL_REQUEST_TEMPLATE.md` structure
- **Jira integration** - Extracts ticket ID from URL for PR title
- **Automatic branch creation** - Creates feature branch if on main

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

Simply run the command from within your git repository:

```
/commit-push-pr
```

The command will:
1. Create a new branch if you're on main
2. Commit your changes with an auto-generated message
3. Push the branch to origin
4. Ask for your Jira ticket URL
5. Create a PR with the Jira ID as the title and auto-generated body

### Example

```bash
# Make some changes to your code
/commit-push-pr
```

When prompted, provide your Jira URL:
```
https://bitwarden.atlassian.net/browse/PM-123
```

The PR will be created with:
- **Title**: `PM-123` Short descriptive title
- **Body**: Following the Bitwarden PR template with tracking link and objective

## Requirements

- **Git** - Installed and configured
- **GitHub CLI (`gh`)** - Installed and authenticated (`gh auth login`)
- **Repository setup** - Inside a git repository with a remote configured
- **Changes to commit** - Modified tracked files

## Version History

See [CHANGELOG.md](CHANGELOG.md) for version history.
