# Commit and Pull Request Flows

The commit and pull request skills compose one another, so a change to one skill's contract can ripple into every skill that calls it. These diagrams show those seams: which skill owns each decision, and where control passes between skills.

The `SKILL.md` files are authoritative. Where a diagram and a skill disagree, the skill wins and the diagram needs updating.

## Deciding whether the disclosure policy applies

`committing-changes`, `applying-pr-conventions`, and `force-multiplier` all branch on the verdict `applying-security-disclosure-policy` returns. Most changes leave at the first `No` without a Confluence fetch. A security-relevant change gets rules only from the fetched policy page, and anything short of usable rules is a `Stop`.

```mermaid
graph TD
    start[Verdict requested for one change]
    ticket{Ticket key in the branch<br/>or conversation?}
    lookup[get_issue]
    lookupOk{Lookup succeeded?}
    high{VULN link, VULN-* branch,<br/>Vulnerability-Resolution label,<br/>or the author said so?}
    heuristic{A fix touching auth, sessions,<br/>crypto, input validation,<br/>access control, or secrets?}
    lookupFailed{VULN-* branch, or<br/>the author said so?}
    ask[Ask the author once:<br/>does the policy apply?]
    answer{Author says yes?}
    no[Verdict: No<br/>no fetch]
    fetch[get_confluence_page<br/>for the policy page]
    fetched{Page fetched with a body?}
    usable{Usable wording rules<br/>for commits and PRs?}
    yes[Verdict: Yes<br/>signal and wording rules]
    stop[Verdict: Stop<br/>reason and remedy]

    start --> ticket
    ticket -->|yes, plugin installed| lookup
    ticket -->|no, or plugin missing| high
    lookup --> lookupOk
    lookupOk -->|yes| high
    lookupOk -->|no| lookupFailed
    lookupFailed -->|yes| fetch
    lookupFailed -->|no| ask
    high -->|yes| fetch
    high -->|no| heuristic
    heuristic -->|yes| ask
    heuristic -->|no| no
    ask --> answer
    answer -->|yes| fetch
    answer -->|no| no
    fetch --> fetched
    fetched -->|no| stop
    fetched -->|yes| usable
    usable -->|no| stop
    usable -->|yes| yes
```

> _**Perspective:** For maintainers of the delivery skills, showing how `applying-security-disclosure-policy` reaches one of its three verdicts for a single change. Inside the one skill. Omits how callers act on each verdict, which the flows below show._

## Committing a change

The branch check runs before anything is staged, so work never lands on the default branch by accident. The disclosure check runs before any message is written, because a commit message can't be reworded once it's pushed. It is skipped when the caller passes a verdict it already settled, as `force-multiplier` does after its pilot. Only the first commit on a branch needs the full message format; followups can be a short summary.

```mermaid
graph TD
    start[Commit requested]
    onDefault{On the repo's default branch?}
    newBranch[Ask for a branch name,<br/>offer a suggestion, switch]
    preflight[perform-preflight]
    blocked[Flag the failure to the user]
    disclosure{Security fix?<br/>applying-security-disclosure-policy}
    rules[Draft against the policy's wording rules,<br/>author approves the message]
    policyStop[Stop: policy unavailable or unusable,<br/>no message written]
    first{First commit on the branch?}
    typeKeyword[labeling-changes:<br/>type keyword and t: label]
    full[Ticket prefix, type keyword,<br/>imperative summary, why body]
    short[Short descriptive summary]
    done[Commit]

    start --> onDefault
    onDefault -->|yes| newBranch
    onDefault -->|no| preflight
    newBranch --> preflight
    preflight -->|pass| disclosure
    disclosure -->|No| first
    disclosure -->|Yes| rules
    disclosure -->|Stop| policyStop
    rules --> first
    preflight -->|unresolved failure| blocked
    first -->|yes| typeKeyword
    typeKeyword --> full
    first -->|no| short
    full --> done
    short --> done
```

## Opening a pull request

Preflight settles before the review because fixing a preflight failure can change the diff the review needs to see. The submission preview is the single point where every decision is visible together, and nothing is pushed until the user confirms it. Editing the label from the preview re-asks only the label, since re-entering `applying-pr-conventions` would recompose the title and body and discard an edit already made.

The security-fix decision comes before any title or body exists: `applying-pr-conventions` calls `applying-security-disclosure-policy` first, and its verdict decides how the strings are composed. On a security fix, the push publishes the branch's commits as well as the PR title, so the commits not yet on the remote are checked against the same wording rules before the preview. Commits already pushed are out of scope: this is a check before the push, and they're already public.

```mermaid
graph TD
    start[PR requested]
    preflightDone{Preflight passed?}
    runPreflight[Run perform-preflight]
    preflightFailed[Stop and report the failure]
    depth{How deep is the change?}
    standard[code-review-local]
    substantial[performing-multi-agent-code-review]
    assess[Assess findings with the user:<br/>fix each, or record it as deferred]
    clean[Remove untracked review output]
    disclosure{Security fix?<br/>applying-security-disclosure-policy}
    conventions[applying-pr-conventions:<br/>title with its type from labeling-changes,<br/>body, ai-review label]
    secureConventions[applying-pr-conventions under the wording rules:<br/>no VULN-* key anywhere,<br/>No label recommended for AI review]
    policyStop[Stop: policy unavailable or unusable,<br/>nothing composed or pushed]
    commitCheck{Fetch the branch, then: does any commit<br/>not yet pushed break the wording rules?}
    whichCommit{Is it HEAD?}
    amend[Reword with git commit --amend -F]
    handBack[Hand back to the author,<br/>stop before the preview]
    offer{Author accepts<br/>the reword?}
    preview[Submission preview<br/>on a security fix, shows the verdict<br/>and the commits to be pushed]
    confirm{Submit as previewed?}
    edit[Apply the edit]
    relabel[Re-ask the label only]
    cancel[Stop, nothing pushed]
    push[git push, then gh pr create --draft<br/>with title and body passed via files]
    url[Report the PR URL]

    start --> preflightDone
    preflightDone -->|yes| depth
    preflightDone -->|no| runPreflight
    runPreflight -->|passes| depth
    runPreflight -->|cannot pass| preflightFailed
    depth -->|Standard| standard
    depth -->|Substantial| substantial
    standard --> assess
    substantial --> assess
    assess --> clean
    clean --> disclosure
    disclosure -->|No| conventions
    disclosure -->|Yes| secureConventions
    disclosure -->|Stop| policyStop
    conventions --> preview
    secureConventions --> commitCheck
    commitCheck -->|no| preview
    commitCheck -->|yes| whichCommit
    whichCommit -->|yes| offer
    offer -->|yes| amend
    offer -->|no| handBack
    whichCommit -->|no, older commit| handBack
    commitCheck -->|commit range can't be resolved| handBack
    amend --> preview
    preview --> confirm
    confirm -->|Submit as shown| push
    confirm -->|Edit title or body| edit
    confirm -->|Change ai-review label| relabel
    confirm -->|Cancel| cancel
    edit --> preview
    relabel --> preview
    push --> url
```

## Fanning a change across many targets

`force-multiplier` reuses the same skills across a fleet but cannot answer the conventions or disclosure questions once per target, so it resolves them once at the pilot and locks the result. On a security fix the author approves the pilot's wording once, and a `Stop` ends the campaign before the pilot commits anything. Every fan-out target then runs preflight and commits non-interactively against that locked title, body, label, and security verdict.

```mermaid
graph TD
    pilot[Pilot target]
    disclosure{applying-security-disclosure-policy, once:<br/>security-relevant?}
    policyStop[Stop: no pilot commit or PR,<br/>no fan-out]
    conventions[applying-pr-conventions, once:<br/>lock title, body, label, and verdict]
    confirm{User confirms the pilot, its wording<br/>on a security fix, and the total fan-out?}
    stop[Stop]
    target[Each fan-out target]
    applicable{Signal present and<br/>not already compliant?}
    skipped[Record skipped or<br/>already-compliant]
    apply[Branch and apply the recipe]
    preflight[perform-preflight]
    failed[Record failed, no commit]
    commit[committing-changes<br/>with the locked title and verdict]
    draft[Push and open a draft PR<br/>with the locked conventions]
    report[Report every target]

    pilot --> disclosure
    disclosure -->|No or Yes| conventions
    disclosure -->|Stop| policyStop
    conventions --> confirm
    confirm -->|no| stop
    confirm -->|yes| target
    target --> applicable
    applicable -->|no| skipped
    applicable -->|yes| apply
    apply --> preflight
    preflight -->|fail| failed
    preflight -->|pass| commit
    commit --> draft
    draft --> report
    skipped --> report
    failed --> report
```
