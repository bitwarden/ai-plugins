# The ablation-accretion recipe

Finds a skill's load-bearing core: the instructions that change behavior, as opposed to the ones that cost tokens and reassure the author.

## The idea

Skills accrete instructions, few are tested in isolation, so nobody knows which ones the model would have followed anyway. Run it in reverse:

1. **Ablate.** Strip the skill to a bare skeleton: the sequence of steps plus an output template. No explanations, no re-teaching what a capable model knows, no defensive padding. This is the treatment.
2. **Freeze the original as the control.** Never edit it.
3. **Run both** against real inputs, per the six-phase loop in `SKILL.md`.
4. **Accrete.** When a run reproduces a specific failure that a stripped directive would have prevented, add that directive back, terse. Bump the treatment version. Record it.

The output is a skill as small as the evidence allows, where every surviving instruction has a run attached proving it earned its place.

## The accretion rule

Add a directive back only when you have watched it fail without it. Not because it seems wise, not because the original had it, not because you can imagine a case. A promotion needs all three:

- A run where the treatment produced a wrong or worse result.
- A causal story: this specific missing directive caused this specific failure.
- Confirmation it is a skill property, not run noise. A single flipped run is not enough; reproduce it. Verdicts are noisy on the order of half the items.

Re-adding on intuition just rewrites the original with extra steps.

## Status vocabulary

Track every candidate directive in the ledger as one of:

- **withheld**: stripped, not yet shown to be needed. The default at v0.
- **added**: restored because a run demonstrated the failure it prevents.
- **dropped**: experiments show the treatment does fine without it.

## The trap: directives that interact

The most valuable thing this surfaces is not whether a single directive matters. It is that two individually-earned directives can combine into a loophole neither shows alone.

From the experiment this distills: one directive said "check both of these two repositories for coverage." Another said "if you did not inspect a surface, record it as unverified rather than asserting it has no tests." Each was earned honestly. Together they composed into an escape hatch, and the model satisfied "check both repos" by tagging the second `unverified` without looking at it.

The fix was not more emphasis. It was restructuring into an escalation ladder (inspect locally, else fetch directly, else ask, and only then fall back to unverified) plus a placement change so the decision happened while a human was still in the loop.

So after adding a directive, watch the next run for how it interacts with what is already there. Interactions are visible only by running, and this is the payoff that makes the manual work worth it.

## Attribution during accretion

Before touching the skill, ask what caused the difference:

- **Skill content**: a directive present or absent. The only cause that justifies an edit.
- **Model**: stronger or weaker. Use model-matched pairs to rule this out.
- **Run noise**: search-scope divergence. Reproduce before believing.
- **Run structure**: a run that delegated to a focused subagent looks deeper than one that worked inline, independent of skill content.

Change one thing per comparison.

## When to stop

Stop when the treatment meets or beats the control on the layers you care about, across several real inputs, and the remaining differences sit inside the measured noise floor. The treatment is then your recommended variant: smaller, cheaper, no worse, with a ledger documenting why each surviving instruction is there.
