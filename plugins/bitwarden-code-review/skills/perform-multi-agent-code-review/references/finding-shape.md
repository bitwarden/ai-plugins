# Finding Shape

Every finding and every Step 4/5 return object follows the JSON schema below. Subagents emit JSON arrays; the main orchestrator parses by field.

## Finding object (created in Steps 2 and 3)

Emit as a JSON array. Each finding:

| field          | type    | notes                                                                             |
| -------------- | ------- | --------------------------------------------------------------------------------- |
| `id`           | string  | `{source}-{n}`, e.g. `"bug-3"`. Source ∈ `arch`, `quality`, `simp`, `bug`, `sec`, `val`. |
| `file`         | string  | Repo-relative path.                                                               |
| `line`         | string  | `"42"` or `"42-50"`. Derived per Line Number Accuracy.                            |
| `severity`     | string  | `"blocker"` \| `"important"` \| `"refactor"` \| `"suggestion"`.                   |
| `confidence`   | integer | 0–100. Only findings ≥ 80 are emitted.                                            |
| `title`        | string  | < 100 chars. Renders as the section header in the final report.                   |
| `detail`       | string  | Markdown. Explanation, why it matters, suggested fix.                             |
| `source_agent` | string  | `"architect"` \| `"quality"` \| `"simplification"` \| `"bug"` \| `"security"` \| `"validation"`.    |

If an agent produces no findings, return `[]`.

The orchestrator renders `source_agent` on every finding in the final report — set it accurately. The id-prefix → source_agent mapping is fixed: `arch → architect`, `quality → quality`, `simp → simplification`, `bug → bug`, `sec → security`, `val → validation`.

## Step 4 return (validation)

One entry per incoming finding, keyed by `id`:

| field              | type   | notes                                     |
| ------------------ | ------ | ----------------------------------------- |
| `id`               | string | Matches input.                            |
| `status`           | string | `"validated"` \| `"dismissed"`.           |
| `dismissal_reason` | string | Present only when `status = "dismissed"`. |

**Collateral findings** produced during Step 4 (per the collateral-change check) use the full **Finding object** schema above with `source_agent: "validation"` and `id: "val-N"`. They append to Step 5's input.

## Step 5 return (severity audit)

One entry per incoming finding, keyed by `id`:

| field              | type   | notes                                             |
| ------------------ | ------ | ------------------------------------------------- |
| `id`               | string | Matches input.                                    |
| `status`           | string | `"confirmed"` \| `"downgraded"` \| `"dismissed"`. |
| `final_severity`   | string | Severity value. Omit when `status = "dismissed"`. |
| `dismissal_reason` | string | Present only when `status = "dismissed"`.         |

## Orchestrator behavior

- Maintains a master finding map keyed by `id`.
- Each step's return merges into the master object by `id`.
- Original `severity`, `confidence`, `source_agent`, `title`, `detail`, `file`, `line` are set at creation and never rewritten.
- Step 6 partitions the master map by final status (validated vs dismissed) and renders the report.
