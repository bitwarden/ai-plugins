# applying-security-disclosure-policy evals

Behavior test cases for the `applying-security-disclosure-policy` skill, in the `skill-creator` schema.

`evals.json` holds six cases, one per branch of the skill's decision: a VULN-linked fix (high-confidence `Yes`), a session-handling fix with no Jira signal (the heuristic tier asks once), a dependency bump whose ticket can't be read (the skill fails closed and asks, with no fetch), a confirmed fix with the Atlassian plugin missing (`Stop`), a branch named for a `VULN-*` key (the key stays out of the title), and a ticket whose Jira lookup fails (the skill asks rather than returning `No`). Each case's `expectations` are the pass criteria.

Cases are **advice-only**: the graded artifact is the stated plan or draft, and nothing is committed or submitted. Every ticket key uses the `-999NN` range so no case describes a real vulnerability record.

Run with `/skill-creator:skill-creator` in Benchmark mode, `with-skill` against `without-skill`, three runs per config, with a config-blind grader. Point each subagent at the skill by file path, not by name, since the installed plugin cache lags the working tree. Tell it the run is non-interactive, so a question is stated as plain text rather than sent to a live person.

Run each trial as its own `claude -p` session with auto memory off (`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`), from an empty working directory so no `CLAUDE.md` loads. Subagents of a normal session inherit the user's auto memory, and a saved note about the disclosure policy is enough to lift the `without-skill` arm. Make the no-plugin cases real with `--disallowedTools` on the Atlassian MCP tools rather than telling the runner they are missing, and tell runners to call a tool rather than predict its result.

The cases need two different environments. Cases 1 and 5 need a working Confluence fetch: `bitwarden-atlassian-tools` installed and valid Atlassian credentials with access to the APPSEC space. Without that, the skill correctly returns `Stop`, and cases 1 and 5 accept that outcome but no longer test the wording rules. Case 4 depends on `get_confluence_page` being unavailable. Run it without `bitwarden-atlassian-tools` installed, or with the MCP server disabled. Cases 2, 3, and 6 use fictional ticket keys, which the skill can't read whether or not the plugin is installed, so it fails closed and asks the author in all three. Case 3 checks that it asks even for a routine dependency bump; case 6 checks a lookup that really runs and fails, so it needs the plugin installed.

`behavior-baseline.json` records the pass rate per case, keyed by model and effort, with denominators of expectations × runs. The current numbers come from the 2026-11-23 run: Opus 5.5 runners with auto memory off, a blind Opus 5.5 grader, three runs per config. No case is a control for over-asking any more: with the fail-closed rule, the skill should ask in case 3 too, and it stays quiet only when there is no ticket key. Regression check:

```bash
diff <(jq -S . behavior-baseline.json) <(jq -S . result.json)
```

An empty diff means no regression. When a change is intentional, replace `behavior-baseline.json` with the new results in the same PR as the skill change.
