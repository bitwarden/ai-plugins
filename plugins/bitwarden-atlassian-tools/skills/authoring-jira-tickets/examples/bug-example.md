# Bug Example — Custom Icon Renders Blank on Item List

This is a complete example output `.md` file for a Bug ticket. It demonstrates the format and writing style expected by the skill.

---

## Filename

`bug-custom-icon-renders-blank-on-item-list.md`

---

## Output

```markdown
# Custom Icon Renders Blank Image on Item List (web)

**Type:** Bug

---

**DESCRIPTION**

# Purpose

Custom icons set on items display as a blank white square in the item list and item detail views on web. The issue does not affect default icons or favicon-fetched icons — only icons uploaded directly by the user.

# Risks / Considerations

- If the root cause is a CDN caching issue, the fix may require a cache invalidation step that affects all users — coordinate with infrastructure before releasing

# Questions and Answers

[STATUS: Open] **Does this affect the mobile clients as well, or is it web-only?**
> Not yet confirmed. Mobile testing needed before closing.

# External References

- [Custom icon upload documentation](LINK TO BE PROVIDED)

---

**REPLICATION STEPS**

1. Log in to an account that has at least one item with a custom icon uploaded
2. Navigate to the item list
3. Observe the icon column for the item with a custom icon

**Expected Result:** The custom icon image appears in the icon column.

**Actual Result:** A blank white square appears in place of the custom icon.

**Build Version:** 2024.11.1

---

**QA TESTING NOTES**

- Test with icons in multiple formats (PNG, JPG, SVG) — the blank may be format-specific
- Test on both Chrome and Firefox; the defect was first observed on Chrome
- Accounts without any custom icons are not affected and do not need to be included in the test run
```

---

## Annotation

**What this example shows:**

- Title names the symptom and where it occurs, not the root cause (root cause is unknown at filing time)
- Description states what is broken and where without restating the replication steps — one short paragraph
- Risks / Considerations, Questions and Answers, and External References are Description sub-sections inside the DESCRIPTION block — they use `# H1` headings and have no `---` separators between them
- Replication Steps and QA Testing Notes are standalone Jira fields — they follow a `---` and use `**BOLD ALL-CAPS**` labels
- Replication Steps start with account setup (step 1 establishes the required state before the user does anything)
- Expected / Actual / Build Version are clearly labeled subsections
- QA Testing Notes adds three pieces of information that aren't derivable from the steps alone: format variants, browser scope, and which accounts to skip
- No Scenarios, Acceptance Criteria, Technical Breakdown, or Scope — none of these apply to a Bug
- Risks / Considerations flags a coordination concern (cache invalidation) that QA and product should know about
- Questions and Answers captures a genuinely open question (mobile scope) so it doesn't get lost
- External References used for one link — the icon upload docs that inform the test setup; primary repro is self-contained in the steps
