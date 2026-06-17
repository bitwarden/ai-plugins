## Core Vocabulary

Use Bitwarden's standard terminology when writing security definitions:

- **Vault Data** — A user's private information stored in Bitwarden (passwords, usernames, secure notes, credit cards, identities, attachments).
- **Protected Data** — Data stored in unreadable format (typically encrypted) with expectations about secure key storage.
- **Data at Rest / in Use / in Transit** — The three data states. "At rest" is stored data on disk. "In use" is data in volatile memory during processing. "In transit" is data moving between locations, processes, or devices.
- **Secure Channel** — A communication channel providing confidentiality (unreadable to unauthorized parties) and integrity (tamper-proof).
- **Trusted Channel** — A secure channel that also provides authenticity (verified identities of communicating parties).
- **Data Exporting** — Controlled process where data leaves Bitwarden unprotected, nullifying security guarantees. Requires informed and explicit consent.
- **Data Sharing** — Controlled data exchange within the Bitwarden secure environment (security guarantees maintained).
- **Data Leaking** — Unintentional departure of data from Bitwarden unprotected.
- **Bitwarden Secure Environment** — Any process or application adhering to Bitwarden's security standards.
