# Bitwarden DevOps Engineer Plugin

Claude Code commands and skills for GitHub Actions workflow compliance, action security auditing, and org-wide CI/CD remediation. Generic AI assistance doesn't know Bitwarden's workflow linter rules, approved actions list, or remediation patterns. These tools keep Claude focused on how we manage CI/CD workflows here.

## Components

**Agent:** `bitwarden-devops-engineer`

**Commands:** `workflow-fix`, `action-audit`

**Skills:** `bitwarden-workflow-linter-rules`

## Installation

Available through Bitwarden's internal Claude Code marketplace:

```bash
# Add the Bitwarden marketplace (if not already added)
/plugin marketplace add https://github.com/bitwarden/ai-plugins

# Install the DevOps engineer plugin
/plugin install bitwarden-devops-engineer@bitwarden-marketplace

# Restart Claude Code
```

## References

- [Bitwarden Workflow Linter](https://github.com/bitwarden/workflow-linter) — `bwwl` source, approved actions list, and rule definitions
- [actionlint](https://github.com/rhysd/actionlint) — Static checker for GitHub Actions workflow files, used internally by `bwwl`
- [GitHub Actions Documentation](https://docs.github.com/en/actions) — Workflow syntax, permissions model, and contexts reference
- [GitHub Code Search](https://docs.github.com/en/search-github/github-code-search/understanding-github-code-search-syntax) — Syntax reference for `gh search code` used in `action-audit`
