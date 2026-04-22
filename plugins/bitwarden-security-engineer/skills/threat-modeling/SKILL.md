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

Security Definitions (SDs) are Bitwarden's formal construct for communicating the security posture of a system. Each definition has three components: a **threat model** (attacker capabilities), **security goals** (what the system guarantees), and an **accepted goal status** (honest assessment of whether the goal is currently met).

Use Bitwarden's standard vocabulary when writing definitions — see `references/bitwarden-vocabulary.md` for the full glossary. Align security goals with Bitwarden's security principles (P01-P06) — see `references/security-principles.md`.

### Threat Model Component

Describe attacker capabilities AND limitations — what they can and cannot do. Always state both sides to scope the definition precisely:

- "Attacker can run a user space process after the user's client has logged out" + "Attacker does not have access to secure storage mechanisms"
- "Attacker has database access and can read and write to the Send table" + "Attacker does not have access to the ASP.NET Core Data Protection encryption keys"

Include concrete examples where helpful (e.g., "An example for this is a stolen device"). Don't assume external mitigations are in place — even if obtaining an auth token is difficult, still explore what happens if an attacker has one.

Apply these rules when scoping the threat model:

- **Prune dominated threats.** If the attacker capability you're describing is strictly weaker than one already accepted as out-of-scope, delete the SD — its residual-risk statement collapses to a tautology like "equivalent to full user-account compromise". See `references/writing-quality-sds.md` for the dominated-threat anti-pattern and the term **Dominated Threat** in `references/bitwarden-vocabulary.md`.
- **Include passive observers, not just adversaries.** For any secret or protected data that crosses into an external service (LLM provider, log aggregator, analytics pipeline, training-data collector), write at least one SD whose attacker is **honest-but-curious**. Confidentiality harms often arise from _visibility_, not malice — an adversarial framing alone misses the baseline concern. See the **Passive Observer** vocabulary entry.
- **Verify "attacker does not have X" against the target platforms.** Every limitation must be factually true on every OS/runtime in scope. Common pitfall: assuming kernel-level privileges are required for a capability that is actually unprivileged on Linux and Windows (e.g., reading another process's environment). If the limit isn't true, the SD is mis-scoped.

### Security Goals Component

State concise, testable guarantees about what cannot happen given the threat model. Reference specific assets (tokens, keys, vault data):

- "Valid tokens cannot be accessed by attacker after the user's client has logged out"
- "Attacker cannot retrieve any decrypted MasterKeys that do not belong to them"
- "Attacker can perform reads on encrypted email addresses lists only"

Every goal carries a **Rationale** — three pieces, one line each:

- **Principle** — which Bitwarden principle (P01–P06) the goal enforces. See `references/security-principles.md`.
- **Asset** — the specific data, key, or token being protected.
- **Harm** — the user-visible consequence if the goal is violated (e.g., "master password exposed to third-party LLM provider and potentially their training pipeline").

A goal without a rationale is a claim, not a requirement. Rationales let reviewers judge whether the goal is load-bearing or can be cut.

Two additional rules on goal framing:

- **Reality-check goals against runtime.** Goals that claim a secret is "cleared from memory", "zeroized", or "not retained" are unenforceable in garbage-collected, string-interned runtimes (JavaScript, .NET, JVM, Python). If the runtime cannot uphold the goal, restate it in terms of what the runtime _can_ guarantee (scope minimization, short-lived references, process isolation), or mark Accepted Goal Status as explicitly not met and link the systemic limitation. Do not write goals the language cannot back.
- **Prefer stdin or file-descriptor handoff over env/argv for secrets.** If the goal forbids secret exposure to `process.env` or `argv`, the implementation MUST use stdin or an inherited file descriptor. An SD whose goal forbids env exposure but whose implementation passes the secret through env is internally inconsistent — fix the design, or fix the goal, but do not ship both.

### Accepted Goal Status Component

Provide an honest assessment of the current state:

- **Goal is met** — Explain how (e.g., "User state clearing includes removal of the stored token from disk")
- **Goal is partially met** — Break down what works and what doesn't, using separate indicators for each aspect
- **Goal is not met** — Explain the gap and why it is accepted
- **Best Effort** — For goals dependent on platform capabilities (e.g., "This goal is not upheld for clients that do not have access to secure storage such as web and browser")

When a goal is known to be broken, link to the relevant tracking issue. Note scoping caveats (e.g., "These definitions do not apply in the case of a Vault Timeout set to `Never`").

Two additional rules:

- **Quantify "brief" or "short-lived" rationales.** If acceptance of residual risk rests on "the exposure is short", state the bound. For example: "Secret resides in the child process env for the duration of `bw unlock`, which scales with KDF iterations and vault size — observed between 1 and 8 seconds on representative hardware." _Brief without a number is not an accepted status — it is a hope._ See the **Exposure Window** vocabulary entry.
- **Enforce internal consistency.** The Threat Model, Security Goal, and Accepted Goal Status must agree. If the threat model puts capability X in-scope, the goal must defend against X, and the status must say whether that defense holds. If the goal forbids env exposure but the implementation uses env, the SD is wrong — pick which of the three to change and change it. Inconsistency is not a style issue; it is the SD failing to describe the system.

### Writing Security Definitions

- It's OK to be wrong — the purpose is to start the conversation and see if these can be broken
- Start with what the system SHOULD guarantee, then validate through threat analysis
- Separate macro-level definitions (e.g., end-to-end encryption) from micro-level definitions specific to the feature
- Number definitions sequentially (SD1, SD2, SD3) — each is a self-contained unit
- Include a glossary of feature-specific terms when the feature introduces domain-specific vocabulary
- **Prioritize by impact, not by enumeration.** A short document listing the 3–5 threats that actually shape the design is more useful than a 15-SD document that buries the important ones in noise. Before adding an SD, ask: _"If this threat didn't exist, would the design change?"_ If the answer is no, it is likely code-quality commentary, not a security definition.
- **Tag each SD with a Criticality level** (Critical / High / Medium / Low) and order the document by Criticality descending, so reviewers see the load-bearing SDs first. See `references/writing-quality-sds.md` for the prioritization heuristic.
- **Verbosity is a failure mode.** The same anti-pattern that plagued early LLM code review — long lists with low signal — also plagues generated security definitions. Cut SDs that describe implementation-detail concerns (e.g., a future maintainer editing a constant to contain shell metacharacters) unless they are load-bearing to the design.

## Artifact Generation

Use the templates in `examples/` when generating artifacts:

- **`examples/security-definition-document.md`** — Full SD document template with glossary, numbered definitions, Criticality tagging, goal rationale, and accepted goal status
- **`examples/data-flow-diagram.md`** — Mermaid DFD template with trust boundaries
- **`examples/threat-catalog.md`** — Threat catalog table and mitigation tracking templates

Consult these references when writing or reviewing SDs:

- **`references/writing-quality-sds.md`** — Anti-patterns (dominated threats, adversarial-only attackers, unenforceable goals, aspirational limitations, shell-quoting SDs, the "brief exposure" trap) and the self-consistency checklist
- **`references/bitwarden-vocabulary.md`** — Standard terms, including **Passive Observer**, **Dominated Threat**, and **Exposure Window**
- **`references/security-principles.md`** — P01–P06, referenced by every goal's Rationale line
- **`references/stride-framework.md`** — STRIDE categories for structured threat identification

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
- **Dominated or implementation-trivial threats are noise.** Cut SDs whose residual-risk text reduces to "equivalent to full user-account compromise" or whose only mitigation is "reviewers notice a constant being edited". They degrade signal-to-noise and hide the threats that actually matter.
- **Every security goal carries a rationale.** Tie each goal to a Bitwarden principle (P01–P06), the protected asset, and the user-visible harm. Goals without rationales cannot be prioritized or evaluated for necessity, and tend to survive review by inertia rather than merit.

Before finalizing a set of SDs, apply the self-consistency checklist in `references/writing-quality-sds.md`.
