---
name: architecting-solutions
description: Bitwarden solution architecture process — context discovery, requirements refinement, gap analysis, architecture design, and deliverable production. Use when planning a solution, reviewing architecture, assessing blast radius, or evaluating trade-offs in any Bitwarden repository. Not for writing code — for deciding what to build and how the parts connect.
---

## Step 1: Context Discovery

Before any planning, orient yourself in the target repository:

1. **Read the repo's CLAUDE.md** — learn architecture constraints, security rules, code organization, and available skills from the **Skills & Commands** table.

2. **Read architecture documentation** referenced in CLAUDE.md — follow whatever links or file references it provides.

3. **Identify the planning skill** from the Skills & Commands table — look for skills matching triggers like "plan implementation", "architecture plan", or "design approach". **Use the `Skill` tool to invoke it by name** (e.g., `Skill("planning-android-implementation")`). Do NOT read the SKILL.md file directly — invoking loads it into your active context with proper activation.

4. **If no planning skill exists**: Fall back to codebase exploration via sub-agents to discover conventions, patterns, and project structure organically.

---

## Step 2: Requirements Refinement

Parse the requirements and actively look for gaps — focus on Bitwarden-specific concerns:

- Missing security or zero-knowledge implications
- Unspecified API contracts or SDK interactions — especially V+/-2 compatibility
- Undefined multi-account or account-switching behavior
- Missing app extension / module boundary considerations
- Impact on self-hosted deployments and the version matrix

If a requirements-refinement skill exists in the repo, **use the `Skill` tool to invoke it by name**.

Produce a structured specification covering: summary, affected modules, functional requirements, non-functional requirements, open questions, and assumptions.

---

## Step 3: Technical Gap Analysis

Evaluate each item and note which are relevant — do not include items that clearly don't apply:

- [ ] Zero-knowledge / encryption implications
- [ ] Authentication / authorization changes
- [ ] Multi-account / account-switching impact
- [ ] Multi-client impact (web, browser, desktop, CLI, self-hosted)
- [ ] App extension / module boundary impact
- [ ] SDK dependency or API contract changes (V+/-2 compatibility)
- [ ] Dual data-access parity (both database backends, if applicable)
- [ ] Data migration or schema changes
- [ ] Performance / memory implications
- [ ] Offline / network failure behavior

You own **technical** gaps (security, platform constraints, SDK, extensions). Product/UX gaps are the product analyst's domain.

---

## Step 4: Architecture Design

1. **Explore the codebase** via sub-agents to understand existing patterns before designing. Never assume file locations or implementations.

2. **Design the architecture** — prefer established patterns found in the codebase. Flag cases where a new pattern might be genuinely needed (rare). Reference specific existing files as implementation guides.

3. Organize work into logical, dependency-ordered phases. Use the repo's planning skill for platform-specific phase ordering if available.

---

## Bitwarden-Specific Constraints

### Security Mindset

Bitwarden is a password manager — security isn't a feature, it's the product.

- **Threat model early.** Before approving an approach, ask: what can an attacker reach from here? Use the threat-modeling skill for complex features.
- **Classify data touch points.** Know which fields are encrypted, which are plaintext, and which cross trust boundaries. Never add a new path for sensitive data without encryption at rest and in transit.

### Platform Constraints

- **Version matrix (V +/- 2):** The server must support clients up to 2 major versions behind. Every API change must be additive: new fields are optional, responses degrade gracefully, and nothing breaks for a client that hasn't updated yet.
- **No formal API versioning:** Breaking changes are actively discouraged. API models trend toward optional-everywhere to preserve backwards compatibility. Don't add required fields to existing endpoints.
- **Self-hosted constraint:** Features must degrade gracefully for self-hosted customers who may run older versions or different infrastructure.

### Judgment

- **Complement existing patterns.** New code should work alongside what's already there. When proposing new approaches, show how they coexist with current patterns — do not force a rewrite to adopt them.
- **Document tech debt, don't silently fix it.** Unscoped refactors create unwanted risk. Identify the finding and report it to the user.

### Red Flags to Surface

- Silent behavior changes in shared libraries (`libs/common`, `src/Core`)
- Refactors bundled with feature work without explicit scope approval
- Security shortcuts in the name of velocity

---

## Deliverables

### 1. Implementation Plan (`{slug}-IMPLEMENTATION-PLAN.md`)

```
# Implementation Plan: [Feature Name]

## Refined Requirements
### Summary
### Functional Requirements
### Non-Functional Requirements
### Assumptions
### Open Questions (if any — request answers from user before proceeding)

## Technical Gap Analysis
[Security, platform constraints, SDK, multi-account, extensions — only items that apply]

## Architecture Design
### Affected Components
### New Interfaces & Implementations
### Data Flow Diagram (text-based)

## Phased Implementation Plan
### Phase 1: [Name]
- Task 1.1: [concrete, actionable task]
  - Files: [paths]
  - Depends on: [nothing | task X.Y]
  - Acceptance: [how to verify this task is done]
### Phase 2: [Name]
...

## File Manifest
### New Files
### Modified Files

## Risk & Dependency Notes

## Handoff Notes for Implementer
```

### 2. Work Breakdown Document (`{slug}-WORK-BREAKDOWN.md`)

When consolidating with a product analyst's high-level breakdown: merge their epics/stories/acceptance criteria with your technical task breakdown into Jira-ready tasks.

### 3. Architecture Review

When reviewing implementation against a plan: verify adherence to the architecture design, pattern selection, and repo conventions.

---

## Output Location

Write artifacts to `${CLAUDE_PLUGIN_DATA}/plans/`:
- `${CLAUDE_PLUGIN_DATA}/plans/{slug}-IMPLEMENTATION-PLAN.md`
- `${CLAUDE_PLUGIN_DATA}/plans/{slug}-WORK-BREAKDOWN.md`

Create the output directory if it doesn't exist.
