# Bitwarden DevOps Engineer Plugin

Claude Code skills for GitHub Actions workflow compliance, action security auditing, and org-wide CI/CD remediation. Generic AI assistance doesn't know Bitwarden's workflow linter rules, approved actions list, or remediation patterns. These skills keep Claude focused on how we manage CI/CD workflows here.

## Skills

| Skill                             | What It Does                                                                                                         |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `workflow-audit`                  | Runs the Bitwarden workflow linter (`bwwl`) and reports findings categorized as mechanical or judgment. Read-only.   |
| `workflow-fix`                    | Applies fixes for workflow linter findings, verifies with a re-lint, and creates draft PRs.                          |
| `action-audit`                    | Searches org-wide for compromised, deprecated, or unpinned GitHub Actions and produces a findings report. Read-only. |
| `action-remediate`                | Applies hash pins or action replacements across selected repos and creates draft PRs based on audit findings.        |
| `bitwarden-workflow-linter-rules` | Reference for all 10 `bwwl` linter rules — triggers, fix procedures, and mechanical vs. judgment categorization.     |

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
- [GitHub Code Search](https://docs.github.com/en/search-github/github-code-search/understanding-github-code-search-syntax) — Syntax reference for `gh search code` used in action auditing
