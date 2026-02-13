---
name: threat-modeling
description: This skill should be used when the user asks to "create a threat model", "define security goals", "generate a data flow diagram", "write security definitions", "perform an initial security assessment", or needs to produce threat model artifacts for new features or architecture changes.
---

## Bitwarden's Engagement Model

Bitwarden follows a 4-phase engagement model for security work. This skill primarily supports Phase 1 (engineering-owned) and assists with Phase 2-4 artifacts.

### Phase 1: Initial Security Assessment (Engineering Team)

1. Create data flow diagrams (Mermaid, Excalidraw, or Structurizr)
2. Define security requirements separate from product requirements
3. Propose security definitions (threat model + security goals)
4. Identify initial threats using STRIDE (see `references/stride-framework.md`)

### Phase 2: AppSec Team Review (AppSec + Engineering)

- Share data flow diagrams and security definitions in advance
- Walk through system architecture collaboratively
- Validate or refine proposed security definitions
- Identify additional threats, assess risk
- Avoid assuming external mitigations exist

### Phase 3: Implementation (Engineering Team)

- Implement necessary security mitigations
- Create Jira follow-up work for threats without existing protections
- Include security considerations in sprint planning

### Phase 4: Testing & Validation (Engineering + AppSec)

- Verify mitigations work as intended
- Adopt adversarial mindset during code review
- Test hypotheses (e.g., "Can I bypass SSO?") by working backwards
- Update security definitions as the system evolves

## Security Definitions

Security definitions are Bitwarden's formal construct for communicating the security posture of a system. Each definition has three components: a **threat model** (attacker capabilities), **security goals** (what the system guarantees), and an **accepted goal status** (honest assessment of whether the goal is currently met).

Use Bitwarden's standard vocabulary when writing definitions — see `references/bitwarden-vocabulary.md` for the full glossary. Align security goals with Bitwarden's security principles (P01-P06) — see `references/security-principles.md`.

### Threat Model Component

Describe attacker capabilities AND limitations — what they can and cannot do. Always state both sides to scope the definition precisely:

- "Attacker can run a user space process after the user's client has logged out" + "Attacker does not have access to secure storage mechanisms"
- "Attacker has database access and can read and write to the Send table" + "Attacker does not have access to the ASP.NET Core Data Protection encryption keys"

Include concrete examples where helpful (e.g., "An example for this is a stolen device"). Don't assume external mitigations are in place — even if obtaining an auth token is difficult, still explore what happens if an attacker has one.

### Security Goals Component

State concise, testable guarantees about what cannot happen given the threat model. Reference specific assets (tokens, keys, vault data):

- "Valid tokens cannot be accessed by attacker after the user's client has logged out"
- "Attacker cannot retrieve any decrypted MasterKeys that do not belong to them"
- "Attacker can perform reads on encrypted email addresses lists only"

### Accepted Goal Status Component

Provide an honest assessment of the current state:

- **Goal is met** — Explain how (e.g., "User state clearing includes removal of the stored token from disk")
- **Goal is partially met** — Break down what works and what doesn't, using separate indicators for each aspect
- **Goal is not met** — Explain the gap and why it is accepted
- **Best Effort** — For goals dependent on platform capabilities (e.g., "This goal is not upheld for clients that do not have access to secure storage such as web and browser")

When a goal is known to be broken, link to the relevant tracking issue. Note scoping caveats (e.g., "These definitions do not apply in the case of a Vault Timeout set to `Never`").

### Writing Security Definitions

- It's OK to be wrong — the purpose is to start the conversation and see if these can be broken
- Start with what the system SHOULD guarantee, then validate through threat analysis
- Separate macro-level definitions (e.g., end-to-end encryption) from micro-level definitions specific to the feature
- Number definitions sequentially (SD1, SD2, SD3) — each is a self-contained unit
- Include a glossary of feature-specific terms when the feature introduces domain-specific vocabulary

## Artifact Generation

Use the templates in `examples/` when generating artifacts:

- **`examples/security-definition-document.md`** — Full SD document template with glossary, numbered definitions, and accepted goal status
- **`examples/data-flow-diagram.md`** — Mermaid DFD template with trust boundaries
- **`examples/threat-catalog.md`** — Threat catalog table and mitigation tracking templates

## When to Engage AppSec

Teams should initiate a full engagement with the AppSec team (#team-eng-appsec) when:

- **Greenfield projects** or new services
- **Data sharing modifications** (organization memberships, Send, sharing features)
- **New IPC channels** between components
- **Cross-domain or cross-origin** functionality
- **Uncertain about security implications** — perform an Initial Security Assessment first and post findings to #team-eng-appsec with a note indicating uncertainty about whether a full engagement is needed

Quick questions (e.g., concerns about a third-party library or coding practice) don't need a full engagement — post those directly to #team-eng-appsec.

## Critical Rules

- **Separate product requirements from security requirements** in tech breakdowns. They serve different purposes and have different stakeholders.
- **Security definitions are living documents.** Revisit them when features change, new threats emerge, or security issues are discovered.
- **Complexity increases vulnerability risk.** Flag overly complex security-critical code as tech debt. Complex code with numerous dependencies and intricate logic is exceptionally challenging to secure.
- **Threat modeling will never identify all vulnerabilities.** It's one tool among many. Balance it with code analysis, security testing, and adversarial review.
- **Don't assume external mitigations.** When defining the threat model, explore what happens if an attacker bypasses external controls.
