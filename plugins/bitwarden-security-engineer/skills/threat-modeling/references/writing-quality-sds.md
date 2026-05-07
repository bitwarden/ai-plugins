# Writing Quality Security Definitions

Security definitions exist to communicate the security posture of a system to reviewers, auditors, and future maintainers. A noisy or poorly-scoped SD document is worse than a shorter honest one — it hides the threats that actually matter behind threats that do not.

This reference collects the recurring anti-patterns that degrade SD quality and the checks to apply before shipping.

## Anti-patterns

### 1. The dominated threat

**Symptom.** An SD describes an attacker whose capabilities are strictly weaker than an attacker already accepted as out-of-scope. The residual-risk statement ends up saying "this is equivalent to full user-account compromise, which is outside our threat model."

**Example.** A tool that wraps a local CLI binary adds an SD about a malicious replacement of that binary on `PATH`. If the threat model already treats _full local-user compromise_ as out-of-scope, then a same-user attacker who can replace the binary could equivalently prompt the user for their password through any other mechanism — the threat reduces to one already accepted.

**Why it's bad.** The SD contributes no new information and consumes reviewer attention. Its presence suggests the document is comprehensive when it is really just long.

**Fix.** Delete the SD. If there is a _narrower_ concern worth keeping (e.g., the tool should refuse to run if the binary's path is not a known install location), write that narrower SD, not the dominated one.

### 2. The adversarial-only attacker

**Symptom.** An SD frames a confidentiality concern as an adversary actively trying to exfiltrate data, when the actual risk is _passive visibility_ during normal operation.

**Example.** A feature routes a master password through an external AI service. The generated SD reads: "A prompt-injected or malicious LLM attempts to trick the user into revealing their master password." The real threat is simpler and more serious: _the password is now visible to the LLM provider_, which may log it, surface it in support tooling, or incorporate it into training data. No malicious intent is required for the harm.

**Why it's bad.** Adversarial framing makes the threat feel exotic and low-probability when in fact the harm is inherent to the data flow. Reviewers may accept residual risk on the grounds that adversarial LLMs are rare, missing the systemic issue.

**Fix.** Whenever a secret or protected data crosses a trust boundary into an external service, write at least one SD whose attacker is an **honest-but-curious Passive Observer** (see vocabulary). If both the adversarial and passive framings are interesting, write both — but do not omit the passive one.

### 3. The unenforceable goal

**Symptom.** A security goal claims a secret is "cleared from memory", "zeroized", or "not retained", in a runtime that cannot make that guarantee.

**Example.** A Node.js server asserts that a session token MUST be cleared from process memory after use. JavaScript is garbage-collected and interns strings; there is no reliable way to overwrite a string's backing storage or to force eviction. The goal is unenforceable by any mechanism available to the application.

**Why it's bad.** Unenforceable goals erode trust in the document. Either the reviewer catches the contradiction and the SD loses credibility, or they don't and the document misrepresents the system's security posture.

**Fix.** Restate the goal in terms the runtime _can_ enforce — minimize the number of references, keep the secret scoped to the shortest possible function/process lifetime, isolate into a child process or separate process, use language features that provide zeroization when available (e.g., Rust's `Zeroize`, SDK boundaries). If none of those apply, mark Accepted Goal Status as explicitly _not met_ and link to the systemic runtime limitation so the honest answer is on record.

### 4. The aspirational limitation

**Symptom.** A threat-model limitation ("Attacker does not have X") assumes a privilege level that is not actually required for the capability in question on the target platforms.

**Example.** An SD claims the threat model excludes "attackers with kernel-level privileges" as justification for why a secret in process environment variables is safe. On Linux (per-user process visibility via `/proc/<pid>/environ`) and on Windows (via unprivileged APIs on the same user session), reading another process's environment does not require kernel privileges. The limit is aspirational, not factual.

**Why it's bad.** The SD's entire scoping depends on a limitation that does not hold, so its conclusions are unsound. Worse, the limitation _sounds_ reassuring, so downstream readers may build on it without checking.

**Fix.** For every "Attacker does not have X" clause, verify X actually requires the privilege claimed on every OS/runtime in scope. If not, either narrow the clause ("Attacker does not have another process running under the same user account") or accept the broader capability and restate the goal to defend against it.

### 5. The shell-quoting SD

**Symptom.** An SD describes a threat where a future maintainer edits a hardcoded constant to contain shell metacharacters (backticks, `$`, backslashes, newlines), breaking out of a quoted string into arbitrary code execution.

**Example.** An SD reads: "Attacker is a future maintainer who edits `DIALOG_TITLE` to contain quotes or backticks, breaking out of the AppleScript string context." The only mitigation available is "code review notices the constant change" — which is code quality practice, not a security control.

**Why it's bad.** The mitigation is "don't edit the constant in a dangerous way", which is not a security boundary. These SDs conflate secure-coding practice with threat modeling. They are almost always low-criticality and generate noise that masks higher-criticality SDs.

**Fix.** Do not write an SD whose only mitigation is code review or author discipline. If the constant truly needs to be treated as tainted input, refactor the code to handle it safely (parameterized execution, no shell interpolation). The safety is then a property of the implementation, not an SD.

### 6. The "brief exposure" trap

**Symptom.** Accepted Goal Status justifies residual risk with "brief", "short-lived", or "transient" — without a number.

**Example.** "The secret is held in child-process environment for only a brief window during unlock" — when unlock duration scales with KDF iterations and vault size, and may run for several seconds on representative hardware. During that window, every process running under the same user can observe it.

**Why it's bad.** "Brief" is a hope, not a bound. It lets reviewers mentally round down to "instant" when the real window may be long enough to matter for an attacker with a concurrent process.

**Fix.** Quantify the exposure window. State the typical and worst-case duration, and name what is running that could observe it. If you cannot quantify it, you cannot claim it is short enough to accept — remove the acceptance rationale and treat the goal as not met.

## Self-consistency checklist

Run these five checks before shipping a set of SDs. If any fails, fix the SD — do not ship it and rely on reviewers to catch the inconsistency.

1. **Spec ↔ implementation.** For every capability the threat model puts in-scope, does a goal defend against it, and does the implementation actually uphold that defense? If the goal forbids exposure to `process.env` but the implementation passes the secret through env, the SD is wrong.
2. **Runtime feasibility.** Can the language/runtime actually uphold every goal as written? Flag any goal that relies on memory clearing, zeroization, or non-retention in a GC'd / interned-string runtime.
3. **Platform reality.** For every "Attacker does not have X" clause, is X actually restricted on every supported OS? Reading another process's env, enumerating open handles, and inspecting argv are not kernel-privileged on common platforms.
4. **Passive-observer coverage.** For every secret or protected datum that crosses into an external service (LLM provider, log aggregator, analytics, training pipeline), is there an SD with a passive/honest-but-curious attacker? Adversarial framing alone is not sufficient.
5. **Criticality and ordering.** Does every SD carry a Criticality tag (Critical / High / Medium / Low), and is the document ordered by Criticality descending? If not, the reader will anchor on whichever SD appears first, not the one that matters most.

## Prioritization heuristic

Before including an SD, ask: _"If this threat did not exist, would the design change?"_

- **Yes** → the SD is load-bearing. Keep it.
- **No** → the SD is commentary. Cut it, or move it to a secure-coding notes section that is clearly not part of the SD document.

A 5-SD document that survives this filter is more valuable than a 15-SD document that does not. Verbosity is a failure mode — the early iterations of LLM-generated code review taught the organization this lesson already, and the same dynamic applies to LLM-generated security definitions.
