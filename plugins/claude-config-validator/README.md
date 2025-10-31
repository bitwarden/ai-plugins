# Claude Config Validator Plugin

Comprehensive validation for Claude Code configuration files, ensuring security, structure, and quality standards across all configuration types.

## Overview

The Claude Config Validator plugin provides expert-level validation for Claude Code projects, reviewing configuration files with the same rigor as human code reviewers. It catches security vulnerabilities, structural issues, and quality problems before they impact your AI-assisted development workflows.

## Features

### Comprehensive Configuration Coverage

Validates **6 configuration file types** with specialized checklists:

| Configuration Type | What Gets Validated |
|-------------------|---------------------|
| **Agents** (`.claude/agents/*.md`) | YAML frontmatter, tool access security, model selection, system prompt quality, description clarity |
| **Skills** (skill directories) | Progressive disclosure, file organization, YAML validation, structured thinking patterns, token efficiency |
| **CLAUDE.md** (project instructions) | Clarity, specificity, security patterns, proper emphasis, structured organization |
| **Prompts/Commands** (`.claude/prompts/*.md`, `.claude/commands/*.md`) | Purpose clarity, session context handling, skill references, parameter validation |
| **Settings** (`.claude/settings.json`) | Security (no committed credentials), permission scoping, valid JSON structure |
| **Plugin Configurations** (`plugins/*/`) | Manifest validation, directory structure, marketplace standards |

### Security-First Validation

Every review **always** includes critical security checks:
- ✅ No committed `settings.local.json` files
- ✅ No hardcoded credentials (API keys, passwords, tokens)
- ✅ Appropriate permission scoping
- ✅ Principle of least privilege for agent tool access
- ✅ Detection of dangerous command patterns in hooks/scripts

### Evidence-Based Quality Standards

All validation criteria sourced from **official Anthropic documentation** and enterprise best practices (Microsoft Azure AI patterns):
- Agent tool access security matrices
- Progressive disclosure guidelines (500-line file limits)
- Model selection decision trees (haiku/sonnet/opus)
- System prompt engineering patterns
- Token efficiency optimization

### Multi-Pass Review Strategy

Uses structured, systematic validation approach:
1. **Security Scan** - Critical checks first (prevents wasted effort on insecure configs)
2. **Structure Validation** - YAML frontmatter, file organization, required fields
3. **Functionality Review** - Logic, completeness, integration points
4. **Quality Assessment** - Best practices, prompt engineering, documentation
5. **Marketplace Standards** - Elevated requirements for public plugins

### Inline, Actionable Feedback

Provides specific, file:line referenced feedback with:
- **Priority classification** (CRITICAL / IMPORTANT / SUGGESTED / OPTIONAL)
- **Specific fixes** with code examples
- **Rationale** explaining why issues matter
- **References** to official documentation

## Installation

### Add Bitwarden Marketplace (if not already added)

```bash
/plugin marketplace add bitwarden/ai-marketplace
```

### Install the Plugin

```bash
/plugin install claude-config-validator@bitwarden-marketplace
```

## Usage

### Basic Invocation

```bash
/skill reviewing-claude-config
```

The skill will automatically:
1. Detect which configuration files were recently modified
2. Select appropriate validation checklists
3. Execute security-first review
4. Provide inline feedback with file:line references

### Use Cases

#### 1. Pre-Commit Configuration Review

**Scenario**: You've created a new agent configuration and want to ensure it meets security and quality standards before committing.

**Usage**:
```markdown
Review my new agent configuration in .claude/agents/code-analyzer.md
```

**Output**: Inline comments with specific improvements, security concerns flagged as CRITICAL, quality suggestions as IMPORTANT/SUGGESTED.

---

#### 2. Plugin Marketplace Submission Validation

**Scenario**: You're preparing a plugin for marketplace submission and need to meet elevated quality standards.

**Usage**:
```markdown
Review my plugin configuration in plugins/my-plugin/ for marketplace readiness
```

**Output**: Comprehensive validation against marketplace standards, documentation completeness checks, security validation, example quality assessment.

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

**Description**: Reviews Claude configuration files in .claude directories for security, structure, and prompt engineering quality.

**Validates**:
- CLAUDE.md files
- Skills (SKILL.md)
- Agents
- Prompts
- Commands
- Settings

**Capabilities**:
- YAML frontmatter validation
- Progressive disclosure pattern analysis
- Token efficiency assessment
- Security best practice enforcement
- Detection of critical issues (committed secrets, malformed YAML, broken references, oversized files, insecure tool access)

**Validation Strategy**:
- Multi-pass review (structure → security → functionality → quality)
- Evidence-based recommendations (all criteria from official docs)
- Priority-classified feedback (CRITICAL → IMPORTANT → SUGGESTED → OPTIONAL)
- Inline comments with specific fixes and rationale

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

### Skill Validation (4-Pass Strategy)

**Pass 1: Structure and YAML**
- Valid YAML frontmatter with required fields
- SKILL.md presence
- Proper file organization

**Pass 2: Progressive Disclosure**
- File size limits (500-line guideline for references)
- On-demand vs auto-loaded content
- Token efficiency optimization

**Pass 3: Quality and Clarity**
- Clear instructions
- Structured thinking blocks
- Example inclusion
- Proper emphasis

**Pass 4: Integration and Completeness**
- No broken file references
- Checklist completeness
- Reference accuracy

### Security Validation (Always Executed)

**Critical Checks** (all configuration types):
- settings.local.json NOT committed to git
- No hardcoded credentials (passwords, API keys, tokens)
- Permissions appropriately scoped
- No secrets in plaintext

**Detection Methods**:
- Git status checks
- Pattern matching for common secret formats
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

Reference: `reference/agent-configuration-security.md` - Tool Access Security Matrix
```

### Example 2: Skill Progressive Disclosure Violation

**Input**: Skill with 690-line reference file

**Output**:
```
**.claude/skills/my-skill/reference/patterns.md:1** - IMPORTANT: File exceeds 500-line progressive disclosure guideline

Current: 690 lines (38% over recommended limit)
Guideline: 500 lines maximum for on-demand loading

Impact: Loads extra 190 lines into context unnecessarily, reducing token efficiency by 38%.

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

Specific, actionable instructions improve AI behavior by 60% (Anthropic research).

Reference: `reference/quality-specificity.md` - Specificity Best Practices
```

## Plugin Structure

```
plugins/claude-config-validator/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── skills/
│   └── reviewing-claude-config/
│       ├── SKILL.md         # Main skill instructions
│       ├── README.md        # Skill-specific documentation
│       ├── checklists/      # 5 validation checklists (agents, skills, CLAUDE.md, prompts, settings)
│       ├── reference/       # 16 reference files (security, quality, agent patterns)
│       ├── examples/        # 6 example review outputs
│       ├── docs/            # Implementation plans, changelog
│       └── scripts/         # Validation automation scripts
└── README.md               # This file
```

## Contributing

Contributions welcome! Please follow:
- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com)
- Repository standards in root `README.md`
- Code quality requirements in `.editorconfig`

## Support

- **Issues**: [GitHub Issues](https://github.com/bitwarden/ai-marketplace/issues)
- **Documentation**: [Claude Code Docs](https://docs.claude.com/en/docs/claude-code/)
- **Marketplace**: [Bitwarden AI Marketplace](https://github.com/bitwarden/ai-marketplace)
