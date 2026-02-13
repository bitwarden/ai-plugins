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
