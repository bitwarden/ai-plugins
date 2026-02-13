# Security Definition Document Template

Use this template when creating security definitions for a new feature or system.

```markdown
# [Feature Name] Security Definitions

[Link to macro-level security definitions and any parent feature documentation.]

[Optional scoping caveat, e.g., "These security definitions do not apply
in the case of a Vault Timeout set to `Never`."]

## Glossary

- **[Term]**: [Feature-specific definition]
- **[Term]**: [Feature-specific definition]

## SD1: [Concise threat scenario title]

### Threat Model

- Attacker can [capability]
  - An example for this is [concrete scenario]
- Attacker does not have [limitation that scopes this definition]

### Security Goal

- [Concise, testable guarantee about what cannot happen]

### Accepted Goal Status

- ✅ Goal is met:
  - [Explanation of how the goal is satisfied in the current implementation]

---

## SD2: [Concise threat scenario title]

### Threat Model

- Attacker can [capability]
- Attacker does not have [limitation]

### Security Goal

- [What the system guarantees]
- [Additional guarantee if applicable]

### Accepted Goal Status

- Goal is **partially** met:
  - ✅ [Aspect that is satisfied]
  - ❌ [Aspect that is not satisfied, with explanation of why this is accepted]
```
