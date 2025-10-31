# Agent Tool Access and Security

Comprehensive guide on tool access security, appropriate tool combinations, and secure patterns for agent configurations.

**Source:** [Anthropic - Claude Code Subagents Documentation](https://docs.claude.com/en/docs/claude-code/sub-agents.md)

**Related References:**
- `agent-configuration.md` - Model selection and naming conventions
- `agent-system-prompts.md` - System prompt engineering patterns

---

## Tool Access Security Matrix

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

## Secure Tool Access Patterns

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

## Resources

- [Anthropic - Subagent Documentation](https://docs.claude.com/en/docs/claude-code/sub-agents.md)
- [Anthropic - Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- `agent-configuration.md` - Model selection and validation
- `agent-system-prompts.md` - Prompt engineering patterns
