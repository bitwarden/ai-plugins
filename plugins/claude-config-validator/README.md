# Claude Config Validator Plugin

Comprehensive validation for Claude Code configuration files, ensuring security, structure, and quality standards across all configuration types.

## Overview

The Claude Config Validator plugin provides expert-level validation for Claude Code projects, reviewing configuration files with the same rigor as human code reviewers. It catches security vulnerabilities, structural issues, and quality problems before they impact your AI-assisted development workflows.

## Features

### Comprehensive Configuration Coverage

Validates these configuration file types, each routed to its own targeted skill except where noted:

| Configuration Type                                                                    | What Gets Validated                                                                                                                                   |
| ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Agents** (`.claude/agents/*.md`)                                                    | YAML frontmatter, tool access security, model selection, system prompt quality, description clarity                                                   |
| **Skills** (`SKILL.md`)                                                               | Not validated here. The commands delegate this to `plugin-dev:skill-reviewer`; support files under a skill are read by `reviewing-claude-config`      |
| **CLAUDE.md** (project instructions)                                                  | Clarity, specificity, security patterns, proper emphasis, structured organization                                                                     |
| **Prompts/Commands** (`.claude/prompts/`, `.claude/commands/`, `plugins/*/commands/`) | Purpose clarity, session context handling, skill references, parameter validation                                                                     |
| **Hooks** (`hooks.json`, or a `hooks` block in settings)                              | Schema, event names, `${CLAUDE_PLUGIN_ROOT}` script paths, command and prompt-hook safety                                                             |
| **Settings** (`.claude/settings.json`)                                                | Security (no committed credentials), permission scoping, valid JSON structure                                                                         |
| **Plugin Configurations** (`plugins/*/`)                                              | Manifest validation, directory structure, marketplace standards. No checklist of its own: the commands delegate this to `plugin-dev:plugin-validator` |

### Security-First Validation

Every review **always** includes critical security checks:

- ✅ No `settings.local.json` in the changeset, checked from the changed-files list when one is available and reported as skipped otherwise
- ✅ No hardcoded credentials (API keys, passwords, tokens)
- ✅ Appropriate permission scoping
- ✅ Principle of least privilege for agent tool access
- ✅ An inventory of every string the configuration runs or auto-approves, for a reviewer to read

### Evidence-Based Quality Standards

All validation criteria sourced from **official Anthropic documentation**:

- Agent tool access security matrices
- Model selection decision trees (haiku/sonnet/opus)
- System prompt engineering patterns
- Hook command safety and event-name currency

### Multi-Pass Review Strategy

The skill works through five steps:

1. **Settle Scope** - Only what the changeset introduced or worsened; a changed file is not a changed line
2. **Security Scan** - Critical checks first (prevents wasted effort on insecure configs)
3. **Route** - Invokes the targeted review skill for the detected type
4. **Filter** - Drops candidates that are pre-existing, unspecific, have no remediation, or are already covered by a checker outside this pipeline; duplicates from two checkers inside it are merged at the higher severity
5. **Document Findings** - One finding per issue, anchored to `file:line`

Each targeted skill then runs its own multi-pass strategy over the file under review.

### Specific, Actionable Feedback

Provides specific, file:line referenced feedback with:

- **Priority classification** (CRITICAL / IMPORTANT / SUGGESTED / OPTIONAL)
- **Specific fixes** with code examples
- **Rationale** explaining why issues matter
- **References** to official documentation

## Installation

Requires Claude Code 2.1.210 or later. Both commands scope their report write with an
`Edit(<path>)` rule, and consulting that rule for the `Write` tool is behavior that release
introduced. On an older CLI the report write falls back to a permission prompt, which in a
headless workflow run means no report and a failed check.

### Add Bitwarden Marketplace (if not already added)

```bash
/plugin marketplace add bitwarden/ai-plugins
```

### Install the Plugin

```bash
/plugin install claude-config-validator@bitwarden-marketplace
```

## Usage

### Commands

| Command                                                      | Purpose                                                                                                                                              |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`/validate-ai-local`](commands/validate-ai-local/README.md) | Validate the Claude material you changed locally (branch commits plus uncommitted work) and write a report to `${CLAUDE_PLUGIN_DATA}/ai-validation/` |
| [`/validate-ai`](commands/validate-ai/README.md)             | Validate the Claude material changed in a pull request and report to a sticky pull request comment                                                   |

Both commands run the same review the
[validate-ai](https://github.com/bitwarden/gh-actions/tree/main/validate-ai) GitHub
Action runs org-wide: this plugin's `reviewing-claude-config` skill for configuration and
security, plus the `plugin-dev` plugin's `plugin-validator` and `skill-reviewer` agents
for plugin structure and skill quality. `/validate-ai-local` additionally runs the
action's structure, marketplace, and version-bump shell checks against your checkout.
They share their scope rules and report contract in
[`reference/validate-ai-scope.md`](skills/reviewing-claude-config/reference/validate-ai-scope.md),
so the two commands and the action cannot drift apart.

### Basic Invocation

```bash
/claude-config-validator:reviewing-claude-config
```

Or describe the review in your own words, which is how the skill's triggers are written to be reached.

The skill will automatically:

1. Detect the type of each configuration file you name
2. Route it to the targeted review skill for that type
3. Execute security-first review
4. Return one finding per issue with file:line references

### Use Cases

#### 1. Pre-Commit Configuration Review

**Scenario**: You've created a new agent configuration and want to ensure it meets security and quality standards before committing.

**Usage**:

```markdown
Review my new agent configuration in .claude/agents/code-analyzer.md
```

**Output**: One finding per issue with specific improvements. Security concerns are CRITICAL where they reach credentials or destructive commands and IMPORTANT otherwise; quality suggestions are SUGGESTED or OPTIONAL.

---

#### 2. Plugin Marketplace Submission Validation

**Scenario**: You're preparing a plugin for marketplace submission and need to meet elevated quality standards.

**Usage**:

```markdown
Review my plugin configuration in plugins/my-plugin/ for marketplace readiness
```

**Output**: The component files inside `plugins/my-plugin/` reviewed by the targeted skills for agents, commands, hooks, and settings, with security findings first. Two things are deliberately not this skill's: `SKILL.md` review, which `plugin-dev:skill-reviewer` owns, and manifest and marketplace-standard checks, which `plugin-dev:plugin-validator` owns. `/validate-ai-local` runs all three together.

---

#### 3. Runtime Configuration Review

**Scenario**: A pull request changes `.claude/settings.json` and adds a hook.

**Usage**:

```markdown
Review the settings and hook changes in this branch
```

**Output**: Permission scoping against least privilege, auto-approval safety, and every hook command read as executable code: egress, destructive operations, credential access, and hook input routed into a shell.

---

#### 4. Security Audit

**Scenario**: You want to audit all Claude configurations in your project for security issues.

**Usage**:

```markdown
Security audit all Claude configuration files in this project
```

**Output**: Security-focused review covering credential exposure, permission scoping, dangerous patterns, tool access violations.

## Skills Included

### reviewing-claude-config

**Description**: Reviews Claude configuration files for security, structure, and prompt engineering quality, wherever they live: a repository's `.claude/` directory, a root `CLAUDE.md`, or a plugin's own components.

**Validates**, by routing each type to a targeted skill:

| Type                 | Skill                             |
| -------------------- | --------------------------------- |
| Agents               | `reviewing-agent-definitions`     |
| Prompts and commands | `reviewing-command-definitions`   |
| Settings and hooks   | `reviewing-runtime-configuration` |
| CLAUDE.md files      | `reviewing-project-guidance`      |

`SKILL.md` files are reviewed by `plugin-dev:skill-reviewer`, not here — it already covers frontmatter, trigger quality, word count, progressive disclosure, and broken references, and both `validate-ai` commands route every changed skill to it.

**Capabilities**:

- YAML frontmatter validation
- Verbosity of `CLAUDE.md`, which is re-read every turn in its scope
- Instruction-content review of skill support files that have no targeted reviewer
- Security best practice enforcement
- Detection of critical issues (committed secrets, malformed YAML, broken references, insecure tool access, unsafe hook commands)

**Validation Strategy**:

- Multi-pass review (structure → security → functionality → quality)
- Evidence-based recommendations (all criteria from official docs)
- Priority-classified feedback (CRITICAL → IMPORTANT → SUGGESTED → OPTIONAL)
- Per-issue findings with specific fixes and rationale

## Validation Coverage Details

### Agent Validation (`reviewing-agent-definitions`)

Five passes, ordered so the security question comes first.

**Pass 1: Tool access** — least privilege; analysis-only agents holding `Write`, `Edit`, or `Bash`; `Bash` unexplained by the description; unexplained `WebFetch` or `WebSearch` egress alongside read access; unexplained `Task` or `Skill`, both of which escape the grant rather than widening it; tool names exact and case-sensitive, since a misspelled entry is silently not a grant; a grant that contradicts what the description claims.

**Pass 2: Frontmatter** — valid YAML, required `name` and `description`, `<example>` blocks, valid `color`, non-empty system prompt. Skipped only where `plugin-dev:plugin-validator` actually ran, and recorded as skipped rather than passed; a bare `.claude/agents/*.md`, or any agent when `plugin-dev` is not installed, is checked here.

**Pass 3: Description and activation triggers** — states both what the agent does and when to reach for it; single responsibility rather than a catch-all.

**Pass 4: System prompt** — role, capabilities, boundaries, and output format where the agent produces a structured artifact; decision criteria rather than bare instructions.

**Pass 5: Model selection** — flagged only on a clear mismatch, such as `opus` for formatting or `haiku` for deep analysis.

### Skill Validation

Not performed by this plugin. `plugin-dev:skill-reviewer` owns `SKILL.md` review — frontmatter, description and trigger quality, word count and writing style, progressive disclosure, and referenced files that do not exist — and both `validate-ai` commands route every changed skill to it. Reviewing the same file against a second rule set produces duplicate findings a reader cannot tell from independent confirmation.

Skill support files (`reference/`, `examples/`, `scripts/`) have no targeted reviewer, so `reviewing-claude-config` reads them directly for instruction content.

### Security Validation (Always Executed)

**Critical Checks** (all configuration types):

- No `settings.local.json` in the changeset, from the changed-files list when one is available and reported as skipped otherwise
- No hardcoded credentials (passwords, API keys, tokens)
- Permissions appropriately scoped
- No secrets in plaintext

**Detection Methods**:

- Pattern matching for common secret formats, applied with `Grep`
- Permission validation against least privilege principle

## Examples

### Example 1: Agent Security Issue

**Input**: Agent configuration with missing `tools` field

**Output**:

```
**.claude/agents/documentation-writer.md:1-6** - CRITICAL: Missing tools field - inherits all tools including Bash

Agent has no `tools` field, meaning it inherits ALL tools including destructive operations.

Recommended:
---
name: documentation-writer
description: Generates API documentation...
tools: Read, Grep, Glob, Write
---

Rationale:
- Read/Grep/Glob: Analyze code to document
- Write: Create documentation files
- NO Edit: Doesn't modify source code
- NO Bash: Documentation doesn't require command execution

Security principle: Grant minimum necessary tools only.

Reference: `reference/claude-code-requirements.md` - Tool Access Security
```

### Example 2: Hook Credential Access

**Input**: A pull request adding a `PostToolUse` hook

**Output**:

```
**.claude/settings.json:14** - CRITICAL: Hook command reads SSH private keys

Current:

"command": "cat ~/.ssh/id_rsa >> .build-cache/audit.log"

Hooks run automatically on tool events with no permission prompt, from a file a
contributor can edit in a pull request. This command exfiltrates nothing by itself,
so it clears an egress check — but it stages key material in a file a later step can
ship. Read now, send later is the usual shape.

Remove the command. If the hook needs to know a key exists, test for the path rather
than reading its contents.
```

### Example 3: CLAUDE.md Clarity Issue

**Input**: CLAUDE.md with vague instructions

**Output**:

```
**.claude/CLAUDE.md:42** - SUGGESTED: Instruction lacks specificity

Current: "Always write good code"
Issue: "Good code" is subjective and non-actionable.

Recommended:
"Follow these code quality standards:
- Write comprehensive unit tests for all business logic
- Use descriptive variable names (no single letters except loop counters)
- Add inline comments explaining 'why', not 'what'
- Follow project's established patterns in `docs/architecture.md`"

Specific, actionable instructions improve AI behavior (Anthropic prompt engineering guidance).

Reference: `reviewing-project-guidance` - Pass 4: Clarity
```

## Running the security scanner directly

`security-scan.sh` is a human-run helper, not something the skills execute: their grants are
read-only. Check 4 reads every string in `settings.json` except the rules in
`permissions.deny` and `permissions.ask`, which are controls rather than grants. That covers
`permissions.allow`, `additionalDirectories`, `apiKeyHelper`, `statusLine.command`, hook
commands and `env` values without enumerating them.

Check 3 is narrower on purpose. Its sensitive-path scan reads `permissions.allow` and
`additionalDirectories` only, since a path in a grant is the whole meaning of the rule, while a
path a command merely mentions is a judgment call Check 4 hands to the reviewer. Its rule-form
test additionally reads `deny` and `ask`, since a colon-separated rule fails open in any array.

The four checks are: a committed `settings.local.json`; hardcoded secrets; permission scoping,
covering filesystem-wide, bare and sensitive-path grants, rule forms Claude Code does not read,
and `defaultMode: bypassPermissions`; and an inventory of every string the configuration runs
or auto-approves, each with its location in the file.

Check 4 lists rather than classifies. Pattern-matching shell strings traded a false negative
for a false positive every time it was tightened, so the script reports what will run and the
reviewer judges it.

```bash
# Scans the .claude directory of the current working directory
~/.claude/plugins/cache/*/claude-config-validator/*/skills/reviewing-claude-config/scripts/security-scan.sh

# Or a specific directory
~/.claude/plugins/cache/*/claude-config-validator/*/skills/reviewing-claude-config/scripts/security-scan.sh /path/to/.claude
```

The permission checks and the inventory report themselves as skipped rather than passed when
they cannot run. Check 3's four rule tests need `jq`, a `settings.json` that parses, and string
rules in `permissions.allow`, since a rule in `deny` is the control rather than a defect and
telling it from `allow` needs the array the rule sits in; the inventory needs the first two. The
`settings.local.json` check does the same when the target is not inside a git repository, since
it cannot then tell whether the file is committed.

An absent `settings.json` is not a skip. It is an answer: no rules are set in the scanned
directory. Rules reaching the session from elsewhere, such as `~/.claude/settings.json` or
managed settings, are outside what this scan looks at.

`scripts/security-scan.test.sh` covers the scanner, including the paths where a check that did
not run must not report as passed. It is plain bash and takes no arguments:

```bash
skills/reviewing-claude-config/scripts/security-scan.test.sh
```

Nothing runs it automatically, so run it after changing the scanner. Install `jq` first: without
it check 3's rule tests are skipped and the suite asserts the incomplete verdict instead of the
clean one, which still passes but exercises less.

## Plugin Structure

```
plugins/claude-config-validator/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── CHANGELOG.md             # Version history
├── commands/
│   ├── validate-ai/         # /validate-ai - pull request validation (command + README)
│   └── validate-ai-local/   # /validate-ai-local - local checkout validation (command + README)
├── skills/
│   ├── reviewing-claude-config/        # Entry point: scope, security scan, routing, filtering
│   │   ├── SKILL.md
│   │   ├── reference/                  # Priority framework, security patterns, requirements, changeset scope
│   │   └── scripts/                    # Security scan helper (human-run)
│   ├── reviewing-agent-definitions/    # Tool access, triggers, system prompts
│   ├── reviewing-command-definitions/  # Slash commands and prompts
│   ├── reviewing-runtime-configuration/ # Settings and hooks
│   └── reviewing-project-guidance/     # CLAUDE.md
└── README.md               # This file
```

## Contributing

Contributions welcome! Please follow:

- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com)
- Repository standards in root `README.md`
- Code quality requirements in `.editorconfig`

## Support

- **Issues**: [GitHub Issues](https://github.com/bitwarden/ai-plugins/issues)
- **Documentation**: [Claude Code Docs](https://docs.claude.com/en/docs/claude-code/)
- **Marketplace**: [Bitwarden AI Plugins](https://github.com/bitwarden/ai-plugins)
