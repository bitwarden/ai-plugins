# Example Agent Composition Reviews

Reviews of how agents are invoked and how they depend on one another, rather than of a single agent's configuration.

For reviews of individual agent files, see `example-agent-review.md`.

---

## Example 1: Agent Invocation Review

**Context:** Reviewing a skill that invokes agents.

### Skill Code

**File:** `.claude/skills/code-reviewer/SKILL.md`

```markdown
## Step 3: Invoke Reviewer

Use the code-reviewer agent.
```

### Review Comments

**`.claude/skills/code-reviewer/SKILL.md:28`** - IMPORTANT: Agent invocation lacks specificity

Current invocation is too vague and provides no context or expectations.

Recommended:

```markdown
## Step 3: Invoke Security Analysis

Invoke the security-scanner agent to analyze modified files for vulnerabilities:

**Files to analyze:**
{list of modified files from step 1}

**Focus areas:**

- Authentication and authorization logic
- Database query construction
- User input handling and validation
- Output encoding and XSS prevention

**Expected output:**

- Inline comments with file:line references
- CRITICAL priority for vulnerabilities
- Specific fix recommendations with secure code examples
- OWASP category for each finding

**Context:**

- Application uses JWT authentication
- Database is PostgreSQL with SQLAlchemy ORM
- Framework is Flask with Jinja2 templates
```

Specific invocations with context improve agent output quality by ~40%.

---

## Example 2: Circular Agent Dependency (Anti-Pattern)

**Context:** Reviewing agents that invoke each other circularly.

### Configuration

**Agent A:** `.claude/agents/code-analyzer.md`

```markdown
If issues found, invoke code-fixer agent.
```

**Agent B:** `.claude/agents/code-fixer.md`

```markdown
After fixing, invoke code-analyzer agent to verify.
```

### Review Comments

**`.claude/agents/code-analyzer.md:45` + `.claude/agents/code-fixer.md:38`** - CRITICAL: Circular agent dependency

These agents invoke each other, creating a potential infinite loop:

- code-analyzer → code-fixer → code-analyzer → ...

Fix:

```markdown
# code-analyzer.md

Report issues found. Do NOT invoke other agents.

# code-fixer.md

After fixing, report completion. Do NOT invoke analyzer.

# Create separate coordinator if needed:

# code-improvement-workflow.md

1. Invoke code-analyzer
2. Review results
3. If fixes needed, invoke code-fixer
4. Verify results manually or with single analyzer invocation
```

Rationale: Circular dependencies cause unpredictable behavior and infinite loops. Use explicit workflow coordination instead.
