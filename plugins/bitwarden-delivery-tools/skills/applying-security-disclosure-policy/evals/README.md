# applying-security-disclosure-policy evals

Behavior test cases for the `applying-security-disclosure-policy` skill, in the `skill-creator` schema.

`evals.json` holds five cases, one per branch of the skill's decision: a VULN-linked fix (high-confidence `Yes`), a session-handling fix with no Jira signal (the heuristic tier asks once), a dependency bump (`No`, with no fetch), a confirmed fix with the Atlassian plugin missing (`Stop`), and a branch named for a `VULN-*` key (the key stays out of the title). Each case's `expectations` are the pass criteria.

Cases are **advice-only**: the graded artifact is the stated plan or draft, and nothing is committed or submitted. Every ticket key uses the `-999NN` range so no case describes a real vulnerability record.

Run with `/skill-creator:skill-creator` in Benchmark mode, `with-skill` against `without-skill`, three runs per config, with a config-blind grader. Point each subagent at the skill by file path, not by name, since the installed plugin cache lags the working tree. Tell it the run is non-interactive, so a question is stated as plain text rather than sent to a live person.

The cases need two different environments. Cases 1 and 5 need a working Confluence fetch: `bitwarden-atlassian-tools` installed and valid Atlassian credentials with access to the APPSEC space. Without that, the skill correctly returns `Stop`, and cases 1 and 5 accept that outcome but no longer test the wording rules. Case 4 depends on `get_confluence_page` being unavailable. Run it without `bitwarden-atlassian-tools` installed, or with the MCP server disabled. Cases 2 and 3 never reach the fetch, so they work in either.

`behavior-baseline.json` records the pass rate per case, keyed by model and effort, with denominators of expectations × runs. The current numbers come from the 2026-09-30 run: Sonnet 5.5 runners, a blind Opus 5.5 grader, three runs per config. Case 3 ties by design, because it is the negative control and only catches over-triggering. Regression check:

```bash
diff <(jq -S . behavior-baseline.json) <(jq -S . result.json)
```

An empty diff means no regression. When a change is intentional, replace `behavior-baseline.json` with the new results in the same PR as the skill change.
