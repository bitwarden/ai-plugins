---
argument-hint: [target user or time window] | (blank to use your preferences)
allowed-tools: Task
description: Generate a RAG-status standup report from your GitHub and Jira/Confluence activity
---

Invoke the `standup:standup-report-generator` agent to run the full standup pipeline: collect activity, synthesize the report, and deliver it.

Invoke the `Task` tool with:

- `subagent_type`: "standup:standup-report-generator"
- `description`: "Generate a standup report"
- `prompt`:
  - Always instruct the agent to load the preferences file as the baseline for every setting. If the user supplied an argument (a target GitHub/Jira user or a time window), pass it through as an override on top of those preferences: `Generate a standup report for: $ARGUMENTS. Load the preferences file and use it for every setting the argument does not specify.`
  - Otherwise: `Generate a standup report using the preferences file.`

The agent owns preflight, preference loading, and orchestration. Do NOT collect activity, synthesize, or deliver output yourself. The agent handles the entire pipeline.
