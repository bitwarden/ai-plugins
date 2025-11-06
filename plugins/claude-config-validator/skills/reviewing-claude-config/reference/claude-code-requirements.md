# Claude Code Requirements

Claude Code-specific conventions, formats, and requirements that differ from general best practices. This reference consolidates domain-specific knowledge necessary for validating Claude Code configuration files.

---

## YAML Frontmatter Format

### Skills (SKILL.md files)

**Required Fields:**
```yaml
---
name: skill-name-in-kebab-case
description: Clear description with activation triggers
---
```

**Optional Fields:**
```yaml
version: 1.0.0  # Semver format (MAJOR.MINOR.PATCH)
```

**Field Requirements:**
- `name`: **MUST** be kebab-case (use-dashes-not_underscores)
- `description`: **MUST** include activation triggers (when to use the skill)
- `version`: **SHOULD** follow semantic versioning if marketplace-bound
- **NO TABS**: Use spaces only (YAML requirement)

**Valid Example:**
```yaml
---
name: reviewing-changes
version: 2.0.0
description: Comprehensive code reviews for Android. Detects change type and applies appropriate review depth. Use when reviewing pull requests, checking commits, or analyzing code changes.
---
```

**Invalid Examples:**
```yaml
---
name: reviewing_changes  # ❌ Underscore instead of dash
description: Reviews code  # ❌ Too vague, no activation triggers
---
```

---

### Agents (.claude/agents/*.md or plugins/*/agents/*.md)

**Required Fields:**
```yaml
---
name: agent-name-in-kebab-case
description: Clear description of agent purpose
---
```

**Optional Fields:**
```yaml
model: sonnet  # haiku, sonnet, opus, or inherit
tools: Read, Write, Grep, Glob, Bash  # Specific tools only
```

**Field Requirements:**
- `name`: kebab-case, unique within project
- `description`: Clear purpose and activation context
- `model`: One of: `haiku`, `sonnet`, `opus`, `inherit` (lowercase)
- `tools`: Exact tool names (case-sensitive): `Read`, `Write`, `Edit`, `Grep`, `Glob`, `Bash`, `WebFetch`, `WebSearch`
- **Omit `tools` field** to inherit all tools (default)

---

## Model Selection

### Valid Model Values

| Model | Value | Use Case |
|-------|-------|----------|
| Haiku | `haiku` | Fast, simple tasks (formatting, scripts, quick operations) |
| Sonnet | `sonnet` | Balanced default (code review, testing, documentation) |
| Opus | `opus` | Complex reasoning (architecture, novel problems) |
| Inherit | `inherit` | Use parent session's model |

**Default**: If `model` field omitted, defaults to `sonnet`

---

## Tool Access Patterns

### Tool Names (Case-Sensitive)

**Read-Only Tools** (LOW RISK):
- `Read` - Read file contents
- `Grep` - Search file contents
- `Glob` - Find files by pattern

**Write Tools** (MEDIUM RISK):
- `Write` - Create new files
- `Edit` - Modify existing files

**Execution Tools** (HIGH RISK):
- `Bash` - Execute shell commands

**Network Tools** (MEDIUM-HIGH RISK):
- `WebFetch` - Fetch URL content
- `WebSearch` - Search web

### Tool Access Security

**Read-only agents** (safest pattern):
```yaml
tools: Read, Grep, Glob
```

**Write-capable agents** (moderate risk):
```yaml
tools: Read, Grep, Glob, Write, Edit
```

**Full-access agents** (highest risk - justify in review):
```yaml
# Omit tools field to inherit all tools
# OR explicitly list all needed tools
```

### Tool Security Guidelines

1. **Principle of Least Privilege**: Only grant tools agent actually needs
2. **Read-Only by Default**: Start with `Read, Grep, Glob` and add tools as needed
3. **Justify Bash Access**: Bash tool = arbitrary code execution, requires strong justification
4. **Omit for Full Access**: Omitting `tools` field grants all tools (document why this is necessary)

---

## Progressive Disclosure

### 500-Line Guideline

**Main skill file** (SKILL.md):
- **Target**: ≤500 lines
- **Maximum**: 500 lines is guideline, not hard limit
- **Rationale**: Context window efficiency, cognitive load management

**If exceeding 500 lines**:
- Split into supporting files
- Use on-demand loading pattern
- Organize into subdirectories

### File Organization Pattern

```
skill-name/
├── SKILL.md              # Main orchestration (aim for ≤500 lines)
├── checklists/           # Task-specific procedures
├── reference/            # Detailed criteria (loaded as needed)
├── examples/             # Sample outputs
└── scripts/              # Executable automation (if applicable)
```

### On-Demand Loading

**Main file should:**
- Provide routing logic (which file to load when)
- Reference supporting files explicitly
- Use structured thinking to guide decisions

**Supporting files should:**
- Be self-contained (understandable in isolation)
- State clear purpose at top
- Avoid circular dependencies

**Example routing:**
```markdown
### Step 2: Load Appropriate Checklist

Based on detected type, read the relevant checklist:

- **Agents** → `checklists/agents.md`
- **Skills** → `checklists/skills.md`
- **Settings** → `checklists/settings.md`
```

---

## Security Conventions

### settings.local.json

**CRITICAL**: `settings.local.json` must **NEVER** be committed to git

**Detection**:
```bash
git status | grep "settings.local.json"
git diff --cached | grep "settings.local.json"
```

**If found**: Flag as **CRITICAL** blocking issue

**Rationale**: Contains user-specific settings and potentially sensitive paths

---

### Auto-Approved Tool Patterns

**Format** (in settings.json):
```json
{
  "autoApproved": [
    "Bash(git status:*)",
    "Bash(git diff:*)",
    "Read(/absolute/path/to/specific/dir/**)"
  ]
}
```

**Guidelines**:
- Use specific command patterns, not wildcards: `Bash(git status:*)` not `Bash(*)`
- Use absolute paths for Read permissions: `Read(/full/path/**)` not `Read(**)`
- Glob patterns for restricted access: `Read(/project/src/**/*.ts)` to limit file types

---

## Common Validation Issues

### YAML Errors

| Issue | Detection | Fix |
|-------|-----------|-----|
| Tabs instead of spaces | Malformed YAML error | Replace tabs with spaces |
| Missing colon | Parser error | Add `:` after field name |
| Wrong field name | Skill not recognized | Check exact spelling: `name` not `Name` |
| Invalid model value | Ignored or error | Use: `haiku`, `sonnet`, `opus`, `inherit` |

### Tool Access Errors

| Issue | Detection | Fix |
|-------|-----------|-----|
| Wrong tool name | Tool not available | Use exact case: `Grep` not `grep` |
| Typo in tool name | Tool not available | Check spelling: `Bash` not `bash` |
| Over-privileged | Security review | Remove unnecessary tools |

### Progressive Disclosure Violations

| Issue | Detection | Fix |
|-------|-----------|-----|
| Main file >500 lines | Line count | Split into supporting files |
| All context loaded upfront | Review structure | Use on-demand loading |
| Circular dependencies | File references | Reorganize file structure |

---

## Validation Checklist

**YAML Frontmatter**:
- [ ] `name` field present and kebab-case
- [ ] `description` field present with activation triggers
- [ ] `version` follows semver (if present)
- [ ] `model` is valid value: `haiku`/`sonnet`/`opus`/`inherit` (if present)
- [ ] `tools` uses exact case-sensitive names (if present)
- [ ] No tabs (spaces only)
- [ ] Valid YAML syntax

**Progressive Disclosure**:
- [ ] Main SKILL.md file ≤500 lines
- [ ] Supporting files organized in subdirectories
- [ ] On-demand loading pattern used
- [ ] File references are correct and exist

**Security**:
- [ ] No settings.local.json committed
- [ ] No hardcoded credentials or API keys
- [ ] Tool access follows least privilege principle
- [ ] Bash access justified if granted

**File Organization**:
- [ ] Skills: `SKILL.md` with YAML frontmatter
- [ ] Agents: `.claude/agents/*.md` or `plugins/*/agents/*.md`
- [ ] Prompts: `.claude/prompts/*.md` or `.claude/commands/*.md`
- [ ] Settings: `.claude/settings.json` (NOT settings.local.json)

---

## Quick Reference

**Model Values**: `haiku` | `sonnet` | `opus` | `inherit`

**Tool Names**: `Read` | `Write` | `Edit` | `Grep` | `Glob` | `Bash` | `WebFetch` | `WebSearch`

**Line Limit**: SKILL.md ≤500 lines (guideline)

**Naming**: kebab-case for `name` fields

**NEVER Commit**: `settings.local.json`

**YAML**: Spaces only, no tabs
