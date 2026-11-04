# Adaptive assertion evaluation

After any assertion step fails, apply this evaluation before recording the result:

1. Review page content, visible text, error messages, and element content already in your context and screenshots. If that is not enough, gather more with read-only calls: `snapshot`, `eval` and `run-code` reads of the DOM, `console`, `requests`, and `response-body`. Do NOT click, fill, navigate, reload, or otherwise change the page.
2. Ask: "Is the semantic condition this assertion was checking — the underlying behavior or content the test intends to verify, independent of the specific selector or element path specified — demonstrably present in what I observed?"
   - A condition you could not have observed, such as a toast that dismissed before your read, is not absent. It is present when the page shows the outcome it stands for and no response to the triggering action failed.
   - A response status can support page evidence but never stands alone.
3. Apply the rule to each failed assertion individually:
   - If **all** failed assertions resolve adaptively → record the test case as `PASS (adaptive)`
   - If **any** failed assertion represents a genuine failure → record `FAIL`; document the adaptive assessments for the resolved assertions in Notes
4. When recording `PASS (adaptive)`, write in Notes:
   - What the plan's assertion specified
   - What was actually found, including any evidence gathered in step 1
   - Why the semantic condition is considered met
5. Do NOT apply adaptive evaluation when:
   - The feature behavior itself is wrong (e.g., the server accepted input it should have rejected)
   - The expected content or behavior is genuinely absent from the page
   - The test could not run due to environment state (dirty database, missing seed data, skipped `[HUMAN]` step)
   - The failed assertion was a URL/navigation check (wrong URL always means wrong behavior)
