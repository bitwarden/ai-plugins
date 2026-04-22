# Security Definition Document Template

Use this template when creating security definitions for a new feature or system.

Order SDs by **Criticality descending**. Reviewers anchor on what they see first — lead with the load-bearing threats.

Every Security Goal must carry a **Rationale** line linking the goal to a Bitwarden principle (P01–P06), the protected asset, and the user-visible harm. Goals without rationale are claims, not requirements.

When an Accepted Goal Status says a secret's exposure is "brief", "short-lived", or "transient", **quantify the window** — state a typical and worst-case duration. "Brief" without a number is a hope, not a status.

```markdown
# [Feature Name] Security Definitions

[Link to macro-level security definitions and any parent feature documentation.]

[Optional scoping caveat, e.g., "These security definitions do not apply
in the case of a Vault Timeout set to `Never`."]

## Glossary

- **[Term]**: [Feature-specific definition]
- **[Term]**: [Feature-specific definition]

---

## SD1: [Concise threat scenario title]

**Criticality:** Critical | High | Medium | Low

### Threat Model

- Attacker can [capability]
  - An example for this is [concrete scenario]
- Attacker does not have [limitation that scopes this definition — verified against every supported OS]

### Security Goal

- [Concise, testable guarantee about what cannot happen]
- **Rationale:** Enforces [P0X: Principle Name]; protects [asset: token/key/vault data/password]; harm if violated is [user-visible consequence, e.g., "master password visible to third-party LLM provider and potentially their training pipeline"].

### Accepted Goal Status

- ✅ Goal is met:
  - [Explanation of how the goal is satisfied in the current implementation]

---

## SD2: [Concise threat scenario title]

**Criticality:** Critical | High | Medium | Low

### Threat Model

- Attacker is a **Passive Observer** — [e.g., the LLM provider receiving tool I/O, a log aggregator, a telemetry pipeline]. No malicious intent required; the harm arises from visibility during normal operation.
- Attacker does not have [limitation]

### Security Goal

- [What the system guarantees]
- **Rationale:** Enforces [P0X]; protects [asset]; harm if violated is [consequence].

### Accepted Goal Status

- Goal is **partially** met:
  - ✅ [Aspect that is satisfied]
  - ❌ [Aspect that is not satisfied — include quantified exposure window if acceptance rests on "brief" duration, e.g., "secret resides in child-process env for 1–8 s depending on KDF iterations and vault size"]

---

## SD3: [Concise threat scenario title]

**Criticality:** Critical | High | Medium | Low

### Threat Model

- Attacker can [capability]
- Attacker does not have [limitation]

### Security Goal

- [What the system guarantees]
- **Rationale:** Enforces [P0X]; protects [asset]; harm if violated is [consequence].

### Accepted Goal Status

- ❌ Goal is **not** met:
  - [Explanation of the gap. If the goal is unenforceable due to runtime constraints — e.g., memory zeroization in a GC'd, string-interning runtime — state the systemic limitation here and link any tracking issue. Do not write a goal the language cannot back.]
```

## Before shipping

Apply the self-consistency checklist in [`../references/writing-quality-sds.md`](../references/writing-quality-sds.md):

1. Does each goal defend against every in-scope threat-model capability?
2. Is every goal realizable by the runtime?
3. Is every "attacker does not have X" true on every supported OS?
4. Is there a passive-observer SD wherever a secret crosses an external-service boundary?
5. Is every SD tagged with Criticality, and is the document ordered Criticality-descending?
