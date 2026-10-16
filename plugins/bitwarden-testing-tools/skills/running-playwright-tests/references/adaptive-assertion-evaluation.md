# Adaptive assertion evaluation

After any assertion step fails, apply this evaluation before recording the result — using only what you already observed during normal execution:

1. Review page content, visible text, error messages, and element content already in your context and screenshots. Do NOT issue additional browser calls.
2. Ask: "Is the semantic condition this assertion was checking — the underlying behavior or content the test intends to verify, independent of the specific selector or element path specified — demonstrably present in what I already observed?"
3. Apply the rule to each failed assertion individually:
   - If **all** failed assertions resolve adaptively → record the test case as `PASS (adaptive)`
   - If **any** failed assertion represents a genuine failure → record `FAIL`; document the adaptive assessments for the resolved assertions in Notes
4. When recording `PASS (adaptive)`, write in Notes:
   - What the plan's assertion specified
   - What was actually found
   - Why the semantic condition is considered met
5. Do NOT apply adaptive evaluation when:
   - The feature behavior itself is wrong (e.g., the server accepted input it should have rejected)
   - The expected content or behavior is genuinely absent from the page
   - The test could not run due to environment state (dirty database, missing seed data, skipped `[HUMAN]` step)
   - The failed assertion was a URL/navigation check (wrong URL always means wrong behavior)
