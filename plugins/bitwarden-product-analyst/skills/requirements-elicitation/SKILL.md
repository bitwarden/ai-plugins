---
name: requirements-elicitation
description: Extract complete, unambiguous requirements from specifications. Use when analyzing feature requests, processing enhancement specifications, or identifying missing information. Trigger phrases: "extract requirements", "analyze specification", "identify requirements", "clarify ambiguities".  After extracting requirements, use the `work-breakdown` skill.
---

# Requirements Elicitation

## Key Capabilities

1. **Extract Requirements** — Identify functional and non-functional requirements from multiple sources
2. **Clarify Ambiguities** — Flag unclear specifications and formulate targeted questions
3. **Identify Constraints** — Find technical, business, security, and resource limitations
4. **Categorize Requirements** — Organize by type (functional, non-functional, security, performance)

## Approach

### 1. Read and Understand

- Read entire specification thoroughly, including all referenced documents
- Identify the primary source (main requirement) vs. supporting documentation
- Note the scope and context of the request

### 2. Extract Explicit Requirements

- Capture clearly stated requirements
- Document exact specifications (API signatures, data formats, performance metrics)
- Preserve technical details verbatim

### 3. Identify Implicit Requirements

- Infer unstated but necessary requirements (e.g., error handling, validation, logging)
- Consider security implications based on Bitwarden security principles (P01-P06)
- Identify data classification needs (Vault Data, Protected Data, secure channels)

### 4. Flag Ambiguities and Gaps

- Document unclear or missing information
- Formulate specific questions to resolve ambiguities
- Identify conflicting requirements between sources
- Note assumptions being made

### 5. Document Constraints

- Technical constraints (APIs, platforms, compatibility)
- Security constraints (data protection, authentication, authorization)
- Resource constraints (performance, storage, bandwidth)
- Business constraints (timeline, scope, dependencies)

### 6. Create Acceptance Criteria

- For each requirement, define testable acceptance criteria
- Specify verification methods (commands, tests, manual checks)
- Include edge cases and error scenarios

## Bitwarden-Specific Considerations

### Security Requirements

Always consider and document:

- **Data classification** — Is this Vault Data, Protected Data, or other?
- **Data states** — Requirements for data at rest, in use, in transit
- **Security channels** — Need for secure/trusted channels?
- **Security principles** — Which principles (P01-P06) apply?
- **Threat scenarios** — What could go wrong?

### Common Bitwarden Requirement Types

- **Authentication/Authorization** — Who can access what?
- **Encryption** — What data needs protection and how?
- **Zero-knowledge** — Server must not have access to plaintext (P01)
- **Cross-platform** — Works on all Bitwarden clients?
- **Backwards compatibility** — Maintains existing behavior?

## Example

See `examples/export-functionality.md` for a complete worked example.

## Best Practices

### Do's

- ✅ Ask "what" questions, not "how" — Focus on requirements, not implementation
- ✅ Document assumptions explicitly — Make implicit knowledge visible
- ✅ Create testable acceptance criteria — Avoid vague success measures
- ✅ Consider all user types — Free users, premium, enterprise, admins
- ✅ Think about edge cases — Empty vaults, huge vaults, network failures
- ✅ Reference Bitwarden security principles — Ground security requirements in P01-P06
- ✅ Use Bitwarden vocabulary — Standard terminology for data, channels, security

### Don'ts

- ❌ Avoid: Making technical implementation decisions — That's the architect's job
- ❌ Avoid: Assuming unstated requirements are obvious — Explicit is better
- ❌ Avoid: Generic acceptance criteria — "It works" is not testable
- ❌ Avoid: Ignoring security implications — Security is never optional at Bitwarden
- ❌ Avoid: Skipping constraints — They're as important as requirements

## Output Format

Organize extracted requirements in structured sections:

```markdown
## Functional Requirements

1. REQ-F-001: [Specific capability the system must have]
   - **Acceptance Criteria**: [Testable condition]
   - **Priority**: Critical | High | Medium | Low

## Non-Functional Requirements

- **Performance**: [Response time, throughput, resource usage]
- **Reliability**: [Error handling, edge cases, availability]
- **Compatibility**: [Platform support, backwards compatibility]
- **Usability**: [User experience expectations]

## Security Requirements

- **Data Classification**: [Vault Data | Protected Data | Other]
- **Security Principles**: [P01, P02, P03, P04, P05, P06 as applicable]
- **Threat Considerations**: [What could go wrong?]

## Constraints

- **Technical**: [APIs, platforms, dependencies]
- **Business**: [Timeline, scope, resources]
- **Security**: [Compliance, encryption, authentication]

## Open Questions

1. [Specific question needing stakeholder input]
2. [Ambiguity requiring clarification]
3. [Missing information that blocks complete specification]

## Assumptions

- [Assumption 1: explicit statement of what's assumed]
- [Assumption 2: should be validated with stakeholders]
```
