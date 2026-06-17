## Security Principles (P01–P06)

Every design, review, and agent prompt must reason against these six principles. Quoted text is verbatim from the linked source.

- **P01 — Servers are zero knowledge.** "There is no possibility for an attacker or Bitwarden employee to access your unencrypted data by compromising Bitwarden's infrastructure." [6]
- **P02 — A locked vault is secure.** "Clients must ensure that highly sensitive vault data cannot be accessed in plain text once the vault has been locked, even if the device becomes compromised after the lock occurs." [7]
- **P03 — Limited security for vaults on semi-compromised devices.** "On such devices, clients must leverage available protections to prevent malware from accessing plaintext vault data while the vault is unlocked." [8]
- **P04 — No security on fully compromised systems.** "When hardware or OS-level integrity is fully compromised, vault data may become accessible to attackers." [9]
- **P05 — Controlled access to vault data.** "Clients must ensure that vault data, whether at rest or in use, is accessible only to authorized parties and always under the user's explicit control." [10]
- **P06 — Minimized impact of security breaches.** "Bitwarden should take available actions to help users limit the damage caused by such breaches, both in scope and duration." [11]

Always consider the **threat model** (what can an attacker do?) and **security goals** (what must an attacker NOT be able to do?). Evaluate every change against P01–P06 and the requirements under **VD** (Vault Data), **EK** (Encryption Keys), **AT** (Authentication Tokens), **SC** (Secure Channels), and **TC** (Trusted Channels) [5].
