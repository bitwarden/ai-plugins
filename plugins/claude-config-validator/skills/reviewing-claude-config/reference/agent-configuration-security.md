# Agent Configuration and Security

Comprehensive guide on agent configuration including model selection, naming conventions, system prompt engineering, tool access security, and secure configuration patterns.

**Sources:**
- [Anthropic - Claude Code Subagents Documentation](https://docs.claude.com/en/docs/claude-code/sub-agents.md)
- [Anthropic - Chain of Thought Prompting](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/chain-of-thought)

---

## Table of Contents

**Configuration:**
- [Model Selection](#model-selection) - Haiku, Sonnet, Opus, Inherit
- [Naming Conventions](#naming-conventions) - kebab-case, descriptive names
- [Security Checklists](#security-checklists) - By agent type

**System Prompts:**
- [Prompt Engineering Patterns](#prompt-engineering-patterns) - Proven structures
- [Common Anti-Patterns](#common-anti-patterns) - What to avoid

**Tool Access Security:**
- [Tool Security Matrix](#tool-security-matrix) - Risk levels and appropriate uses
- [Secure Access Patterns](#secure-access-patterns) - By agent type

---

## Model Selection

### Haiku - Fast and Cost-Effective

**Use For:**
- Simple formatting tasks
- Running predefined scripts
- Quick file operations
- Straightforward analysis with clear criteria
- High-volume, repetitive tasks

**Characteristics:**
- Fastest response time
- Lowest cost
- Good for simple, well-defined tasks
- Less capable reasoning

**Example Agents:**
- Code formatter
- Import organizer
- Simple linter
- File converter

---

### Sonnet - Balanced Default

**Use For:**
- Code review
- Bug analysis
- Test generation
- Documentation writing
- Most agent tasks

**Characteristics:**
- Balanced speed and capability
- Default choice for most agents
- Good reasoning ability
- Cost-effective for quality work

**Example Agents:**
- Code reviewer
- Test generator
- Documentation writer
- Refactoring agent

---

### Opus - Maximum Capability

**Use For:**
- Complex architectural decisions
- Novel problem-solving
- High-stakes analysis
- Multi-file complex refactoring
- Creative solution generation

**Characteristics:**
- Slowest response time
- Highest cost
- Best reasoning capability
- Use sparingly and strategically

**Example Agents:**
- Architecture advisor
- Complex migration planner
- Novel algorithm designer
- High-stakes security analyzer

---

### Inherit - Context-Dependent

**Use For:**
- Agents that should match user's model choice
- Context-dependent decision making
- When parent conversation context matters

**Characteristics:**
- Inherits model from parent conversation
- Maintains consistency
- Good for user-facing agents

**Example Agents:**
- Interactive assistant
- Context-aware helper
- User-preference-dependent agents

---

### Model Selection Decision Tree

```
Is the task simple and well-defined?
├─ YES → Haiku
└─ NO → Continue

Is the task highly complex requiring maximum reasoning?
├─ YES → Opus
└─ NO → Continue

Should the agent match user's model preference?
├─ YES → Inherit
└─ NO → Sonnet (default)
```

---

## Naming Conventions

**Format:** lowercase-with-hyphens

**Good Names:**
- `code-reviewer`
- `test-generator`
- `python-linter`
- `git-workflow-helper`

**Bad Names:**
- `CodeReviewer` (not kebab-case)
- `code_reviewer` (use hyphens, not underscores)
- `helper` (too vague)
- `ai-assistant` (too generic)

**Best Practices:**
- Descriptive and specific
- Indicates purpose clearly
- Follows kebab-case convention
- Matches description scope

---

## Security Checklists

### Analysis Agents (Read-Only)
- [ ] Tools: Read, Grep, Glob only
- [ ] No Write, Edit, or Bash access
- [ ] Model: Sonnet or Haiku
- [ ] System prompt: Analysis focus, no modifications

### Generator Agents (Create Files)
- [ ] Tools: Read, Grep, Glob, Write
- [ ] No Edit or Bash unless justified
- [ ] Model: Sonnet
- [ ] System prompt: Creates new files only

### Refactoring Agents (Modify Code)
- [ ] Tools: Read, Grep, Glob, Edit
- [ ] Bash only if needed for testing
- [ ] Model: Sonnet
- [ ] System prompt: Strong safety guardrails

### Automation Agents (Command Execution)
- [ ] Tools: Include Bash with justification
- [ ] System prompt: Specify safe commands
- [ ] Model: Sonnet or Haiku
- [ ] Document dangerous commands to avoid

---

## Prompt Engineering Patterns

### Pattern 1: Structured Role Definition

```markdown
# [Agent Name]

## Role
You are a [specific role] specialized in [specific domain].

## Capabilities
- [Capability 1]
- [Capability 2]
- [Capability 3]

## Constraints
- [What you DON'T do]
- [Boundaries]
```

**Benefit:** Clear scope and expectations

---

### Pattern 2: Process-Driven

```markdown
## Process

<thinking>
Before analyzing, consider:
1. [Key question 1]
2. [Key question 2]
3. [Key question 3]
</thinking>

Then execute these steps:
1. [Step 1]
2. [Step 2]
3. [Step 3]
```

**Benefit:** Systematic approach, 40% fewer errors (Anthropic research)

---

### Pattern 3: Output Format Specification

```markdown
## Output Format

Provide findings in this format:

**file.py:42** - [PRIORITY]: [Issue]

[Specific fix with code example]

[Rationale]
```

**Benefit:** Consistent, parseable output

---

### Pattern 4: Examples-Based

```markdown
## Examples

### Example 1: Good Code
[Example of good pattern]

### Example 2: Issue Found
[Example with problem]

**Your analysis would be:**
[Example output]
```

**Benefit:** Demonstrates expected behavior

---

## Common Anti-Patterns

### Anti-Pattern 1: Over-Privileged Agent

**Problem:**
```yaml
name: documentation-writer
description: Writes documentation
# No tools field - inherits everything including Bash
```

**Fix:**
```yaml
name: documentation-writer
description: Writes documentation
tools: Read, Grep, Glob, Write
```

**Rationale:** Documentation writer doesn't need Bash or Edit

---

### Anti-Pattern 2: Vague Description

**Problem:**
```yaml
description: Helps with code stuff.
```

**Fix:**
```yaml
description: Reviews Python code for PEP 8 style violations and common anti-patterns. Use when analyzing .py files or during pre-commit checks.
```

**Rationale:** Specific triggers enable automatic delegation

---

### Anti-Pattern 3: Wrong Model for Task

**Problem:**
```yaml
name: code-formatter
model: opus  # Expensive overkill for formatting
```

**Fix:**
```yaml
name: code-formatter
model: haiku  # Fast and sufficient
```

**Rationale:** Formatting is mechanical, doesn't need opus reasoning

---

### Anti-Pattern 4: Scope Creep

**Problem:**
```yaml
description: Handles all development tasks including coding, testing, deployment, documentation, and architecture.
```

**Fix:** Split into focused agents:
```yaml
# Agent 1
name: code-reviewer
description: Reviews code for quality issues...

# Agent 2
name: test-generator
description: Generates unit tests...

# Agent 3
name: deployment-helper
description: Assists with deployment tasks...
```

**Rationale:** Single responsibility, clearer delegation

---

### Anti-Pattern 5: Missing Structured Thinking

**Problem:**
```markdown
Review the code and find issues.
```

**Fix:**
```markdown
## Process

<thinking>
Before reviewing, analyze:
1. What is the file's purpose?
2. What are the main risk areas?
3. What patterns should I check?
</thinking>

Then provide your review...
```

**Rationale:** Structured thinking reduces errors by 40%

---

## Tool Security Matrix

### Read Tool - File System Access

**Purpose:** Read files from the file system

**Security Level:** LOW RISK (read-only)

**Safe Uses:**
- Code analysis and review
- Documentation generation
- Data extraction and reporting
- Codebase exploration

**Security Considerations:**
- Can read any file the user has access to
- May expose sensitive information if paths not scoped
- Consider limiting to project directories
- Safe for most analysis tasks

**Appropriate Agents:**
- Code reviewers
- Documentation generators
- Data analysts
- Any read-only analysis agent

---

### Grep Tool - Content Search

**Purpose:** Search file contents using regex patterns

**Security Level:** LOW RISK (read-only)

**Safe Uses:**
- Finding code patterns
- Security vulnerability scanning
- Dependency analysis
- Documentation search

**Security Considerations:**
- Read-only operation
- Can search entire accessible filesystem
- May reveal sensitive data in search results
- Safe for analysis tasks

**Appropriate Agents:**
- Code analyzers
- Security scanners
- Documentation tools
- Pattern detection agents

---

### Glob Tool - Pattern Matching

**Purpose:** Find files by name patterns

**Security Level:** LOW RISK (read-only)

**Safe Uses:**
- Finding files by extension
- Discovering project structure
- Locating configuration files
- Asset management

**Security Considerations:**
- Read-only file discovery
- Returns file paths only
- Safe for all agents needing file discovery

**Appropriate Agents:**
- Any agent needing file discovery
- Project analyzers
- Build tool agents

---

### Write Tool - Create New Files

**Purpose:** Create new files in the filesystem

**Security Level:** MEDIUM RISK (creates files)

**Safe Uses:**
- Test generation
- Documentation creation
- Code scaffolding
- Report generation

**Security Considerations:**
- Can create files anywhere user has write access
- May overwrite existing files if paths conflict
- Should be combined with Read to check for conflicts
- Requires justification for agent purpose

**Appropriate Agents:**
- Test generators
- Documentation writers
- Code scaffolders
- Report generators

**Avoid:**
- Read-only analysis agents (no need to create files)
- Agents that only modify existing code

---

### Edit Tool - Modify Existing Files

**Purpose:** Make targeted edits to existing files

**Security Level:** MEDIUM RISK (modifies files)

**Safe Uses:**
- Code refactoring
- Bug fixing
- Updating documentation
- Configuration changes

**Security Considerations:**
- Modifies existing files (can introduce bugs)
- Should understand code context before editing
- Requires Read access to understand file content
- Higher risk than Write (changes existing code)

**Appropriate Agents:**
- Refactoring agents
- Bug fix agents
- Code updaters
- Migration tools

**Avoid:**
- Pure analysis agents (no need to modify)
- Agents that only create new files (use Write)

---

### Bash Tool - Command Execution

**Purpose:** Execute shell commands

**Security Level:** HIGH RISK (arbitrary command execution)

**Safe Uses:**
- Running tests
- Build operations
- Git operations
- Package management
- Database queries

**Security Considerations:**
- Can execute ANY command user has permission for
- Highest risk tool - requires strong justification
- Should be scoped to specific safe commands if possible
- May cause data loss if misused
- Can trigger network operations
- Requires explicit approval in most settings

**Appropriate Agents:**
- Test runners (./gradlew test, npm test)
- Build automation (make, gradle build)
- Git workflow agents (git status, git log)
- Data analysis agents (SQL queries)
- Deployment automation

**Red Flags:**
- Analysis-only agents with Bash access
- Documentation writers with Bash access
- No clear justification for command execution

**Safe Command Patterns:**
- Read-only: git status, git log, git diff
- Idempotent: npm install, make build
- Test execution: npm test, pytest, ./gradlew test

**Dangerous Commands:**
- Destructive: rm -rf, dd, mkfs
- Force operations: git push --force
- Permission changes: chmod, chown
- Remote code: curl | sh

---

## Secure Access Patterns

### Pattern 1: Read-Only Analysis Agent

**Purpose:** Analyze code without modification

**Tool Access:**
```yaml
tools: Read, Grep, Glob
```

**Security:** LOW RISK

**Examples:**
- Code quality analyzer
- Security vulnerability scanner
- Documentation linter
- Complexity calculator

**Rationale:** Cannot modify anything, safe for analysis

---

### Pattern 2: Test Generator

**Purpose:** Create test files for existing code

**Tool Access:**
```yaml
tools: Read, Grep, Glob, Write
```

**Security:** MEDIUM RISK

**Examples:**
- Unit test generator
- Integration test scaffolder
- E2E test creator

**Rationale:**
- Read/Grep/Glob: Understand existing code
- Write: Create new test files
- No Edit: Doesn't modify source code
- No Bash: Test execution separate concern

---

### Pattern 3: Refactoring Agent

**Purpose:** Modify existing code structure

**Tool Access:**
```yaml
tools: Read, Grep, Glob, Edit
```

**Security:** MEDIUM-HIGH RISK

**Examples:**
- Code modernizer
- Rename refactorer
- Pattern updater

**Rationale:**
- Read/Grep/Glob: Find code to refactor
- Edit: Modify existing files
- No Write: Only modifies existing (safer than creating)
- No Bash: Doesn't execute code

---

### Pattern 4: Automation Agent

**Purpose:** Run commands and coordinate workflows

**Tool Access:**
```yaml
tools: Read, Grep, Bash
```

**Security:** HIGH RISK

**Examples:**
- Test runner
- Build automation
- Git workflow agent
- Deployment coordinator

**Rationale:**
- Read/Grep: Understand project state
- Bash: Execute commands
- Requires careful system prompt to limit commands
- Should specify safe command patterns

---

### Pattern 5: Full-Stack Development Agent

**Purpose:** Complete development tasks end-to-end

**Tool Access:**
```yaml
# No tools field - inherits all tools
```

**Security:** HIGHEST RISK

**Use Cases:**
- Main development assistant
- General-purpose coding agent
- Complex multi-step workflows

**Rationale:**
- Only for agents requiring all capabilities
- Requires comprehensive system prompt
- Should include strong guardrails
- Appropriate for primary assistant only

**Warning:** Most agents should NOT use this pattern. Apply principle of least privilege.

---

## Validation Quick Reference

**CRITICAL Issues:**
- Missing YAML frontmatter
- Invalid field types
- Security vulnerabilities (over-privileged access)
- Dangerous tool combinations without justification

**IMPORTANT Issues:**
- Vague descriptions (no activation triggers)
- Poor system prompts
- Inappropriate model selection
- Missing structured thinking

**SUGGESTED Issues:**
- Could add more examples
- Token efficiency improvements
- Alternative patterns available

---

## Resources

- [Anthropic - Subagent Documentation](https://docs.claude.com/en/docs/claude-code/sub-agents.md)
- [Anthropic - Chain of Thought Prompting](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/chain-of-thought)
- [Anthropic - Prompt Engineering Overview](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview)
- [Anthropic - Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
