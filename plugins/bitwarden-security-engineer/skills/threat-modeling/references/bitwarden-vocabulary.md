# Bitwarden Security Vocabulary

Standard terminology for use in security definitions. Sourced from
[Security Definitions](https://contributing.bitwarden.com/architecture/security/definitions).

## Core Terms

- **Vault Data** — A user's private information stored in Bitwarden (passwords, usernames, secure notes, credit cards, identities, attachments)
- **Protected Data** — Data stored in unreadable format (typically encrypted) with expectations about secure key storage
- **Data at Rest** — Stored data not actively used or transmitted (disk storage on devices or servers)
- **Data in Use** — Data actively being processed or accessed, held in volatile memory
- **Data in Transit** — Data actively transferred between locations, processes, or devices
- **Secure Channel** — A communication channel providing confidentiality (unreadable to unauthorized parties) and integrity (tamper-proof)
- **Trusted Channel** — A secure channel that also provides authenticity (verified identities of communicating parties)
- **Data Exporting** — Controlled process where data leaves Bitwarden unprotected, nullifying security guarantees. Requires informed and explicit consent.
- **Data Sharing** — Controlled data exchange within the Bitwarden secure environment (security guarantees maintained)
- **Data Leaking** — Unintentional departure of data from Bitwarden unprotected
- **Bitwarden Secure Environment** — Any process or application adhering to Bitwarden's security standards

## Threat-Modeling Terms

- **Passive Observer** — An entity that sees data during normal operation without acting maliciously (e.g., LLM providers receiving tool I/O over the API, log aggregators, analytics pipelines, training-data collectors). Used to frame confidentiality harms that arise from _visibility_, not _attack_. Every SD involving a secret that crosses an external-service trust boundary should include at least one passive-observer framing.
- **Dominated Threat** — A threat whose attacker capabilities are strictly weaker than those of another threat already accepted as out-of-scope. Dominated SDs are pruned because their residual-risk statements collapse to tautologies (e.g., "equivalent to full user-account compromise"). They contribute no new information and dilute the signal of the SD document.
- **Exposure Window** — The bounded duration a secret is accessible in a less-protected context (e.g., a password held in child-process environment variables during an unlock operation). When Accepted Goal Status justifies residual risk on the grounds that exposure is "brief" or "short-lived", the window MUST be quantified (typical and worst-case duration).
