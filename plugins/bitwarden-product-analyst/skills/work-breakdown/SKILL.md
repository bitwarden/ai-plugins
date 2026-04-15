---
name: work-breakdown
description: Break down features and requirements into actionable, implementable tasks with clear scope and acceptance criteria. Use when planning implementation, organizing complex work, or creating task lists. Trigger phrases: "break down tasks", "create work plan", "organize implementation", "plan development". This skill works best when preceded by `requirements-elicitation` skill use.
---

# Work Breakdown

## Key Capabilities

1. **Task Identification** — Identify discrete, implementable work units from high-level requirements
2. **Dependency Analysis** — Determine task order, relationships, and blocking dependencies
3. **Scope Definition** — Create clear, bounded task descriptions with acceptance criteria
4. **Phase Organization** — Group related tasks into logical implementation phases

## Approach

### 1. Read and Understand Requirements

- Review the complete requirements document
- Understand the full scope and all success criteria
- Identify major components and subsystems affected
- Note security requirements and constraints

### 2. Identify System Components

- What parts of the codebase are affected?
- Which APIs, services, databases, UIs need changes?
- What external systems or dependencies are involved?
- Are multiple platforms affected (web, desktop, mobile, CLI)?

### 3. Break into Phases

Organize work into logical phases:

**Phase 1: Architecture & Design**

- Design system architecture and data models
- Create sequence diagrams, data flow diagrams
- Define API contracts and interfaces
- Security threat modeling (if applicable)

**Phase 2: Implementation**

- Core functionality development
- Database schema changes
- API endpoint creation
- UI component development
- Integration work

**Phase 3: Testing**

- Unit test development
- Integration test development
- End-to-end test scenarios
- Security testing (if applicable)
- Cross-platform verification

**Phase 4: Documentation & Deployment**

- User documentation
- API documentation
- Deployment procedures
- Migration scripts (if needed)

### 4. Define Individual Tasks

Each task should be:

- **Right-sized**: Completable in 2-8 hours (not days)
- **Independent**: Can be worked on without blocking on other incomplete tasks (except explicit dependencies)
- **Testable**: Has clear acceptance criteria that can be verified
- **Specific**: Clear description of what needs to be done
- **Assigned**: Identified role or team (e.g., "Backend team", "Security team", "QA")

### 5. Identify Dependencies

- What tasks must be completed before others can start?
- Are there parallel work streams that can proceed independently?
- What external dependencies exist (library updates, third-party APIs)?
- What approval gates are needed (security review, design review)?

### 6. Validate Completeness

- Do the tasks cover all functional requirements?
- Are non-functional requirements addressed (performance, security, reliability)?
- Is testing adequately planned?
- Is documentation included?
- Are verification commands/tests defined?

## Task Template

Each task should follow this structure:

```markdown
**Task X.Y**: [Concise task title]

- **Description**: [What needs to be done]
- **Team/Role**: [Backend | Frontend | Security | QA | DevOps]
- **Estimated Duration**: [2-8 hours]
- **Dependencies**: [Task IDs that must complete first, or "None"]
- **Deliverables**: [Specific outputs or changes]
- **Acceptance Criteria**: [How to verify completion]
```

## Example

See `examples/oauth-authentication.md` for a complete worked example.

## Best Practices

### Do's

- ✅ **Right-size tasks** — 2-8 hours each, not full days or weeks
- ✅ **Clear acceptance criteria** — Must be testable and specific
- ✅ **Assign appropriate teams** — Match task to expertise
- ✅ **Group related tasks** — Organize into phases for clarity
- ✅ **Identify dependencies** — Make blocking relationships explicit
- ✅ **Ensure completeness** — All requirements covered, nothing orphaned
- ✅ **Include verification** — Testing and validation tasks for every feature
- ✅ **Plan documentation** — Technical and user docs are deliverables
- ✅ **Consider security** — Threat modeling and security testing included
- ✅ **Think cross-platform** — Bitwarden runs everywhere; plan for it

### Don'ts

- ❌ **Tasks too large** — >1 day tasks should be broken down further
- ❌ **Vague acceptance criteria** — "Make it work" is not testable
- ❌ **Circular dependencies** — Tasks shouldn't block each other in loops
- ❌ **Missing phases** — Don't skip design, testing, or documentation
- ❌ **Unclear deliverables** — Every task should produce something concrete
- ❌ **Ignoring platforms** — Don't forget mobile, CLI, browser extensions
- ❌ **Skipping security** — Security tasks are not optional at Bitwarden

## Output Format

Organize work breakdown in structured phases:

```markdown
# Work Breakdown: [Feature Name]

## Summary

- **Total Estimated Duration**: X-Y hours
- **Number of Tasks**: N tasks across M phases
- **Teams Involved**: [List of teams]
- **Critical Path**: [Key dependencies or bottlenecks]

---

## Phase 1: [Phase Name]

**Goal**: [What this phase accomplishes]

**Task 1.1**: [Task title]

- **Description**: [What needs to be done]
- **Team/Role**: [Who does this]
- **Estimated Duration**: [Hours]
- **Dependencies**: [Prerequisites or "None"]
- **Deliverables**: [Concrete outputs]
- **Acceptance Criteria**: [How to verify]

**Task 1.2**: [Next task]
...

---

## Phase 2: [Phase Name]

...

---

## Verification

After all phases complete, verify:

- [ ] All functional requirements implemented
- [ ] All non-functional requirements met
- [ ] All security requirements addressed
- [ ] All tests passing (unit, integration, E2E)
- [ ] Documentation complete and accurate
- [ ] Deployment procedures tested
```
