# Claude Config Validator Plugin

Comprehensive validation for Claude Code configuration files, ensuring security, structure, and quality standards across all configuration types.

## Overview

The Claude Config Validator plugin provides expert-level validation for Claude Code projects, reviewing configuration files with the same rigor as human code reviewers. It catches security vulnerabilities, structural issues, and quality problems before they impact your AI-assisted development workflows.

## Features

### Comprehensive Configuration Coverage

Validates these configuration file types, each with its own checklist except where noted:

| Configuration Type                                                                    | What Gets Validated                                                                                                                                   |
| ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Agents** (`.claude/agents/*.md`)                                                    | YAML frontmatter, tool access security, model selection, system prompt quality, description clarity                                                   |
| **Skills** (skill directories)                                                        | Progressive disclosure, file organization, YAML validation, structured thinking patterns, token efficiency                                            |
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
- ✅ Detection of dangerous command patterns in hooks/scripts

### Evidence-Based Quality Standards

All validation criteria sourced from **official Anthropic documentation**:

- Agent tool access security matrices
- Progressive disclosure guidelines (500-line target per file)
- Model selection decision trees (haiku/sonnet/opus)
- System prompt engineering patterns
- Token efficiency optimization

### Multi-Pass Review Strategy

The skill works through five steps:

1. **Detect File Type** - Determines which checklists apply
2. **Security Scan** - Critical checks first (prevents wasted effort on insecure configs)
3. **Load Checklist** - Routes to the checklist for the detected type
4. **Consult References** - Loads detailed criteria only when needed
5. **Document Findings** - One finding per issue, anchored to `file:line`

Each checklist then runs its own multi-pass strategy over the file under review.

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
2. Select appropriate validation checklists
3. Execute security-first review
4. Return one finding per issue with file:line references

### Use Cases

#### 1. Pre-Commit Configuration Review

**Scenario**: You've created a new agent configuration and want to ensure it meets security and quality standards before committing.

**Usage**:

```markdown
Review my new agent configuration in .claude/agents/code-analyzer.md
```

**Output**: One finding per issue with specific improvements, security concerns flagged as CRITICAL, quality suggestions as IMPORTANT/SUGGESTED.

---

#### 2. Plugin Marketplace Submission Validation

**Scenario**: You're preparing a plugin for marketplace submission and need to meet elevated quality standards.

**Usage**:

```markdown
Review my plugin configuration in plugins/my-plugin/ for marketplace readiness
```

**Output**: The component files inside `plugins/my-plugin/` reviewed against the agent, skill, command, and hook checklists, with security findings first. Manifest and marketplace-standard checks are not this skill's: `/validate-ai-local` covers those by delegating to `plugin-dev:plugin-validator`.

---

#### 3. Skill Architecture Review

**Scenario**: You've created a complex skill with multiple reference files and want to ensure proper progressive disclosure.

**Usage**:

```markdown
Review my skill at .claude/skills/my-skill/ for progressive disclosure and token efficiency
```

**Output**: File size analysis (500-line guideline), reference organization recommendations, auto-loaded vs on-demand content optimization.

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

**Validates**:

- CLAUDE.md files
- Skills (SKILL.md)
- Agents
- Prompts
- Commands
- Hooks
- Settings

**Capabilities**:

- YAML frontmatter validation
- Progressive disclosure pattern analysis
- Token efficiency assessment
- Security best practice enforcement
- Detection of critical issues (committed secrets, malformed YAML, broken references, oversized files, insecure tool access, unsafe hook commands)

**Validation Strategy**:

- Multi-pass review (structure → security → functionality → quality)
- Evidence-based recommendations (all criteria from official docs)
- Priority-classified feedback (CRITICAL → IMPORTANT → SUGGESTED → OPTIONAL)
- Per-issue findings with specific fixes and rationale

## Validation Coverage Details

### Agent Validation (6-Pass Strategy)

**Pass 1: Structure and YAML Frontmatter**

- Valid YAML syntax (no tabs, proper structure)
- Required fields: `name`, `description`
- Optional fields validated: `tools`, `model`
- System prompt presence and non-empty

**Pass 2: Security and Tool Access**

- Principle of least privilege verification
- Tool access appropriateness (Read/Grep/Glob for analysis, Write/Edit for modification, Bash justification required)
- Over-privileged agent detection
- Dangerous tool combination identification

**Pass 3: Description and Activation Triggers**

- Specificity (clear purpose statement)
- Activation triggers ("Use when...", "PROACTIVELY invoke...")
- Single responsibility principle
- Appropriate scope

**Pass 4: System Prompt Quality**

- Role clarity
- Capability definition
- Structured thinking guidance (`<thinking>` blocks)
- Examples provided
- Output format specification
- Token efficiency

**Pass 5: Model Selection**

- Appropriate model for task complexity (haiku/sonnet/opus/inherit)
- Cost/performance optimization
- Justification for selection

**Pass 6: Marketplace Standards** (if applicable)

- Elevated documentation requirements
- Production readiness
- Error handling
- Example quality

### Skill Validation (5-Pass Strategy)

**Pass 1: Structure and Security**

- Proper file organization
- SKILL.md presence
- Security checks first

**Pass 2: YAML Frontmatter Validation**

- Valid frontmatter with required fields
- Description quality and trigger phrases

**Pass 3: Progressive Disclosure**

- File size limits (500-line guideline for references)
- On-demand vs auto-loaded content
- No broken file references

**Pass 4: Prompt Engineering Quality**

- Clear instructions
- Structured thinking blocks
- Example inclusion and proper emphasis

**Pass 5: Token Efficiency**

- Lean SKILL.md with detail deferred to supporting files
- No duplicated content across tiers

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

### Example 2: Skill Progressive Disclosure Violation

**Input**: Skill with 690-line reference file

**Output**:

```
**.claude/skills/my-skill/reference/patterns.md:1** - IMPORTANT: File exceeds 500-line progressive disclosure guideline

Current: 690 lines (38% over recommended limit)
Guideline: 500 lines maximum for on-demand loading

Impact: Loads an extra 190 lines into context unnecessarily on every use.

Recommended: Split into focused files:
- patterns-security.md (tool access, permissions)
- patterns-configuration.md (model selection, naming)
- patterns-prompts.md (system prompt engineering)

Reference: Progressive Disclosure Best Practices
```

### Example 3: CLAUDE.md Clarity Issue

**Input**: CLAUDE.md with vague instructions

**Output**:

```
**.claude/CLAUDE.md:42** - IMPORTANT: Instruction lacks specificity

Current: "Always write good code"
Issue: "Good code" is subjective and non-actionable.

Recommended:
"Follow these code quality standards:
- Write comprehensive unit tests for all business logic
- Use descriptive variable names (no single letters except loop counters)
- Add inline comments explaining 'why', not 'what'
- Follow project's established patterns in `docs/architecture.md`"

Specific, actionable instructions improve AI behavior (Anthropic prompt engineering guidance).

Reference: `checklists/claude-md.md` - Clarity and Specificity
```

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
│   └── reviewing-claude-config/
│       ├── SKILL.md         # Main skill instructions
│       ├── README.md        # Skill-specific documentation
│       ├── checklists/      # One per configuration type (agents, skills, CLAUDE.md, prompts, hooks, settings)
│       ├── reference/       # Priority framework, security patterns, requirements, changeset scope
│       ├── examples/        # Sample reviews, one or more per configuration type
│       └── scripts/         # Security scan helper (human-run)
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
