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
4. Identify initial threats using STRIDE

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

### Core Vocabulary

Use Bitwarden's standard terminology when writing security definitions:

- **Vault Data** — A user's private information stored in Bitwarden (passwords, usernames, secure notes, credit cards, identities, attachments)
- **Protected Data** — Data stored in unreadable format (typically encrypted) with expectations about secure key storage
- **Data at Rest / in Use / in Transit** — The three data states. "At rest" is stored data on disk. "In use" is data in volatile memory during processing. "In transit" is data moving between locations, processes, or devices.
- **Secure Channel** — A communication channel providing confidentiality (unreadable to unauthorized parties) and integrity (tamper-proof)
- **Trusted Channel** — A secure channel that also provides authenticity (verified identities of communicating parties)
- **Data Exporting** — Controlled process where data leaves Bitwarden unprotected, nullifying security guarantees. Requires informed and explicit consent.
- **Data Sharing** — Controlled data exchange within the Bitwarden secure environment (security guarantees maintained)
- **Data Leaking** — Unintentional departure of data from Bitwarden unprotected
- **Bitwarden Secure Environment** — Any process or application adhering to Bitwarden's security standards

### Threat Model Component

Describe attacker capabilities AND limitations — what they can and cannot do. Always state both sides to scope the definition precisely:

- "Attacker can run a user space process after the user's client has logged out" + "Attacker does not have access to secure storage mechanisms"
- "Attacker has database access and can read and write to the Send table" + "Attacker does not have access to the ASP.NET Core Data Protection encryption keys"
- "Attacker can execute arbitrary JavaScript on the web vault domain"
- "Attacker can make requests to the `/xyz` endpoint" + "Attacker does not have access to self-hosted server infrastructure"

Include concrete examples where helpful (e.g., "An example for this is a stolen device" or "e.g., through stored XSS in vault data or compromised third-party script").

**Key principle:** Don't assume external mitigations are in place. Even if obtaining an auth token is difficult, still explore what happens if an attacker has one.

### Security Goals Component

State concise, testable guarantees about what cannot happen given the threat model. Reference specific assets (tokens, keys, vault data) and align with Bitwarden's security principles (P01-P06) where applicable:

- "Valid tokens cannot be accessed by attacker after the user's client has logged out"
- "Attacker cannot retrieve any decrypted MasterKeys that do not belong to them"
- "Token cannot be exfiltrated"
- "The Credential is not released, and the Attacker and Attacking Application do not get access to the Credential"
- "Attacker can perform reads on encrypted email addresses lists only"

### Accepted Goal Status Component

Provide an honest assessment of the current state. Use status indicators:

- **Goal is met** — Explain how (e.g., "User state clearing includes removal of the stored token from disk")
- **Goal is partially met** — Break down what works and what doesn't, using separate indicators for each aspect
- **Goal is not met** — Explain the gap and why it is accepted (e.g., "access to the self-hosted infrastructure means that the token could likely be exfiltrated through other means")
- **Best Effort** — For goals dependent on platform capabilities (e.g., "This goal is not upheld for clients that do not have access to secure storage such as web and browser")

When a goal is known to be broken, link to the relevant tracking issue or documentation. Note any scoping caveats (e.g., "These definitions do not apply in the case of a Vault Timeout set to `Never`").

### Writing Security Definitions

- It's OK to be wrong — the purpose is to start the conversation and see if these can be broken
- Start with what the system SHOULD guarantee, then validate through threat analysis
- Reference the official vocabulary and existing definitions at [Security Definitions](https://contributing.bitwarden.com/architecture/security/definitions)
- Separate macro-level definitions (e.g., end-to-end encryption) from micro-level definitions specific to the feature
- Number definitions sequentially (SD1, SD2, SD3) within a feature area
- Each SD is a self-contained unit — one threat model, one security goal, one accepted status
- Include a glossary of feature-specific terms before the definitions when the feature introduces domain-specific vocabulary

## Bitwarden Security Principles

These six principles form the foundation for all threat modeling at Bitwarden. Reference them when writing security goals and evaluating threats.

| Principle | Name                                         | Core Guarantee                                                                                                                                                                                                                                       |
| --------- | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **P01**   | Servers are Zero Knowledge                   | Bitwarden infrastructure cannot access unencrypted user data. The server must not enable weakening of user-chosen protections, masquerade server data as user-encrypted content, or access encrypted data outside the client context.                |
| **P02**   | A Locked Vault is Secure                     | Highly sensitive vault data cannot be accessed in plaintext once the vault is locked, even if the device is compromised after locking. Platform limitations (e.g., JS memory) are mitigated through buffer clearing and available security features. |
| **P03**   | Limited Security on Semi-Compromised Devices | For unlocked vaults on devices with userspace malware (but intact OS/kernel), clients maximize kernel/OS-level protections and balance security with usability through controls like biometrics.                                                     |
| **P04**   | No Security on Fully Compromised Systems     | Bitwarden cannot guarantee vault protection when hardware or OS-level integrity is fully compromised. This applies to unlocked vaults only — locked vaults are covered by P02.                                                                       |
| **P05**   | Controlled Access to Vault Data              | Vault data, whether at rest or in use, is accessible only to authorized parties under the user's explicit control. Isolation mechanisms are critical in high-risk environments like web browsers.                                                    |
| **P06**   | Minimized Impact of Security Breaches        | Limit breach scope and duration through session invalidation, key rotation (countering "harvest now, decrypt later"), and post-compromise security (new data remains protected after a breach).                                                      |

**Controlled exceptions exist.** For example, P01 has documented exceptions for Key Connector (self-hosted SSO without passwords) and the Icons Service (plaintext domain names for favicons). When threat modeling, check the [principles documentation](https://contributing.bitwarden.com/architecture/security/principles/) for current exceptions.

## Security Requirements

Security requirements define concrete MUST/SHOULD/MAY obligations organized by category. Reference these when validating that a design satisfies Bitwarden's security standards:

- **VD (Vault Data)** — Protection at rest (encrypted with UserKey), allowances in use (decrypted during unlock), protection in transit (trusted channels), and export controls (informed consent required)
- **EK (Encryption Keys)** — UserKey requires 256-bit security strength, must be protected at rest and in transit, must never be exported
- **AT (Authentication Tokens)** — Protected storage at rest, mandatory transit protection
- **SC (Secure Channels)** — Confidentiality, integrity, replay prevention, forward secrecy for long-lived channels
- **TC (Trusted Channels)** — Secure channel properties plus receiver identity verification

Full requirements: [Security Requirements](https://contributing.bitwarden.com/architecture/security/requirements)

## STRIDE Framework

Use STRIDE as a guide for structured threat identification. Some vulnerabilities won't map cleanly to STRIDE — that's expected.

| Category                   | Question to Ask                                    | Example Threats                                               | Typical Mitigations                                      |
| -------------------------- | -------------------------------------------------- | ------------------------------------------------------------- | -------------------------------------------------------- |
| **Spoofing**               | Can an attacker impersonate a user or component?   | Forged auth tokens, session hijacking, credential stuffing    | Strong authentication, token validation, MFA             |
| **Tampering**              | Can an attacker modify data in transit or at rest? | Man-in-the-middle, database manipulation, parameter tampering | Integrity checks, signed payloads, TLS, input validation |
| **Repudiation**            | Can an attacker deny performing an action?         | Missing audit logs, unsigned transactions                     | Audit logging, digital signatures, timestamps            |
| **Information Disclosure** | Can an attacker access data they shouldn't?        | Verbose errors, insecure storage, side-channel leaks          | Encryption, access controls, error sanitization          |
| **Denial of Service**      | Can an attacker degrade or prevent service?        | Resource exhaustion, algorithmic complexity attacks           | Rate limiting, input size bounds, circuit breakers       |
| **Elevation of Privilege** | Can an attacker gain unauthorized access?          | Broken access control, privilege escalation, IDOR             | Authorization checks at every layer, least privilege     |

## Artifact Generation

### Data Flow Diagram (Mermaid)

Use Mermaid syntax for text-based DFDs that can be version-controlled:

```mermaid
graph LR
    subgraph Trust Boundary: Client
        A[Browser Extension] --> B[Client SDK]
    end

    subgraph Trust Boundary: Network
        B -->|TLS| C[API Gateway]
    end

    subgraph Trust Boundary: Server
        C --> D[Identity Service]
        C --> E[API Service]
        E --> F[(Database)]
        E --> G[Key Management]
    end

    style A fill:#e1f5fe
    style F fill:#fff3e0
```

Include: components, data stores, external entities, data flows with protocols, and trust boundaries.

Note: Bitwarden is moving toward a Structurizr-based approach for persistent architecture diagrams. For ad-hoc threat modeling, Mermaid or Excalidraw are acceptable.

### Security Definition Document

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

### Threat Catalog

| #   | Threat      | STRIDE      | Component          | Existing Mitigation | Proposed Mitigation  | Risk Level               |
| --- | ----------- | ----------- | ------------------ | ------------------- | -------------------- | ------------------------ |
| 1   | Description | S/T/R/I/D/E | Affected component | What exists today   | What should be added | Critical/High/Medium/Low |

### Mitigation Tracking

For threats without existing mitigations, document for Jira follow-up:

```markdown
## Unmitigated Threat: [Title]

- **Threat:** [Description]
- **STRIDE Category:** [Category]
- **Affected Component:** [Component]
- **Impact:** [What happens if exploited]
- **Proposed Mitigation:** [What to implement]
- **Priority:** [Based on risk assessment]
```

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
