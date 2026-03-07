# Bitwarden Requirements Document Template

This template provides a standard structure for Bitwarden feature requirements documents. Use this as a reference when creating comprehensive specifications for new features or enhancements.

---

````markdown
---
title: [Feature or Enhancement Name]
status: Draft | In Review | Approved | In Progress | Complete
created: YYYY-MM-DD
author: [Your Name]
---

# [Feature Name]: [Brief Title]

## Overview

**Goal**: [One sentence describing what this feature/enhancement accomplishes]

### Product Scope

**Supported on**: Cloud | Self-Hosted | Both

**Plan applicability**:

|                              | Type                             | Applicability |
| ---------------------------- | -------------------------------- | ------------- |
| **Individual plans**         | Free                             |               |
|                              | Premium                          |               |
| **Organization plans**       | Free 2-person org                |               |
|                              | Families                         |               |
|                              | Teams                            |               |
|                              | Enterprise                       |               |
|                              | Enterprise + Access Intelligence |               |
| **Provider-supported plans** | Teams                            |               |
|                              | Enterprise                       |               |
|                              | Enterprise + Access Intelligence |               |

**User role applicability**:

| Role                             | Applicability |
| -------------------------------- | ------------- |
| Member                           |               |
| Admin                            |               |
| Owner                            |               |
| Custom permission                |               |
| Provider Admin (Provider Portal) |               |
| Service User (Provider Portal)   |               |

**Client applicability**:

| Client                                                                        | Applicability |
| ----------------------------------------------------------------------------- | ------------- |
| Web app — Password Manager (end user)                                         |               |
| Web app — Secrets Manager                                                     |               |
| Web app — Admin Console                                                       |               |
| Web app — Provider Portal                                                     |               |
| Browser extension — Chrome, Firefox, Safari, Opera, Edge, Vivaldi, Brave, Tor |               |
| Mobile app — iOS and Android                                                  |               |
| Desktop app                                                                   |               |
| CLI                                                                           |               |

**User Stories**:

- As an **individual user**, I want [goal/capability] so that [benefit/value].
- As an **organization member**, I want [goal/capability] so that [benefit/value].
- As an **organization admin**, I want [goal/capability] so that [benefit/value].
- As a **self-hosted administrator**, I want [goal/capability] so that [benefit/value].
- As a **provider/MSP**, I want [goal/capability] so that [benefit/value]. _(if applicable)_

---

## Measurable Outcomes

> Define success in business terms before writing requirements. Both metric types are required.

| Metric                                              | Metric type              | Data source                        |
| --------------------------------------------------- | ------------------------ | ---------------------------------- |
| [e.g., % of Enterprise orgs adopting this feature]  | Direct adoption metric   | [Bitwarden dB / Stripe / cosmosDB] |
| [e.g., Increase in Enterprise sales-assist revenue] | Indirect business metric | [Stripe]                           |

**Strategic questions**:

- Why are we doing this now?
- Does this drive more differentiation for Bitwarden? How?
- How does this contribute to business outcomes?
- What are the risks associated with this initiative?

---

## Context & Background

### Current State

- What exists today in the Bitwarden codebase
- Relevant system components and architecture
- Why this feature/enhancement is needed now
- What problem does this solve for users?
- Customer quotes and direct feedback supporting this initiative

### Competitive Context

- **1Password**: [How do they handle this?]
- **LastPass**: [How do they handle this?]
- **Keeper**: [How do they handle this?]
- **Dashlane**: [How do they handle this?]
- **Other reference products**: [Any non-competitor products worth referencing?]
- Are there existing tools customers could use today? Would they?

### Technical Context

- Target platforms/environments (Web, Desktop, Mobile, CLI, Browser Extensions)
- Performance requirements or expectations
- Integration points with existing Bitwarden systems
- Architectural considerations

### Dependencies

- Other features or components this relies on
- External libraries, APIs, or tools needed
- Related features or enhancements (cross-references)
- Prerequisite work that must be completed first
- Cross-repo dependencies (e.g., `bitwarden/server` API changes required before client work)

---

## Requirements

### Functional Requirements

> What the system must do. Be specific and testable.

1. **REQ-F-001**: [Specific capability the system must have]
   - [Additional details if needed]
2. **REQ-F-002**: [Another required function]
3. **REQ-F-003**: [User-facing behavior or interaction]

### Non-Functional Requirements

**Performance**:

- [Response time requirements, e.g., "API responds within 200ms"]
- [Throughput requirements, e.g., "Supports 1000 concurrent users"]
- [Resource usage constraints, e.g., "Max 50MB memory footprint on mobile"]

**Reliability**:

- [Error handling expectations]
- [Edge case behaviors]
- [Availability requirements, e.g., "99.9% uptime"]

**Compatibility**:

- [Backwards compatibility requirements]
- [Platform support (which OS, browsers, devices)]
- [API version compatibility]

**Usability**:

- [User experience expectations]
- [Accessibility requirements (WCAG 2.1 AA compliance)]
- [Internationalization/localization needs]

### Required Work

> ALL items in this section MUST be completed for the feature to be considered done.
> Do not skip any items. Do not treat any items as optional.

- [ ] [Specific deliverable or task 1]
- [ ] [Specific deliverable or task 2]
- [ ] [Specific deliverable or task 3]
- [ ] [Backend API implementation (`bitwarden/server`)]
- [ ] [Web vault UI implementation (`apps/web`)]
- [ ] [Browser extension support (`apps/browser`) — Chrome, Firefox, Safari, Edge]
- [ ] [Desktop client support (`apps/desktop`)]
- [ ] [Mobile client support — iOS and Android (`apps/mobile`)]
- [ ] [CLI support and scripting behavior (`apps/cli`)]
- [ ] [Self-hosted deployment compatibility verified]
- [ ] [Localization strings added to all affected clients]
- [ ] [Organization/admin policy controls (if applicable)]
- [ ] [Provider Portal support (if applicable)]
- [ ] [Secrets Manager SDK impact assessed (if applicable)]
- [ ] [Unit and integration tests]
- [ ] [Documentation (user-facing and developer)]

### Out of Scope

> Explicitly list what this feature does NOT include to prevent scope creep.
> These items should not be worked on as part of this feature.

- [Feature X] — Will be addressed in a separate feature/phase
- [Feature Y] — Not needed for this use case
- [Feature Z] — Deferred to future iteration

---

## Open Questions

> Items that need answers before implementation begins.
> If questions remain unanswered, implementation should not start.

1. [Question about design approach or architecture]
2. [Question about API/interface decisions]
3. [Question about platform-specific behavior]
4. [Question about security or privacy considerations]

---

## Constraints & Limitations

### Technical Constraints

- **Must not break**: [Existing features or behaviors that must remain intact]
- **Must use**: [Specific APIs, patterns, or technologies required]
- **Must maintain**: [Backwards compatibility requirements, data format compatibility]
- **Platform limitations**: [iOS restrictions, browser API limitations, etc.]

### Business Constraints

- **Timeline**: [Deadlines or target release dates]
- **Resources**: [Team availability, budget constraints]
- **External dependencies**: [Third-party services, legal requirements]

### Existing Customer Impact & Migration

- **Deprecation**: Is this replacing or removing any existing product functionality? Has leadership signed off?
- **Migration plan**: If yes, how will existing users/data be migrated?
- **Communication plan**: Does this require proactive customer communication?
  - Channels to consider: in-app messaging, email, Reddit, Bitwarden Community forums, social media
  - Timing: before release, at release, or post-release?

### Team Considerations

> Identify all teams required to deliver this initiative.

- **Which teams are needed?** (e.g., Platform, Vault, Admin Console, Mobile, CLI, SM, Data, DevOps, CloudOps, Security, GTM)
- **Data team**: Are there analytics instrumentation, pipeline, or reporting needs?
- **Infrastructure (DevOps / CloudOps)**: Are there infrastructure, deployment, or scaling requirements?
- **Enablement work**: Is backend/platform work required before user-facing work can start? If so, is it scoped to less than one quarter?
- **Staffing approach**: What is the best way to staff this across teams to deliver fastest?
- **Alternative solutions**: Have we explored all possible solutions and time-to-market tradeoffs? Is there a lower-effort path?

---

## Success Criteria

### Definition of Done

> ALL of these criteria must be met. This is not a checklist of options.

- [ ] All Required Work items completed
- [ ] All functional requirements implemented
- [ ] All non-functional requirements met
- [ ] All acceptance tests pass
- [ ] No regressions in existing features
- [ ] Code builds and passes CI/CD pipelines
- [ ] Security review completed (if applicable)
- [ ] Documentation complete and reviewed
- [ ] Cross-platform testing complete (Web, Desktop, Mobile)

### Acceptance Tests

> Concrete, verifiable test cases. Each must pass for the feature to be accepted.

1. **Test 1**: Given [initial state/precondition], when [user action], then [expected result]
2. **Test 2**: Given [scenario], when [action], then [expected outcome]
3. **Test 3 (Edge Case)**: Given [edge condition], when [action], then [system behavior]
4. **Test 4 (Error Scenario)**: Given [error condition], when [action], then [error handling behavior]

### Verification Commands

> Specific commands, scripts, or procedures to verify the feature is complete and correct.

```bash
# Example: Run feature-specific tests (replace <repo> and <pattern> as appropriate)
# Web/browser/desktop/CLI clients:
cd apps/<client> && npm run test -- --testPathPattern=<feature-name>
# Expected: All tests pass, >80% coverage

# Server (bitwarden/server repo):
dotnet test --filter "FullyQualifiedName~<FeatureName>"
# Expected: All tests pass

# Example: Verify no regressions
npm run test:regression
# Expected: All regression tests pass
```
````

---

## Security & Safety Considerations

### Data Classification

- **Vault Data**: [Is this feature handling user vault data? How?]
- **Protected Data**: [What data needs encryption? Key management?]
- **Data in Transit**: [Secure channel or trusted channel requirements?]

### Encryption & Sync

- **Encryption boundary**: Where is data encrypted/decrypted? (Must be client-side for vault data — never on the server)
- **Key material involved**: Master key / organization key / Send key / other?
- **Sync impact**: Does this add or change sync payloads? How does it affect offline mode?
- **Server knowledge**: Can the server read any of this data? (Zero-knowledge check — server must remain blind to vault contents)

### Security Principles

> All six principles must be considered. Document how this feature upholds each, or explicitly note "Not applicable" with justification.

- **P01 (Zero Knowledge)**: [How does this maintain server zero-knowledge? Server must never see plaintext vault data.]
- **P02 (Locked Vault Security)**: [How does this respect locked vault state? What is accessible when vault is locked?]
- **P03 (Trust Hierarchy)**: [How does this interact with org owners, admins, managers, members, and providers?]
- **P04 (Cryptographic Safety)**: [What cryptographic operations are involved? Are they client-side only? Which algorithms/key types?]
- **P05 (Controlled Access)**: [What access controls are implemented? How are permissions enforced?]
- **P06 (Transparency)**: [Audit logging implications? Open-source considerations? What is logged and where?]

### Threat Considerations

- [What could go wrong from a security perspective?]
- [What attack vectors exist?]
- [What mitigations are in place?]
- [Is formal threat modeling required? (Create separate security definition document)]

### Data Validation

- [What inputs need validation?]
- [What are the validation rules?]
- [How are invalid inputs handled?]

### Error Handling

- [How are errors surfaced to users?]
- [What error information is logged?]
- [Are there any sensitive data leakage risks in errors?]

### Resource Management

- [Are there resource limits (memory, disk, network)?]
- [How is cleanup handled (files, connections, sessions)?]
- [What happens on unexpected termination?]

### Organization & Collection Model Impact

- Does this feature apply to personal vaults, organization vaults, or both?
- How does it interact with Collection permissions and access policies?
- How does behavior differ across roles: Owner, Admin, Manager, Member, Custom?
- Provider Portal / MSP considerations (if applicable)?
- Does this feature require new permission types or collection-level controls?

### Enterprise Policy Controls

> Complete this section if the feature has admin-configurable behavior.

- Does this feature need a corresponding organizational policy?
- What can organization admins enforce, restrict, or require?
- What is the behavior when a policy is active vs. inactive?
- Does policy enforcement apply to existing members retroactively or only new logins?

### Feature Flag

- **Flag name**: `[feature-name-enabled]`
- **Rollout strategy**: Internal → Beta → GA
- **Kill switch behavior**: What happens to users mid-rollout if the flag is disabled?
- **Self-hosted flag behavior**: Does the flag apply to self-hosted instances?

---

## UI/UX Considerations

> If this feature has user-facing components

### User Interaction Flow

1. [Step 1: User does X]
2. [Step 2: System responds with Y]
3. [Step 3: User sees Z]

### Input/Output Format

- **Inputs**: [What data does user provide? Format? Validation?]
- **Outputs**: [What feedback does user receive? Success states? Error states?]

### Error Messages

- [What error messages are shown to users?]
- [Are error messages clear, actionable, non-technical?]

### Discoverability & Notifications

- **Discovery**: How will users find or learn about this functionality? (e.g., onboarding, in-app prompt, email, release notes)
- **Alert Center**: Are there user actions or security events related to this feature that should surface in the Alert Center?
- **Notifications**: What notifications should support this feature?
  - In-product notifications: [describe]
  - Email notifications: [describe]

### Accessibility

- [Keyboard navigation support]
- [Screen reader compatibility]
- [Color contrast and visual accessibility — target WCAG 2.1 AA]

---

## Testing Strategy

### Unit Tests

- **Component A**: [Test cases needed]
  - [Specific test scenario 1]
  - [Specific test scenario 2]
- **Component B**: [Test cases needed]
  - [Specific test scenario 1]
  - [Edge case test]

### Integration Tests

- **System interaction X**: [Test scenario]
- **Edge case Y**: [Test scenario]
- **Error handling Z**: [Test scenario]

### End-to-End Tests

- **User flow 1**: [Complete user journey test]
- **User flow 2**: [Alternative path test]
- **Cross-platform**: [Platform-specific behavior verification]

### Manual Test Scenarios

> Scenarios that require human verification

1. **Scenario 1**: [Step-by-step manual test case]
   - Expected outcome: [What tester should observe]
2. **Scenario 2**: [Another manual verification scenario]
   - Expected outcome: [Observable result]

### Performance Testing

- [Load testing requirements]
- [Stress testing scenarios]
- [Performance benchmarks to verify]

---

## Implementation Checklist

> Specific files, components, and changes required. Be explicit.

### Files to Modify

> Note: Bitwarden's server lives in a **separate repository** (`bitwarden/server`). Cross-repo PRs must be coordinated and merged in dependency order (server first, then clients).

**Client repos** (`bitwarden/clients`):

| File Path                                      | Changes Required          |
| ---------------------------------------------- | ------------------------- |
| `apps/web/src/components/feature.component.ts` | [Specific changes needed] |
| `libs/common/src/services/feature.service.ts`  | [Specific changes needed] |
| `apps/mobile/src/screens/feature.screen.tsx`   | [Specific changes needed] |

**Server repo** (`bitwarden/server`):

| File Path                                  | Changes Required          |
| ------------------------------------------ | ------------------------- |
| `src/Api/Controllers/FeatureController.cs` | [Specific changes needed] |
| `src/Core/Services/FeatureService.cs`      | [Specific changes needed] |

### New Files to Create

| Repo                | File Path                                  | Purpose                  |
| ------------------- | ------------------------------------------ | ------------------------ |
| `bitwarden/clients` | `libs/common/src/models/feature.model.ts`  | [Data model for feature] |
| `bitwarden/server`  | `src/Api/Controllers/FeatureController.cs` | [API endpoint handler]   |

### Implementation Pattern

> If a pattern should be applied repeatedly, document it clearly.

```typescript
// BEFORE:
function oldPattern() {
  // [existing code pattern]
}

// AFTER:
function newPattern() {
  // [new code pattern to follow]
}
```

### Database Changes

- **New Tables**: [Table definitions if needed]
- **Schema Modifications**: [Column additions, indexes, constraints]
- **Migration Strategy**: [How to migrate existing data]

---

## Product Positioning

> To be collaborated on between Product, Design, and Product Marketing.

- **Feature name / naming**: How should this offering be named? Does it need a product marketing name?
- **User workflow impact**: How does this improve the target user's day-to-day workflow?
- **Market differentiation**: Why does this matter to the market? How does it differentiate Bitwarden?
- **Demo update**: Does the Bitwarden product demo need to be updated to include this offering?

---

## Design Documentation

- **User research**: [Link to user research, interviews, or survey data]
- **Figma / design files**: [Link to Figma designs aligned to each release milestone]
- **UX flows**: [Link to user flow diagrams or prototypes]

---

## References & Research

- [Link to Bitwarden security definitions](https://contributing.bitwarden.com/architecture/security/definitions)
- [Link to Product Initiative doc in Confluence]
- [Link to relevant GitHub issues]
- [Link to design documents or RFCs]
- [Link to third-party API documentation]
- [Similar implementations in other systems]
- [Technical specifications or standards]

---

## Related Work

- **GitHub Issues**: [Links to related issues]
- **Pull Requests**: [Links to related PRs]
- **Documentation**: [Links to existing docs that relate]
- **Previous Features**: [Links to similar past work]

---

## Notes

[Any additional context, considerations, or information that doesn't fit in other sections]

```

```
