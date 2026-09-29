# applying-security-disclosure-policy evals

Behavior test cases for the `applying-security-disclosure-policy` skill, in the `skill-creator` schema.

`evals.json` holds five cases, one per branch of the skill's decision: a VULN-linked fix (high-confidence `Yes`), a session-handling fix with no Jira signal (the heuristic tier asks once), a dependency bump (`No`, with no fetch), a confirmed fix with the Atlassian plugin missing (`Stop`), and a branch named for a `VULN-*` key (the key stays out of the title). Each case's `expectations` are the pass criteria.

Cases are **advice-only**: the graded artifact is the stated plan or draft, and nothing is committed or submitted. Every ticket key uses the `-999NN` range so no case describes a real vulnerability record.

Run with `/skill-creator:skill-creator` in Benchmark mode, `with-skill` against `without-skill`, three runs per config, with a config-blind grader. Point each subagent at the skill by file path, not by name, since the installed plugin cache lags the working tree. Tell it the run is non-interactive, so a question is stated as plain text rather than sent to a live person.

Case 4 depends on `get_confluence_page` being unavailable. Run it without `bitwarden-atlassian-tools` installed, or with the MCP server disabled.
