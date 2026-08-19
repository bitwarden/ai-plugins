# reviewing-claude-config

Entry point for reviewing Claude Code configuration. Runs the security checks, then routes each file type to a targeted review skill.

## Overview

This skill is the entry point for reviewing Claude Code configuration. It settles what is in scope, runs the security checks with `Grep`, routes each file type to a targeted review skill, filters the results, and returns classified findings. Its grant is `Read, Grep, Glob, Skill`, so it reads, routes, and reports rather than executing anything or posting anywhere.

Two rules shape every review it produces: findings are limited to **what the changeset introduced or worsened**, and a review fails only on **a CRITICAL finding, or one that weakens security**, which includes a new route from contributor input to a shell.

**Use this skill when:**

- Reviewing changes to `CLAUDE.md` files
- Reviewing agents (`.claude/agents/`, `plugins/*/agents/`)
- Reviewing prompts or commands (`.claude/prompts/`, `.claude/commands/`, `plugins/*/commands/`)
- Reviewing hooks (`hooks.json`, or a `hooks` block in a settings file)
- Reviewing settings files (`.claude/settings.json`)
- Validating Claude configuration security and quality

## Features

### Security-First Approach

- Flags `settings.local.json` appearing in a changeset, from the changed-files list when one is available, reported as skipped otherwise
- Scans for hardcoded secrets and credentials
- Validates permission scoping
- Identifies dangerous command auto-approvals
- Ships a `security-scan.sh` helper you can run yourself; the skill performs the same pattern checks with `Grep`

### Routing

- Detects configuration file type automatically
- Invokes the targeted review skill for that type
- Loads reference material only when a specific question calls for it
- Leaves `SKILL.md` review to `plugin-dev:skill-reviewer`, which already covers it

### Quality Enforcement

- YAML frontmatter validation
- Prompt engineering quality checks
- File reference integrity validation
- Verbosity of `CLAUDE.md`, which is re-read every turn in its scope
- Instruction-content review of skill support files that have no targeted reviewer

### What it routes to

- **Targeted review skills**: agent definitions, command definitions, runtime configuration (settings and hooks), project guidance (`CLAUDE.md`)
- **Reference guides**: Priority framework, security patterns, Claude Code requirements, changeset scope
- **Human-run security script**: `security-scan.sh`, which you run yourself; the skill applies the same patterns with `Grep`

## Installation

### Install the plugin (recommended)

The skill ships inside the `claude-config-validator` plugin, so installing the plugin is all it takes:

```bash
/plugin marketplace add bitwarden/ai-plugins
/plugin install claude-config-validator@bitwarden-marketplace
```

Its files then live under the plugin root rather than in your project.

### Standalone use

To use the skill on its own, outside the plugin, copy the directory into a project's `.claude/skills/`:

```bash
cp -r reviewing-claude-config /path/to/your/project/.claude/skills/
```

Under this layout the skill's own directory is `.claude/skills/reviewing-claude-config`. A plugin install puts the same files under the plugin cache instead; see the paths below.

### Verify Installation

For a plugin install, `/plugin list` inside Claude Code is the check that matters.

To inspect the files from a terminal, note that `CLAUDE_PLUGIN_ROOT` is set by Claude Code only while it runs plugin-owned commands and hooks. It is unset in your shell, so use a real path:

```bash
# Standalone layout, from the project root
ls -la .claude/skills/reviewing-claude-config/SKILL.md

# Plugin install: under the plugin cache, keyed by marketplace and version
ls -la ~/.claude/plugins/cache/*/claude-config-validator/*/skills/reviewing-claude-config/SKILL.md
```

## Usage

### As a Skill (Recommended)

Claude Code will automatically invoke this skill when appropriate based on the description. You can also invoke it explicitly:

```
Review the changes to .claude/CLAUDE.md
```

The skill will:

1. Settle scope — only what the change introduced or worsened
2. Execute the security scan
3. Detect the file type (CLAUDE.md in this case) and invoke the targeted review skill
4. Filter the candidate findings
5. Return a structured review, one finding per issue

### Manual Security Scan

Run the executable security script directly:

With no argument it scans the `.claude` directory of the current working directory:

```bash
# Standalone layout
.claude/skills/reviewing-claude-config/scripts/security-scan.sh

# Plugin install
~/.claude/plugins/cache/*/claude-config-validator/*/skills/reviewing-claude-config/scripts/security-scan.sh

# Or scan a specific directory, from either layout
.claude/skills/reviewing-claude-config/scripts/security-scan.sh /path/to/.claude
```

The script checks for:

- Committed settings.local.json
- Hardcoded secrets (API keys, tokens, passwords)
- Overly broad permissions
- Dangerous command auto-approvals

### Examples

**Review a new agent:**

```
Review .claude/agents/my-new-agent.md
```

**Review settings changes:**

```
Review the changes to .claude/settings.json
```

**Review CLAUDE.md updates:**

```
Review .claude/CLAUDE.md for quality and security
```

## File Structure

```
skills/
├── reviewing-claude-config/              # This skill — the entry point
│   ├── SKILL.md                          # Scope, security scan, routing, filtering, output
│   ├── reference/                        # Reference materials (loaded on-demand)
│   │   ├── claude-code-requirements.md   # YAML, tools, models, limits
│   │   ├── priority-framework.md         # Issue classification system
│   │   ├── security-patterns.md          # Security checks and remediation
│   │   └── validate-ai-scope.md          # Changeset scope and report contract
│   ├── scripts/                          # Human-run helpers
│   │   └── security-scan.sh              # Comprehensive security scanner
│   └── README.md                         # This file
├── reviewing-agent-definitions/          # Tool access, triggers, system prompts
├── reviewing-command-definitions/        # Slash commands and prompts
├── reviewing-runtime-configuration/      # Settings and hooks
└── reviewing-project-guidance/           # CLAUDE.md
```

Each targeted skill is a single `SKILL.md`. Its calibration examples live inline at the
point of the check, rather than in a separate directory.

## Review Process

The skill follows a systematic 5-step review process:

1. **Settle Scope**: Findings are limited to what the changeset introduced or worsened. A changed file is not a changed line
2. **Execute Security Scan**: Always performs critical security checks first
3. **Route**: Invokes the targeted review skill for each file type in scope
4. **Filter**: Drops candidates that are pre-existing, have no remediation, are unspecific, are already covered by another checker, or could not be verified in the file
5. **Document Findings**: Returns one finding per issue, anchored to `file:line`, with a specific fix

### Security Checks (Always First)

Regardless of file type, these checks are performed:

- ✅ No `settings.local.json` in the changeset, from the changed-files list when one is available and reported as skipped otherwise
- ✅ No hardcoded credentials
- ✅ Permissions appropriately scoped
- ✅ No dangerous command auto-approvals

If any security check fails, it's flagged as **CRITICAL** immediately and the review then finishes the remaining checks, so the report can still say which ones ran.

### Priority Levels

Issues are classified into four priority levels, defined in
[`reference/priority-framework.md`](reference/priority-framework.md):

- **CRITICAL**: Prevents functionality, exposes security vulnerabilities (must fix)
- **IMPORTANT**: Functional defect or security regression that still loads (should fix)
- **SUGGESTED**: Quality, readability, and structure improvements (could fix)
- **OPTIONAL**: Personal preferences, alternatives (consider)

**Only a CRITICAL finding, or a finding that weakens security, fails a review.** A finding
that widens a permission, tool grant, or hook capability, or that opens a new path from
contributor-controlled input to a shell, sets `Issues found` at whatever severity it carries. Everything else is reported and listed without setting the verdict.

Reporting a finding and failing the run are separate decisions: a review that fails on
readability is a review people learn to ignore. Security needs its own clause rather than a
severity threshold, because `priority-framework.md` rates some real regressions IMPORTANT — an
over-broad agent tool grant that stops short of credentials, a permission broader than needed.

## Requirements

- Claude Code (tested with latest version)

The optional `security-scan.sh` helper additionally needs Git, for committed-file detection,
and Bash to run it. The skill itself needs neither: its grant is `Read, Grep, Glob, Skill`.

## Configuration

This skill works out-of-the-box with no configuration needed. It's 100% generic and supports any project type or language.

### Customization

If you want to customize for your organization:

1. **Modify a targeted skill**: Add project-specific requirements to the skill for that file type
2. **Adjust security patterns**: Add organization-specific secret patterns to `security-scan.sh`
3. **Update priority framework**: Adjust severity levels based on team standards

**Note**: Keep changes generic to maintain portability if sharing with other teams.

## Review Output Format

Each review follows this structure. The skill produces findings and never delivers them, so
where they go is decided by the invoking context, in the order `SKILL.md` step 5 sets out:
the two `validate-ai` commands write the single-document report contract in
`reference/validate-ai-scope.md`; anything else gets the findings back as text to route.

**Findings**, one per issue:

```
**file:line** - PRIORITY: Issue description

[Specific fix with code example]

[Rationale explaining why this matters]
```

**Overall assessment**, stated once. A CRITICAL finding, or one that weakens security, makes it `Issues found`:

```
Pass / Issues found

[Findings grouped by priority: CRITICAL → IMPORTANT → SUGGESTED → OPTIONAL]
```

### Best Practices

**Feedback Quality:**

- Provide specific fixes with code examples, not just problem identification
- Explain rationale (the "why"), not just the "what"
- Include references to documentation when applicable
- Use precise file:line references

**Tone:**

- Constructive and specific, never dismissive
- Focus on code/config, not people
- Acknowledge complexity and trade-offs
- Balance criticism with recognition of what works well

## Research Foundation

This skill incorporates research-backed best practices:

- **Chain of Thought prompting**: reduces reasoning errors (Anthropic)
- **Least privilege**: tool grants scoped to what a component's description justifies
- **Structured thinking**: Systematic analysis before feedback
- **Security-first approach**: Critical checks before quality review

See `reference/claude-code-requirements.md` for the requirements these criteria are drawn from.

## Troubleshooting

### Skill Not Recognized

**Issue**: Claude doesn't invoke the skill automatically

**Solutions:**

1. Verify YAML frontmatter exists in `SKILL.md`
2. Check skill name is `reviewing-claude-config`
3. Confirm the skill is available: run `/plugin list` for a plugin install, or check that the
   files sit in `.claude/skills/reviewing-claude-config/` for a standalone copy
4. Try invoking explicitly: "Use reviewing-claude-config skill"

### Security Script Fails

**Issue**: `./scripts/security-scan.sh` returns errors

**Solutions:**

1. Make executable: `chmod +x scripts/security-scan.sh`
2. Verify you're in a git repository (for git commands)
3. Check script has access to `.claude` directory
4. Review error messages for specific issues

### False Positives in Security Scan

**Issue**: Security scan detects patterns in documentation

**Solutions:**

1. Security scan excludes `examples/` directories, `security-patterns.md`, and the scanner itself. It does not exclude the targeted skills, whose teaching examples sit inline in `skills/reviewing-*/SKILL.md`, so add those paths if you scan this plugin
2. Use "example" or "your-key-here" as placeholders in docs
3. Review manually to confirm false positives

## Contributing

This skill is designed for internal team use but follows open-source best practices.

**To contribute improvements:**

1. Test changes in your project first
2. Ensure changes remain 100% generic (no project-specific references)
3. Update the plugin's [`CHANGELOG.md`](../../CHANGELOG.md) with your changes
4. Bump the plugin version across the files the repository's `.claude/CLAUDE.md` lists. The skill has no version of its own

## Versioning

This skill follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes to skill interface or file structure
- **MINOR**: New features, new targeted review skills, backward-compatible changes
- **PATCH**: Bug fixes, documentation updates, minor improvements

The skill ships with the plugin and carries the plugin's version. See
[`../../CHANGELOG.md`](../../CHANGELOG.md) for version history.

## Support

For issues, questions, or feedback:

1. Check troubleshooting section above
2. Read the targeted review skill for the file type in question
3. Consult reference files for detailed guidance
4. Contact your team's Claude Code administrator

## Acknowledgments

Built with research-backed best practices from:

- Anthropic Official Documentation (Chain of Thought, Progressive Disclosure)
- Claude Code Best Practices
- Security best practices for credential detection
- Prompt engineering quality standards
