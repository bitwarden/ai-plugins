# reviewing-claude-config

Comprehensive skill for reviewing Claude Code configuration files with security-first approach.

## Overview

This skill provides systematic review guidance for Claude Code configuration files in `.claude` directories. It detects file types, applies appropriate review checklists, and runs its security checks with `Grep`. Its own grant is `Read, Grep, Glob`, so it reads and reports rather than executing anything or posting anywhere.

**Use this skill when:**

- Reviewing changes to `CLAUDE.md` files
- Reviewing skill files (`SKILL.md` and supporting files)
- Reviewing agents (`.claude/agents/`, `plugins/*/agents/`)
- Reviewing prompts or commands (`.claude/prompts/`, `.claude/commands/`, `plugins/*/commands/`)
- Reviewing hooks (`hooks.json`, or a `hooks` block in a settings file)
- Reviewing settings files (`.claude/settings.json`)
- Validating Claude configuration security and quality

## Features

### Security-First Approach

- Detects committed `settings.local.json` files
- Scans for hardcoded secrets and credentials
- Validates permission scoping
- Identifies dangerous command auto-approvals
- Ships a `security-scan.sh` helper you can run yourself; the skill performs the same pattern checks with `Grep`

### Intelligent Routing

- Detects configuration file type automatically
- Routes to appropriate specialized checklist
- Progressive disclosure for token efficiency
- Structured thinking throughout review process

### Quality Enforcement

- YAML frontmatter validation
- Progressive disclosure checks (500-line guideline)
- Prompt engineering quality checks
- File reference integrity validation
- Token efficiency optimization

### Comprehensive Coverage

- **Specialized checklists**: Agents, Skills, CLAUDE.md, Prompts/Commands, Hooks, Settings
- **Reference guides**: Priority framework, security patterns, Claude Code requirements, changeset scope
- **Review examples**: One or more per configuration type, demonstrating proper feedback format
- **Executable security script**: Automated security scanning

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

Under this layout the skill's own directory is `.claude/skills/reviewing-claude-config`, which is where the plugin-install paths below point instead.

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

1. Detect the file type (CLAUDE.md in this case)
2. Execute security scan
3. Load the appropriate checklist
4. Return a structured review, one finding per issue

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

**Review a new skill:**

```
Review .claude/skills/my-new-skill/SKILL.md
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
reviewing-claude-config/
├── SKILL.md                          # Main orchestration file
├── checklists/                       # Specialized review checklists
│   ├── agents.md                     # Agent review checklist
│   ├── claude-md.md                  # CLAUDE.md review checklist
│   ├── hooks.md                      # Hooks schema and command safety
│   ├── prompts.md                    # Prompts/commands checklist
│   ├── settings.md                   # Settings security checklist
│   └── skills.md                     # Skill review checklist
├── reference/                        # Reference materials (loaded on-demand)
│   ├── claude-code-requirements.md   # YAML, tools, models, limits
│   ├── priority-framework.md         # Issue classification system
│   ├── security-patterns.md          # Security checks and remediation
│   └── validate-ai-scope.md          # Changeset scope and report contract
├── examples/                         # Sample review outputs
│   ├── example-agent-composition-review.md # Agent invocation and dependency review
│   ├── example-agent-review.md       # Agent configuration review example
│   ├── example-claude-md-review.md   # CLAUDE.md review example
│   ├── example-hooks-review.md       # Hooks review example
│   ├── example-prompts-review.md     # Prompts review example
│   ├── example-settings-review.md    # Settings review example
│   └── example-skill-review.md       # Skill review example
├── scripts/                          # Executable automation
│   └── security-scan.sh              # Comprehensive security scanner
└── README.md                         # This file
```

## Review Process

The skill follows a systematic 5-step review process:

1. **Detect File Type**: Determines whether reviewing agents, skills, CLAUDE.md, prompts and commands, hooks, or settings
2. **Execute Security Scan**: Always performs critical security checks first
3. **Load Appropriate Checklist**: Routes to specialized review guidance
4. **Consult References**: Loads detailed criteria only when needed
5. **Document Findings**: Returns one finding per issue, anchored to `file:line`, with a specific fix

### Security Checks (Always First)

Regardless of file type, these checks are performed:

- ✅ settings.local.json NOT in git
- ✅ No hardcoded credentials
- ✅ Permissions appropriately scoped
- ✅ No dangerous command auto-approvals

If any security check fails, it's flagged as **CRITICAL** immediately.

### Priority Levels

Issues are classified into four priority levels:

- **CRITICAL**: Prevents functionality, exposes security vulnerabilities (must fix)
- **IMPORTANT**: Significantly impacts quality or maintainability (should fix)
- **SUGGESTED**: Nice-to-have improvements (optional)
- **OPTIONAL**: Personal preferences (author decides)

## Requirements

- Claude Code (tested with latest version)
- Git (for committed file detection in security scan)
- Bash (for security-scan.sh script)

## Configuration

This skill works out-of-the-box with no configuration needed. It's 100% generic and supports any project type or language.

### Customization

If you want to customize for your organization:

1. **Modify checklists**: Add project-specific requirements to checklist files
2. **Adjust security patterns**: Add organization-specific secret patterns to `security-scan.sh`
3. **Update priority framework**: Adjust severity levels based on team standards

**Note**: Keep changes generic to maintain portability if sharing with other teams.

## Examples

Review examples per configuration type, each demonstrating the feedback format:

- `examples/example-agent-review.md` - Agent review with security and quality issues
- `examples/example-agent-composition-review.md` - Agent invocation patterns and a circular-dependency anti-pattern
- `examples/example-skill-review.md` - Skill review with multiple issues
- `examples/example-claude-md-review.md` - CLAUDE.md review with duplication
- `examples/example-hooks-review.md` - Hooks review with shell injection and prompt-hook findings
- `examples/example-settings-review.md` - Settings review with security concerns
- `examples/example-prompts-review.md` - Prompts review with quality improvements

### Review Output Format

Each review follows this structure. Findings are returned as text by default; an invoking
context that holds a comment-posting grant can post one comment per finding instead, and the
two `validate-ai` commands write the single-document report contract in
`reference/validate-ai-scope.md`.

**Findings**, one per issue:

```
**file:line** - PRIORITY: Issue description

[Specific fix with code example]

[Rationale explaining why this matters]
```

**Overall assessment**, stated once:

```
**Overall Assessment:** APPROVE / REQUEST CHANGES

[Findings grouped by priority: CRITICAL → IMPORTANT → SUGGESTED → OPTIONAL]
```

### Priority Levels

- **CRITICAL** - Prevents functionality, security vulnerabilities (must fix)
- **IMPORTANT** - Significant quality/maintainability impact (should fix)
- **SUGGESTED** - Nice-to-have improvements (could fix)
- **OPTIONAL** - Personal preferences, alternatives (consider)

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

- **Chain of Thought prompting**: 40% error reduction (Anthropic)
- **Progressive disclosure**: <500 line main files (Anthropic)
- **Structured thinking**: Systematic analysis before feedback
- **Security-first approach**: Critical checks before quality review

See `reference/claude-code-requirements.md` for the requirements these criteria are drawn from.

## Troubleshooting

### Skill Not Recognized

**Issue**: Claude doesn't invoke the skill automatically

**Solutions:**

1. Verify YAML frontmatter exists in `SKILL.md`
2. Check skill name is `reviewing-claude-config`
3. Ensure file is in `.claude/skills/reviewing-claude-config/`
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

1. Security scan excludes `examples/` and `security-patterns.md`
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
- **MINOR**: New features, new checklists, backward-compatible changes
- **PATCH**: Bug fixes, documentation updates, minor improvements

The skill ships with the plugin and carries the plugin's version. See
[`../../CHANGELOG.md`](../../CHANGELOG.md) for version history.

## Support

For issues, questions, or feedback:

1. Check troubleshooting section above
2. Review the examples in `examples/`
3. Consult reference files for detailed guidance
4. Contact your team's Claude Code administrator

## Acknowledgments

Built with research-backed best practices from:

- Anthropic Official Documentation (Chain of Thought, Progressive Disclosure)
- Claude Code Best Practices
- Security best practices for credential detection
- Prompt engineering quality standards
