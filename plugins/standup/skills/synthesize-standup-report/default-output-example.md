## Output format

**Each blocker must state the impediment AND the unblock path or ask. 'Many, but nothing urgent' is acceptable if at least one specific anchor is named.**

**Include explicit artifact-state hedging for all items in non-terminal states: do not imply completion for items in Code Review, Returned from QA, or Blocked. When 4 or more items are in non-terminal states, add one throughput self-assessment sentence (e.g., "appear to be keeping up") to the BLUF summary.**

**Preserve all four earned hedge types: artifact-state (uncertainty about completion), throughput self-assessment (pacing reads), path-uncertainty (genuine decision forks), and organizational/social (relational reads). Earned hedging is a positive signal.**

**Verify each claim verb matches the ticket's real status. Never use Fixed/Shipped/Landed/Resolved/Delivered for tickets not in terminal Done/Merged state. Use Iterating on, Returned from QA on, In Progress on for in-flight work.**

**RAG status line must be the very first line of the report body.**

**Avoid effort verbs (Continue, Progress, Advance, Drive, Reviewed, Gave, Organized, Begin). Use outcome verbs: Shipped, Fixed, Landed, Delivered, Closed, Resolved.**

**Outcome bullets only — no effort narration, no ticket-list enumeration.**

**Constraint: max 6 bullets per section; each bullet <= 30 words. Max 12 bullets total across all sections combined.**

**Each bullet must express exactly one idea — no "and" or ";" joining two distinct items.**

The default report opens with a one-sentence summary line carrying a red/amber/green (RAG) status signal, then a `Last week` section, a `This week` section, and a `Blockers` section. Each bullet carries its prose on the first line; ticket links and status appear on a continuation line as _[TICKET](link)_, `Status`.

```
:large_green_circle: Steady progress on three active tracks; no blockers.

`Last week:`
- Resolved a request-timeout regression in the vault sync flow
  *[PM-12345](https://example.atlassian.net/browse/PM-12345)*, `Done`
- Delivered feedback on device-trust onboarding PR key-derivation boundary
  *[your-org/your-repo#9876](https://github.com/your-org/your-repo/pull/9876)*
- Landed Q3 auth initiative ticket structure across four epics
  *[BW-456](https://example.atlassian.net/browse/BW-456)*, *[BW-457](https://example.atlassian.net/browse/BW-457)*

`This week:`
- Land SSO session-binding refactor
  *[PM-23456]*, `In Development`
- Scope emergency-access flow redesign
  *[PM-34567]*, `In Development`

`Blockers:`
- None
```
