# Example Agent Configuration Reviews

Reviews of individual agent configuration files: tool access, model selection, and system prompt quality.

For reviews of how agents are invoked and composed, see `example-agent-composition-review.md`.

---

## Example 1: Security Issues and Over-Privileged Access

**Context:** Reviewing a new documentation-writer agent with security concerns.

### Agent Configuration

**File:** `.claude/agents/documentation-writer.md`

```yaml
---
name: documentation-writer
description: Helps write documentation.
---
Write good documentation for code.
```

### Findings

**`.claude/agents/documentation-writer.md:3`** - IMPORTANT: Description lacks activation triggers

Current description is too vague and doesn't specify when to use this agent.

Recommended:

```yaml
description: Generates API documentation and code comments for TypeScript projects. Use when documenting functions, classes, or REST endpoints in .ts files.
```

Specific activation triggers improve automatic delegation and discoverability.

Reference: Anthropic Subagent Documentation - Description Best Practices

---

**`.claude/agents/documentation-writer.md:1-6`** - CRITICAL: Missing tools field - inherits all tools including Bash

Agent has no `tools` field, meaning it inherits ALL tools including destructive operations.

Recommended:

```yaml
---
name: documentation-writer
description: Generates API documentation and code comments for TypeScript projects. Use when documenting functions, classes, or REST endpoints in .ts files.
tools: Read, Grep, Glob, Write
---
```

Rationale:

- Read/Grep/Glob: Analyze code to document
- Write: Create documentation files
- NO Edit: Doesn't modify source code
- NO Bash: Documentation doesn't require command execution

Security principle: Grant minimum necessary tools only.

Reference: `../reference/claude-code-requirements.md` - "Tool Access Patterns"

---

**`.claude/agents/documentation-writer.md:6`** - IMPORTANT: System prompt lacks structure and guidance

Current prompt is too brief and unstructured.

Recommended:

```markdown
# Documentation Writer Agent

## Role

You are a documentation specialist focused on creating clear, comprehensive API documentation for TypeScript projects.

## Process

<thinking>
Before documenting:
1. What is the function/class purpose?
2. What are the parameters and return types?
3. What are the edge cases or error conditions?
4. Are there usage examples needed?
</thinking>

## Output Format

Use JSDoc format:
\`\`\`typescript
/\*\*

- [Brief description]
-
- @param {Type} paramName - Parameter description
- @returns {Type} Return value description
- @throws {ErrorType} When error occurs
- @example
- // Usage example
  \*/
  \`\`\`

## Examples

[Include 2-3 examples of good documentation]
```

Structured thinking reduces errors (Anthropic Chain of Thought guidance).

---

**`.claude/agents/documentation-writer.md:1-6`** - SUGGESTED: Add model selection

Consider specifying model for cost/performance optimization:

```yaml
---
name: documentation-writer
description: ...
tools: Read, Grep, Glob, Write
model: sonnet # Or haiku for simple documentation
---
```

Documentation generation is moderately complex (Sonnet) but could use Haiku for speed if following strict templates.

Reference: `../reference/claude-code-requirements.md` - "Model Selection"

---

### Summary

**Overall Assessment:** Issues found

This agent requires fixes before approval:

**Must Fix (CRITICAL):**

- Add tools field with minimum required access (prevent security risk)

**Should Fix (IMPORTANT):**

- Improve description with specific activation triggers
- Add structured system prompt with examples

**Nice to Have (SUGGESTED):**

- Specify model selection

Once security issues are addressed and description improved, this will be ready for use.

---

## Example 2: Well-Configured Agent with Minor Suggestions

**Context:** Reviewing a production-ready security-scanner agent.

### Agent Configuration

**File:** `plugins/security-tools/agents/security-scanner.md`

```yaml
---
name: security-scanner
description: Analyzes code for security vulnerabilities including SQL injection, XSS, and authentication bypass. PROACTIVELY invoke when reviewing authentication, database queries, or user input handling.
tools: Read, Grep, Glob
model: sonnet
version: 1.0.0
---

# Security Scanner Agent

## Role
You are a security analysis specialist focused on identifying vulnerabilities in web applications.

## Capabilities
- SQL injection detection (parameterized queries, raw SQL)
- XSS vulnerability identification (unescaped output, DOM manipulation)
- Authentication bypass patterns (token validation, session handling)
- CSRF vulnerability detection
- Insecure cryptography usage
- Sensitive data exposure

## Process

<thinking>
Before analyzing each file:
1. What is the file's purpose (auth, API, database)?
2. What are the main security risks for this component?
3. Are there user inputs that need validation?
4. Are outputs properly escaped?
5. Is authentication/authorization properly implemented?
</thinking>

Then execute:
1. Read file and understand context
2. Identify all user input points
3. Trace data flow through functions
4. Check for security anti-patterns
5. Verify proper validation and sanitization
6. Document findings with severity and fix recommendations

## Output Format

**file.py:42** - CRITICAL: [Vulnerability type]

[Specific fix with secure code example]

[Rationale explaining security impact and OWASP category]

## Examples

### Example 1: SQL Injection
**api/users.py:78** - CRITICAL: SQL injection vulnerability

Current code uses string concatenation for SQL query:
\`\`\`python
query = f"SELECT * FROM users WHERE id = {user_id}"
\`\`\`

Fix with parameterized query:
\`\`\`python
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
\`\`\`

Rationale: String concatenation allows SQL injection attacks. Parameterized queries prevent this by properly escaping inputs. (OWASP A03:2021 - Injection)

### Example 2: XSS Vulnerability
**templates/profile.html:23** - CRITICAL: Cross-site scripting (XSS)

Current code outputs user data without escaping:
\`\`\`html
<div>{{ user.bio }}</div>
\`\`\`

Fix with auto-escaping:
\`\`\`html
<div>{{ user.bio | escape }}</div>
\`\`\`

Rationale: Unescaped user input allows script injection. Template escaping prevents XSS attacks. (OWASP A03:2021 - Injection)

## Constraints
- Focus ONLY on security issues
- Do not report code style or general quality issues
- Prioritize by severity: CRITICAL > HIGH > MEDIUM > LOW
- Provide specific fix for each finding
- Reference OWASP category where applicable
```

### Findings

**`plugins/security-tools/agents/security-scanner.md:1-8`** - OPTIONAL: Excellent configuration

This agent configuration demonstrates security best practices:

✅ Specific, descriptive name
✅ Clear description with activation triggers ("PROACTIVELY invoke when...")
✅ Minimal tool access (Read, Grep, Glob only - appropriate for analysis)
✅ Explicit model selection (Sonnet for balanced analysis)
✅ Comprehensive system prompt with examples
✅ Structured thinking guidance
✅ Clear output format specification
✅ Security-focused constraints

No changes required. This is a reference-quality agent configuration.

---

**`plugins/security-tools/agents/security-scanner.md:15-25`** - OPTIONAL: Consider additional capabilities

Current capabilities are comprehensive for web applications. For even broader coverage, consider adding:

- Container/Docker security misconfigurations
- API security (rate limiting, API key exposure)
- Dependency vulnerability scanning
- Security header validation

However, keeping focused scope (current approach) may be preferable for clarity and single responsibility principle.

This is a design choice - current scope is excellent.

---

### Summary

**Overall Assessment:** Pass

This is an exemplary agent configuration that demonstrates:

- Security best practices (minimal tool access)
- Clear activation triggers for automatic delegation
- Comprehensive system prompt with structured thinking
- Concrete examples demonstrating expected output
- Appropriate model selection
- Focused single responsibility

No changes required. Consider this a reference implementation for security analysis agents.

---

## Example 3: Agent with Wrong Model Selection

**Context:** Reviewing a code formatter agent.

### Agent Configuration

**File:** `.claude/agents/code-formatter.md`

```yaml
---
name: code-formatter
description: Formats code according to project style guides.
tools: Read, Write, Edit
model: opus
---
Format code files using project style guide.
```

### Findings

**`.claude/agents/code-formatter.md:5`** - IMPORTANT: Model selection inappropriate for task

Current configuration uses `opus` for code formatting, which is expensive overkill.

Recommended:

```yaml
model: haiku # Fast and cost-effective for mechanical tasks
```

Rationale:

- Code formatting is mechanical, doesn't require complex reasoning
- Haiku is 10x+ faster and significantly cheaper
- Opus should be reserved for complex architectural decisions
- This agent will be invoked frequently (cost multiplier)

Reference: `../reference/claude-code-requirements.md` - "Model Selection"

---

**`.claude/agents/code-formatter.md:4`** - IMPORTANT: Tool access includes unnecessary Edit

Code formatter likely creates formatted versions, doesn't need Edit for in-place modification.

Recommended:

```yaml
tools: Read, Write # Remove Edit
```

Or if in-place formatting is required:

```yaml
tools: Read, Edit # Remove Write
```

Clarify in system prompt whether agent:

- Reads and writes new formatted files (Read, Write)
- Modifies files in place (Read, Edit)

Reference: `../reference/claude-code-requirements.md` - "Tool Access Patterns"

---

**`.claude/agents/code-formatter.md:7`** - IMPORTANT: System prompt lacks specification

Current prompt doesn't specify:

- Which style guide to use
- What file types to format
- Output format expectations

Recommended:

```markdown
# Code Formatter Agent

## Role

Format code files according to project style guides automatically.

## Supported Languages

- Python: Black formatter (PEP 8)
- TypeScript: Prettier (project .prettierrc)
- Go: gofmt

## Process

1. Read file and detect language
2. Apply appropriate formatter rules
3. Write formatted output
4. Report files formatted and any errors

## Output

- List of files successfully formatted
- Any files skipped (unsupported language, errors)
- Summary of changes made
```

Clear specification prevents ambiguous behavior.

---

### Summary

**Overall Assessment:** Issues found

**Must Fix (IMPORTANT):**

- Change model from opus to haiku (cost/performance)
- Clarify tool access (Write OR Edit, not both)
- Add comprehensive system prompt

Formatting is a high-frequency operation. Wrong model selection will significantly impact cost and latency at scale.

---

## Key Takeaways

### Excellent Agent Patterns

1. **Minimal tool access** - Grant only necessary tools
2. **Specific descriptions** - Include activation triggers
3. **Structured system prompts** - Use thinking blocks and examples
4. **Appropriate model** - Match complexity to cost/performance
5. **Clear constraints** - Define what agent doesn't do

### Common Mistakes

1. **Over-privileged** - Inheriting all tools unnecessarily
2. **Vague descriptions** - No activation triggers
3. **Wrong model** - Opus for simple tasks, Haiku for complex
4. **Poor prompts** - No structure, examples, or guidance
5. **Scope creep** - Trying to do too many things

### Security Priorities

1. **Always specify tools** unless all tools genuinely needed
2. **Justify Bash access** explicitly in system prompt
3. **Read-only for analysis** agents
4. **Document security implications** of tool choices

---
