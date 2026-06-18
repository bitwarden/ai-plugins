# Bitwarden Code Review Plugin

AI-powered code review for Bitwarden — an autonomous review agent for everyday PRs, plus a rigorous multi-agent pipeline for the changes that warrant a deeper look.

## Overview

This plugin provides an autonomous code review agent that conducts thorough, professional code reviews following Bitwarden's organizational standards. The agent focuses on security, correctness, and high-value feedback while maintaining a high signal-to-noise ratio.

It offers two complementary lenses. The autonomous `bitwarden-code-reviewer` agent reviews a pull request the way a human reviewer would and posts inline comments to GitHub. The `performing-multi-agent-code-review` skill takes a different approach — it has Claude evaluate code _as Claude_ across a pipeline of specialized sub-agents, trading human-style commentary for depth and high-signal findings written to a local report.

## Features

- **Autonomous Review Agent**: Single agent handles all code review tasks without manual invocation
- **Organizational Standards**: Consistent review process, finding classification, and comment formatting across all repositories
- **Thread Detection**: Prevents duplicate comments by detecting existing threads before posting
- **Security-First Approach**: Prioritizes security vulnerabilities, data exposure, and authentication issues
- **Structured Thinking**: Uses explicit reasoning blocks to improve review quality and consistency
- **Confidence Scoring**: Pre-filters findings with a 0-100 confidence score (≥75 threshold) before validation to reduce false positives
- **Multi-Agent Review Pipeline**: A separate `performing-multi-agent-code-review` skill runs six specialized sub-agents — architecture compliance, code quality, bug analysis, security & logic, validation, and severity audit — for depth on complex changes

## Skills

| Skill                                                                                        | Triggers                                                                          | Purpose                                                                                                                              |
| -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| [`classifying-review-findings`](./skills/classifying-review-findings/SKILL.md)               | "classify finding", "severity"                                                    | 5-tier severity system (CRITICAL / IMPORTANT / DEBT / SUGGESTED / QUESTION) with emoji and label mapping                             |
| [`avoiding-false-positives`](./skills/avoiding-false-positives/SKILL.md)                     | "validate finding", "verify before posting"                                       | Rejection criteria and verification checks that drop low-confidence findings before they reach a comment                             |
| [`performing-multi-agent-code-review`](./skills/performing-multi-agent-code-review/SKILL.md) | "perform multi-agent code review", "review the last week of commits in this repo" | Perform a rigorous, multi-agent code review                                                                                          |
| [`posting-bitwarden-review-comments`](./skills/posting-bitwarden-review-comments/SKILL.md)   | "post inline comment", "post PR comment"                                          | Inline PR comment formatting per Bitwarden standards (severity emojis, explanation, actionable suggestion)                           |
| [`posting-review-summary`](./skills/posting-review-summary/SKILL.md)                         | "post summary", "summary comment"                                                 | Final summary comment handling — routes to sticky comment, GitHub Actions MCP tool, or local file based on context                   |
| [`reviewing-dependency-changes`](./skills/reviewing-dependency-changes/SKILL.md)             | "package.json", "Renovate PR", "dependency manifest"                              | Flags dependency manifest changes for AppSec approval, version-bump significance, and lock-file hygiene                              |
| [`addressing-code-review-comments`](./skills/addressing-code-review-comments/SKILL.md)       | "address review comments", "respond to PR feedback"                               | Guides developers working through review comments locally — verify before implementing, surface ambiguity, no performative agreement |

## Architecture

### Code Review Agent

The plugin provides a single agent (`bitwarden-code-reviewer`) that follows a linear 7-step review process — from context gathering through validation to posting. See [`AGENT.md`](./agents/bitwarden-code-reviewer/AGENT.md) for the full flow.

### Finding Classification

See [`classifying-review-findings`](./skills/classifying-review-findings/SKILL.md) for the 5-tier severity system and classification criteria.

### Directory Structure

```bash
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
├── skills/                                   # See Skills table above
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

### Multi-agent code review skill

The `performing-multi-agent-code-review` skill is built for complex changes where one reviewer — human or AI — can't hold every concern in view at once. Instead of a single pass, it puts a team of specialized agents on the same diff, each reviewing from its own perspective — architecture and pattern compliance, code quality, bugs, and security & logic — then validates and severity-audits everything they surface. It started from [Anthropic's `code-review` command](https://github.com/anthropics/claude-code/blob/main/plugins/code-review/commands/code-review.md) and was rebuilt for the control that command lacks: it wires in our own `bitwarden-security-engineer` plugin, runs on any model you choose, reviews **draft or published** PRs — plus local changes, branch comparisons, and commit ranges — and writes its report to a local file instead of posting to GitHub.

It's a deliberately different lens from the `bitwarden-code-reviewer` agent. That agent reviews the way a human reviewer would; this skill has **Claude evaluate code as Claude** — optimized for signal, not parity. It spotlights blockers, real bugs, and known-bad patterns, and stays out of the nit-picking lane. Each potential finding is scored 0–100, and only those clearing an 80-confidence bar are raised; every one it keeps is cited with file, line, and the agent that caught it. What clears the bar still gets challenged — the validation and severity-audit agents can overturn a finding — but an overturned finding is never dropped: it moves into a collapsed **Reviewed and Dismissed** section, tagged with its original severity, original confidence, and the reason it was set aside. That section is deliberate — a human sees everything the first pass surfaced and can judge when a dismissal was wrong and the original call was right; without it, that signal is lost.

Agents start cold — a sub-agent inherits none of the main session's context — so the skill briefs every one of them explicitly. Each receives Bitwarden's zero-knowledge invariant and the P01–P06 threat-model directive verbatim. Feature context — the PR's intent, the ticket, the product framing — is handed out deliberately: the architecture and security agents get the full "why" so they can reason adversarially from intent, while the quality and bug agents see only the diff, so their first read stays unbiased.

The `performing-multi-agent-code-review` skill slots cleanly into a [Claude Code agent-teams](https://code.claude.com/docs/en/agent-teams) loop — run it at the end of a coding session, address what it finds, refactor — or as a depth-of-review gate on a draft PR before you publish.

#### Examples

Invoke the skill explicitly with the slash command, or with natural language — it triggers on phrasing like "thorough", "deep", "multi-pass", or "multi-agent" review, and on commit-range framing like "review the last week of commits". With no model flags, the review runs on your session's model, with the severity audit defaulting to sonnet.

**1. Local changes, all defaults.** The simplest run — review your uncommitted work before you commit:

> Perform a thorough multi-agent code review of my local changes.

**2. A specific pull request.** Pass a PR number or URL; it reviews draft and published PRs alike:

```markdown
/bitwarden-code-review:performing-multi-agent-code-review https://github.com/bitwarden/ios/pull/1234567 --model opus
```

**3. Changes over a period of time.** Commit-range mode reviews the cumulative diff across a time window, commit count, or explicit ref pair. Run it from inside the target repo; it confirms the resolved range with you before spending tokens:

```markdown
Review the last week of commits using /bitwarden-code-review:performing-multi-agent-code-review --model opus
```

**4. Full control, per stage.** Tune each stage independently — opus for analysis and validation, fable for security, sonnet for the audit — and send the report to a specific directory:

```bash
/bitwarden-code-review:performing-multi-agent-code-review \
  https://github.com/bitwarden/gh-actions/pull/604 \
  --model-analysis opus \
  --model-security fable \
  --model-validation opus \
  --model-audit sonnet \
  --output-dir ./reviews
```

A **security floor** keeps `--model-security` from ever dropping below your global model, so threat-model evaluation never silently degrades. Omit `--output-dir` and the report lands in `${CLAUDE_PLUGIN_DATA}`, organized across projects and never git-tracked.

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
