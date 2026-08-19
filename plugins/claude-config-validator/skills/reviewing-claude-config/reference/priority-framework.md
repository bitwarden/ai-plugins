# Priority Framework for Claude Configuration Reviews

Classification system for prioritizing issues found in Claude configuration files.

---

## Priority Levels

### CRITICAL

**Definition:** Issues that prevent functionality, expose security vulnerabilities, or cause immediate harm.

**Examples:**

- settings.local.json committed to git
- Hardcoded API keys, tokens, or passwords
- Missing YAML frontmatter (skill won't be recognized)
- Dangerous command auto-approvals (rm -rf, chmod 777)
- Overly broad permissions exposing sensitive paths
- An agent tool grant reaching credentials or destructive commands
- Broken file references preventing skill loading

**Action Required:** Must fix immediately before approval.

**Finding Format:**

```
**CRITICAL**: [Issue description]

[Specific fix with code example]

This must be fixed before approval because [security/functionality reason].
```

---

### IMPORTANT

**Definition:** Functional defects and security regressions that do not stop the file loading. The configuration works, but it does the wrong thing, or does it less safely than it should.

Quality, style, and readability observations are **not** IMPORTANT — they are SUGGESTED. The test is whether the behavior is wrong, not whether the prose could be better.

**Examples:**

- Permissions broader than the stated purpose needs
- Agent tool grant broader than its description justifies
- Vague activation triggers, so the skill or agent never fires
- Incorrect field names, or missing non-required fields the feature depends on
- A documented behavior the configuration does not actually implement

**Action Required:** Should fix in this PR/commit. If time-constrained, create follow-up issue. Does not block the review — see the verdict rule in `../SKILL.md` Step 5.

**Finding Format:**

```
**IMPORTANT**: [Issue description]

[Specific recommendation]

[Rationale explaining why this matters]
```

---

### SUGGESTED

**Definition:** Improvements that enhance quality but aren't essential for approval. Most readability, structure, and documentation observations land here.

**Examples:**

- Duplicated documentation content
- Poor progressive disclosure (file > 500 lines)
- Missing structured thinking blocks
- Unclear purpose statements
- Missing examples for complex concepts
- Inefficient token usage patterns
- Better file organization
- Alternative approaches

**Action Required:** Optional improvements. Consider for future work.

**Finding Format:**

```
**SUGGESTED**: [Improvement suggestion]

[What would be better and why]

This would improve [aspect] but isn't required for approval.
```

---

### OPTIONAL

**Definition:** Personal preferences, alternative approaches, or minor stylistic choices.

**Examples:**

- Alternative phrasing
- Different organizational structure
- Stylistic preferences
- Personal coding style

**Action Required:** Author decides. No expectation to change.

**Finding Format:**

```
**OPTIONAL**: [Observation or suggestion]

[Alternative approach if applicable]

This is a personal preference - feel free to keep current approach.
```

---

## Classification Decision Tree

Use this structured thinking approach to classify issues:

<thinking>
1. Does this create a security vulnerability or stop the file loading?
   → YES: CRITICAL
   → NO: Continue

2. Does the configuration behave wrongly or less safely than intended, while still loading?
   → YES: IMPORTANT
   → NO: Continue

3. Would fixing it improve quality, readability, or structure?
   → YES: SUGGESTED
   → NO: OPTIONAL

Behavior decides between CRITICAL, IMPORTANT, and SUGGESTED. "This reads badly" never
reaches IMPORTANT, however strongly you feel it.
</thinking>

---

## Context-Specific Priority Adjustments

### Security Context

In security-sensitive configurations (settings.json, permissions):

- Elevate permission issues to CRITICAL
- Elevate secret exposure to CRITICAL
- Broad permissions: IMPORTANT → CRITICAL

### Marketplace-Bound Components

A component published to a marketplace is read and installed by people who did not write it. That raises the stakes of a discoverability defect, but it does not change any severity: unclear activation triggers are already IMPORTANT at baseline, because a component that never fires is functionally broken whoever installs it.

So there is no marketplace escalation. Do not elevate readability or organization to CRITICAL for marketplace components — CRITICAL means broken or unsafe, and that bar does not move with the audience.

### Internal Tools

For internal-only configurations:

- May accept some SUGGESTED issues
- Still require CRITICAL fixes
- IMPORTANT issues can be follow-up work

---

## Priority by Issue Type

### Security Issues

| Issue                                                             | Priority  |
| ----------------------------------------------------------------- | --------- |
| Committed settings.local.json                                     | CRITICAL  |
| Hardcoded API keys/tokens                                         | CRITICAL  |
| Dangerous auto-approved commands                                  | CRITICAL  |
| Overly broad permissions (Read://_, Write://_)                    | CRITICAL  |
| Permissions exposing ~/.ssh, /etc                                 | CRITICAL  |
| Permissions broader than needed                                   | IMPORTANT |
| Agent tool grant reaching credentials or destructive commands     | CRITICAL  |
| Agent tool grant otherwise broader than its description justifies | IMPORTANT |

### Structure Issues

| Issue                                           | Priority  |
| ----------------------------------------------- | --------- |
| Missing YAML frontmatter                        | CRITICAL  |
| Broken file references                          | CRITICAL  |
| File > 500 lines without progressive disclosure | SUGGESTED |
| Poor file organization                          | SUGGESTED |
| Missing structured thinking blocks              | SUGGESTED |

### Quality Issues

| Issue                                 | Priority  |
| ------------------------------------- | --------- |
| No activation triggers in description | IMPORTANT |
| Vague or unclear instructions         | SUGGESTED |
| Missing examples for complex concepts | SUGGESTED |
| Duplicated documentation              | SUGGESTED |
| Inefficient token usage               | SUGGESTED |
| Additional examples would help        | SUGGESTED |
| Alternative phrasing                  | OPTIONAL  |

Only the first is IMPORTANT, and only because a description with no triggers means the component never fires — a functional defect. The rest are readability, and readability does not fail a review.

### Syntax Issues

| Issue                      | Priority  |
| -------------------------- | --------- |
| Invalid JSON syntax        | CRITICAL  |
| Malformed YAML frontmatter | CRITICAL  |
| Incorrect field names      | IMPORTANT |
| Missing required fields    | IMPORTANT |
| Deprecated fields          | SUGGESTED |

---

## Multi-Issue Prioritization

When multiple issues exist in a single review:

1. **Group by priority level** (CRITICAL together, IMPORTANT together, etc.)
2. **Within each level, order by:**
   - Security issues first
   - Functionality issues second
   - Quality issues third
3. **Focus findings on highest priorities**
4. **May skip OPTIONAL issues if many higher-priority issues exist**

---

## Communication Guidelines by Priority

### CRITICAL

- **Tone:** Direct and firm
- **Language:** "Must fix", "Required", "Blocks approval"
- **Explanation:** Always explain the risk/impact
- **Solution:** Always provide specific fix

### IMPORTANT

- **Tone:** Strong recommendation
- **Language:** "Should fix", "Recommended", "Significantly improves"
- **Explanation:** Explain why it matters
- **Solution:** Provide specific recommendation

### SUGGESTED

- **Tone:** Helpful suggestion
- **Language:** "Consider", "Would improve", "Could enhance"
- **Explanation:** Brief rationale
- **Solution:** Optional, may suggest alternatives

### OPTIONAL

- **Tone:** Neutral observation
- **Language:** "Alternative approach", "Personal preference"
- **Explanation:** Acknowledge it's not critical
- **Solution:** Present as option, not directive

---

## Example Classifications

**Example 1: Security Issue**

❌ **settings.json:5** - settings.local.json committed to git
**Priority:** CRITICAL
**Rationale:** Exposes potentially sensitive user-specific configuration and API keys.

---

**Example 2: Structure Issue**

❌ **SKILL.md:1** - Missing YAML frontmatter
**Priority:** CRITICAL
**Rationale:** Skill won't be recognized by Claude Code without frontmatter.

---

**Example 3: Quality Issue**

❌ **SKILL.md:3** - Description lacks activation triggers
**Priority:** IMPORTANT
**Rationale:** Users won't know when to invoke this skill. Reduces discoverability.

---

**Example 4: Improvement Suggestion**

❌ **checklist.md:45** - Could add more examples
**Priority:** SUGGESTED
**Rationale:** Additional examples would clarify complex concept, but current instruction is functional.

---

**Example 5: Style Preference**

❌ **SKILL.md:12** - Alternative phrasing possible
**Priority:** OPTIONAL
**Rationale:** Current phrasing is clear, alternative is just personal preference.
