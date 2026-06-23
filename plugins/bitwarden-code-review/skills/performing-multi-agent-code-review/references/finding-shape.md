# Finding Shape

Every finding and every Step 4/5 return object follows the JSON schema below. Subagents emit JSON arrays; the main orchestrator parses by field.

## Finding object (created in Steps 2 and 3)

Emit as a JSON array. Each finding:

| field          | type    | notes                                                                            |
| -------------- | ------- | -------------------------------------------------------------------------------- |
| `id`           | string  | `{source}-{n}`, e.g. `"bug-3"`. Source ∈ `arch`, `quality`, `bug`, `sec`, `val`. |
| `file`         | string  | Repo-relative path.                                                              |
| `line`         | string  | `"42"` or `"42-50"`. Derived per Line Number Accuracy.                           |
| `severity`     | string  | `"blocker"` \| `"important"` \| `"refactor"`.                                    |
| `confidence`   | integer | 0–100. Only findings ≥ 80 are emitted.                                           |
| `title`        | string  | < 100 chars. Renders as the section header in the final report.                  |
| `detail`       | string  | Markdown. Explanation, why it matters, suggested fix.                            |
| `source_agent` | string  | `"architect"` \| `"quality"` \| `"bug"` \| `"security"` \| `"validation"`.       |

If an agent produces no findings, return `[]`.

The orchestrator renders `source_agent` on every finding in the final report — set it accurately. The id-prefix → source_agent mapping is fixed: `arch → architect`, `quality → quality`, `bug → bug`, `sec → security`, `val → validation`.

## Step 4 return (validation)

One entry per incoming finding, keyed by `id`:

| field              | type   | notes                                     |
| ------------------ | ------ | ----------------------------------------- |
| `id`               | string | Matches input.                            |
| `status`           | string | `"validated"` \| `"dismissed"`.           |
| `dismissal_reason` | string | Present only when `status = "dismissed"`. |

**Collateral findings** produced during Step 4 (per the collateral-change check) use the full **Finding object** schema above with `source_agent: "validation"` and `id: "val-N"`. They append to Step 5's input.

Extra fields beyond this schema are ignored by the merge — creation-time fields come only from the original Finding object, never from Step 4 or Step 5 returns.

```json
// Example Step 4 return
[
  { "id": "arch-1", "status": "validated" },
  {
    "id": "quality-3",
    "status": "dismissed",
    "dismissal_reason": "Substantively covered by arch-1 at higher severity."
  },
  {
    "id": "val-1",
    "file": "plugins/example/.claude-plugin/plugin.json",
    "line": "4",
    "severity": "refactor",
    "confidence": 100,
    "title": "quality findings cite wrong file line for plugin.json description field",
    "detail": "Both citations are diff-offset artifacts; the description field is at file line 4.",
    "source_agent": "validation"
  }
]
```

## Step 5 return (severity audit)

One entry per incoming finding, keyed by `id`:

| field              | type   | notes                                             |
| ------------------ | ------ | ------------------------------------------------- |
| `id`               | string | Matches input.                                    |
| `status`           | string | `"confirmed"` \| `"downgraded"` \| `"dismissed"`. |
| `final_severity`   | string | Severity value. Omit when `status = "dismissed"`. |
| `dismissal_reason` | string | Present only when `status = "dismissed"`.         |

```json
// Example Step 5 return
[
  { "id": "arch-1", "status": "confirmed", "final_severity": "important" },
  {
    "id": "val-1",
    "status": "dismissed",
    "dismissal_reason": "A meta-observation about sibling findings is not a code issue in the change under review."
  }
]
```

## Orchestrator behavior

- Maintains a master finding map keyed by `id`.
- Each step's return merges into the master object by `id`.
- Creation-time fields — `severity`, `confidence`, `source_agent`, `title`, `detail`, `file`, `line` — are set by the Step 2/3 agent and **MUST NOT** be rewritten in Step 4, Step 5, or Step 6 merge. Step 4 and Step 5 returns carry only `id`, `status`, and disposition fields by design; the merge MUST preserve all creation-time fields from the original Step 2/3 finding.
- For dismissed findings, the orchestrator records a `dismissal_stage` field on the master-map entry: `"Step 4 validation"` if Step 4 set the dismissal status, or `"Step 5 severity audit"` if Step 5 did. This field is rendered in the final report as `**Dismissed at:**`.
- Step 6 partitions the master map by final status (validated vs dismissed); Steps 7–9 format, print, and write the report.
