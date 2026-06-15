# Merge Walkthrough

Condensed from a real run. Traces three findings through the Step 6 merge, including the trickiest path: a collateral finding created at Step 4 and dismissed at Step 5.

Steps 2/3 produced two findings: `arch-1` (important, confidence 90, architect) and `quality-3` (refactor, confidence 90, quality).

## After the Step 4 merge

Step 4's return is [`step4-validation-return.json`](step4-validation-return.json). It dismisses `quality-3` as a duplicate and emits one collateral finding, `val-1`, as a full Finding object in the same array. The orchestrator inserts `val-1` into the master map — its creation-time fields come from that Finding object — and it joins Step 5's input. `quality-3` gets `dismissal_stage: "Step 4 validation"`.

| id        | severity  | status    | dismissal_stage     | goes to Step 5? |
| --------- | --------- | --------- | ------------------- | --------------- |
| arch-1    | important | validated | —                   | yes             |
| quality-3 | refactor  | dismissed | "Step 4 validation" | no              |
| val-1     | refactor  | —         | —                   | yes             |

## After the Step 5 merge

Step 5's return is [`step5-severity-audit-return.json`](step5-severity-audit-return.json). It confirms `arch-1` and dismisses `val-1`, which gets `dismissal_stage: "Step 5 severity audit"`. Creation-time fields are untouched throughout.

| id        | severity  | final status | dismissal_stage         | renders in      |
| --------- | --------- | ------------ | ----------------------- | --------------- |
| arch-1    | important | confirmed    | —                       | Findings        |
| quality-3 | refactor  | dismissed    | "Step 4 validation"     | Dismissed block |
| val-1     | refactor  | dismissed    | "Step 5 severity audit" | Dismissed block |
