# Test results JSON contract

The `test-runner` emits run results as JSON. The orchestrator assembles segments into the canonical `test-results-<timestamp>.json` with `merge_results.py` and renders it with `render_report.py`. Concrete examples live in `examples/`; they are the producer's reference and the scripts' golden test fixtures.

## Run object

| Field             | Type   | Notes                                                                                         |
| ----------------- | ------ | --------------------------------------------------------------------------------------------- |
| `run_status`      | string | `complete`, `paused` (segment only), or `aborted`                                             |
| `abort_reason`    | string | Present only when `run_status` is `aborted`                                                   |
| `need_user_input` | string | Present only on a `paused` segment; the resume question                                       |
| `totals`          | object | `{ total, passed, adaptive, failed, errored }`; derived on merge                              |
| `cases`           | array  | Case objects, in order; empty for an aborted run only if it aborted before any case completed |

Totals are derived from the per-case `status` values by `merge_results.py`. The runner does not emit totals. `total = passed + adaptive + failed + errored` and `len(cases) == total` hold by construction.

An `aborted` run MAY carry `cases` and `totals` alongside `abort_reason`. Any abort that lands after at least one test case completed takes this shape, and two paths reach it. A run may have split into segments at a `[HUMAN]` pause with a later segment aborting, most often because the resumed runner could not re-authenticate. Or a single-segment run may have hit an environment fault partway through, such as Mailcatcher becoming unreachable between cases, in which case the aborting segment carries its own completed cases. Either way the completed cases are preserved by `merge_results.py` and the report renders them under an abort banner. An `aborted` run with an empty or absent `cases` array means the run aborted before any test case completed, that is, setup or authentication failed, and no report is produced.

## Case object

| Field         | Type   | Notes                                                                 |
| ------------- | ------ | --------------------------------------------------------------------- |
| `number`      | int    | 1-based                                                               |
| `name`        | string |                                                                       |
| `status`      | string | `PASS`, `PASS (adaptive)`, `FAIL`, or `ERROR`                         |
| `url`         | string | Optional; the page under test                                         |
| `setup_steps` | array  | Step objects; omit or use `[]` when there are none                    |
| `test_steps`  | array  | Step objects                                                          |
| `notes`       | string | Optional                                                              |
| `adaptive`    | object | `{ specified, found }`; present only when status is `PASS (adaptive)` |

## Step object

| Field        | Type   | Notes                                                              |
| ------------ | ------ | ------------------------------------------------------------------ |
| `text`       | string | Step description                                                   |
| `outcome`    | string | `PASS`, `FAIL`, or `COMPLETED (User: <answer>)` for a human step   |
| `observed`   | string | Optional; what was actually observed on an assertion step          |
| `screenshot` | string | Optional; bare filename, rendered relative as `screenshots/<name>` |
| `human`      | bool   | Optional; `true` for a `[HUMAN]` step                              |

## Invariants enforced in code

- `run_status` is a known value.
- Every case `status` is a known enum value.
- Derived totals are internally consistent and `len(cases) == total`.
- Malformed JSON, a missing required field, or an unknown enum is a loud, non-zero-exit failure naming the offending field or case.
