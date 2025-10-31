# Emphasis

Proper formatting highlights critical information and organizes content.

---

## Definition

Proper formatting highlights critical information and organizes content.

## Good Emphasis

✅ **PROPER FORMATTING:**
```markdown
**CRITICAL**: All skills MUST have YAML frontmatter

Required fields:
- `name`: kebab-case skill identifier
- `description`: Clear purpose with activation triggers

**Without frontmatter, skill won't be recognized.**
```

✅ **VISUAL HIERARCHY:**
```markdown
# Main Topic

## Subtopic

### Specific Requirement

**Critical:** [urgent information]

- [ ] Checklist item
```

## Poor Emphasis

❌ **WALL OF TEXT:**
```markdown
All skills must have YAML frontmatter or they won't be recognized by Claude Code. The frontmatter requires a name field which should be in kebab-case format and a description field that clearly states the purpose and when to use the skill.
```

❌ **OVER-EMPHASIS:**
```markdown
**CRITICAL IMPORTANT URGENT: This is very very important!!!**
```

## Formatting Techniques

**Bold:**
- `**CRITICAL**`, `**IMPORTANT**` for priority levels
- `**Required**`, `**Optional**` for field requirements
- Key terms in first introduction

**Code Formatting:**
- `` `technical terms` `` for inline code/commands
- ` ```language ` blocks for multi-line code
- File paths: `` `.claude/settings.json` ``

**Lists:**
- Bulleted lists for unordered items
- Numbered lists for sequential steps
- Checklists `- [ ]` for validation items

**Headers:**
- `#` for major sections
- `##` for subsections
- `###` for specific topics
