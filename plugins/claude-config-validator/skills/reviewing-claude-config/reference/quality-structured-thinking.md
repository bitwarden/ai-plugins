# Structured Thinking

Use `<thinking>` blocks to guide systematic reasoning before actions.

---

## Definition

Use `<thinking>` blocks to guide systematic reasoning before actions.

## Good Structured Thinking

✅ **SYSTEMATIC ANALYSIS:**
```markdown
### Step 1: Detect Change Type

<thinking>
Analyze the changeset systematically:
1. What files were modified? (code vs config vs docs)
2. What is the PR/commit title indicating?
3. Is there new functionality or just modifications?
4. What's the risk level of these changes?
</thinking>

Determine the primary change type:
[detection rules]
```

✅ **DECISION GUIDANCE:**
```markdown
<thinking>
Before writing each comment:
1. Is this issue Critical, Important, or Suggested?
2. Should I ask a question or provide direction?
3. What's the rationale I need to explain?
4. What code example would make this actionable?
</thinking>
```

## Poor Structured Thinking

❌ **NO GUIDANCE:**
```markdown
Review the code and find issues.
[No thinking guidance provided]
```

❌ **POST-HOC THINKING:**
```markdown
[Provides answer immediately]

<thinking>
I guess I should have thought about this first...
</thinking>
```

## Thinking Block Guidelines

**Place Before:**
- Major decisions
- Complex analysis
- Prioritization choices
- Output generation

**Include:**
- Key questions to consider
- Decision criteria
- Systematic approach
- What to evaluate

**Format:**
```markdown
<thinking>
1. [First consideration]
2. [Second consideration]
3. [Decision criteria]
</thinking>

[Then proceed with action based on thinking]
```
