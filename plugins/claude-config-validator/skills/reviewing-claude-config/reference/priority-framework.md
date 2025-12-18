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
- Broken file references preventing skill loading

**Action Required:** Must fix immediately before approval.

**Review Comment Format:**

```
**CRITICAL**: [Issue description]

[Specific fix with code example]

This must be fixed before approval because [security/functionality reason].
```

---

### IMPORTANT

**Definition:** Issues that significantly impact quality, maintainability, or user experience but don't prevent basic functionality.

**Examples:**

- Duplicated documentation content
- Poor progressive disclosure (file > 500 lines)
- Missing structured thinking blocks
- Vague activation triggers
- Unclear purpose statements
- Inefficient token usage patterns
- Missing examples for complex concepts

**Action Required:** Should fix in this PR/commit. If time-constrained, create follow-up issue.

**Review Comment Format:**

```
**IMPORTANT**: [Issue description]

[Specific recommendation]

[Rationale explaining why this matters]
```

---

### SUGGESTED

**Definition:** Improvements that enhance quality but aren't essential for approval.

**Examples:**

- Additional examples for clarity
- Better file organization
- More specific guidance
- Enhanced documentation
- Alternative approaches
- Stylistic improvements

**Action Required:** Optional improvements. Consider for future work.

**Review Comment Format:**

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

**Review Comment Format:**

```
**OPTIONAL**: [Observation or suggestion]

[Alternative approach if applicable]

This is a personal preference - feel free to keep current approach.
```

---

## Classification Decision Tree

Use this structured thinking approach to classify issues:

<thinking>
1. Does this issue create security vulnerability or prevent functionality?
   → YES: CRITICAL
   → NO: Continue

2. Does this significantly impact quality, maintainability, or UX?
   → YES: IMPORTANT
   → NO: Continue

3. Would this improve quality but not essential?
   → YES: SUGGESTED
   → NO: OPTIONAL
   </thinking>

---

## Context-Specific Priority Adjustments

### Security Context

In security-sensitive configurations (settings.json, permissions):

- Elevate permission issues to CRITICAL
- Elevate secret exposure to CRITICAL
- Broad permissions: IMPORTANT → CRITICAL

### Marketplace-Bound Skills

For skills intended for marketplace:

- Elevate missing examples to IMPORTANT
- Elevate unclear activation triggers to IMPORTANT
- Elevate poor progressive disclosure to CRITICAL

### Internal Tools

For internal-only configurations:

- May accept some SUGGESTED issues
- Still require CRITICAL fixes
- IMPORTANT issues can be follow-up work

---

## Priority by Issue Type

### Security Issues

| Issue                                          | Priority  |
| ---------------------------------------------- | --------- |
| Committed settings.local.json                  | CRITICAL  |
| Hardcoded API keys/tokens                      | CRITICAL  |
| Dangerous auto-approved commands               | CRITICAL  |
| Overly broad permissions (Read://_, Write://_) | CRITICAL  |
| Permissions exposing ~/.ssh, /etc              | CRITICAL  |
| Permissions broader than needed                | IMPORTANT |

### Structure Issues

| Issue                                           | Priority  |
| ----------------------------------------------- | --------- |
| Missing YAML frontmatter                        | CRITICAL  |
| Broken file references                          | CRITICAL  |
| File > 500 lines without progressive disclosure | IMPORTANT |
| Poor file organization                          | SUGGESTED |
| Missing structured thinking blocks              | IMPORTANT |

### Quality Issues

| Issue                                 | Priority  |
| ------------------------------------- | --------- |
| Vague or unclear instructions         | IMPORTANT |
| Missing examples for complex concepts | IMPORTANT |
| No activation triggers in description | IMPORTANT |
| Duplicated documentation              | IMPORTANT |
| Inefficient token usage               | SUGGESTED |
| Additional examples would help        | SUGGESTED |
| Alternative phrasing                  | OPTIONAL  |

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
3. **Focus review comments on highest priorities**
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

❌ **skill.md:1** - Missing YAML frontmatter
**Priority:** CRITICAL
**Rationale:** Skill won't be recognized by Claude Code without frontmatter.

---

**Example 3: Quality Issue**

❌ **skill.md:3** - Description lacks activation triggers
**Priority:** IMPORTANT
**Rationale:** Users won't know when to invoke this skill. Reduces discoverability.

---

**Example 4: Improvement Suggestion**

❌ **checklist.md:45** - Could add more examples
**Priority:** SUGGESTED
**Rationale:** Additional examples would clarify complex concept, but current instruction is functional.

---

**Example 5: Style Preference**

❌ **skill.md:12** - Alternative phrasing possible
**Priority:** OPTIONAL
**Rationale:** Current phrasing is clear, alternative is just personal preference.
