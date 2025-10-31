# Structure

Logical organization that aids comprehension and navigation.

---

## Definition

Logical organization that aids comprehension and navigation.

## Good Structure

✅ **LOGICAL FLOW:**
```markdown
# Skill Name

## Purpose
[What this does and when to use it]

## Instructions

### Step 1: [First Action]
[Details]

### Step 2: [Second Action]
[Details]

## Examples
[Concrete examples]

## Common Issues
[Troubleshooting]
```

✅ **PROGRESSIVE DISCLOSURE:**
```markdown
# Main Skill (≤500 lines)
- High-level overview
- Decision routing logic
- References to detailed files

# Supporting Files
- Loaded on-demand
- Self-contained
- Specific deep-dives
```

## Poor Structure

❌ **NO ORGANIZATION:**
```markdown
Here's a bunch of information about the skill. It does various things...
[unstructured content continues]
```

❌ **INVERTED PRIORITY:**
```markdown
[500 lines of detailed implementation patterns]

## Purpose
Oh by the way, this skill reviews code.
```

## Structural Patterns

**Top-Down:**
1. Purpose and activation (what and when)
2. High-level approach (how)
3. Specific details (detailed guidance)
4. Examples (concrete demonstrations)

**Multi-Pass:**
1. First pass: Critical security checks
2. Second pass: Structure validation
3. Third pass: Quality review
4. Fourth pass: Optimization

**Routing:**
1. Detect type
2. Route to appropriate checklist
3. Checklists contain specific guidance
4. Reference files for deep dives
