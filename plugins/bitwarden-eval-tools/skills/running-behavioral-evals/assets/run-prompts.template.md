# Blinded run prompts

Paste one prompt per session. Run each in a **fresh, top-level session** (not a subagent). The two prompts are **identical except the skill name.** Do not add clarifiers, hints, or anything that names what you expect or worry about; how each variant handles the raw input is what is under test.

Fill in:

- `<TASK>`: the task, phrased about the work, not about the eval.
- `<INPUT>`: the real input (issue key, file path, PR).
- `<SKILL>`: the fully qualified skill name, the only field that differs between the two blocks.

---

## Session A - control variant (`<plugin>:<control-skill>`)

```
<TASK> for this input:
<INPUT>

Use the skill `<plugin>:<control-skill>` and follow it exactly. Invoke it via the Skill tool at the very start, passing the input above, then carry out its steps.

When finished, return two things:
1. The full work product you produced. Paste its markdown inline, and give the file path you wrote it to.
2. A terse, factual execution log: the ordered steps you took, every tool/skill/CLI call you made (name + purpose), and anything that blocked you or that you could not determine.

Proceed with sensible defaults; ask only if you genuinely need a decision from me. If an input or tool is unavailable, record that fact and proceed as far as you can. Report only facts about what you did and what you produced, with no meta-commentary about the task itself.
```

## Session B - treatment variant (`<plugin>:<treatment-skill>`)

```
<TASK> for this input:
<INPUT>

Use the skill `<plugin>:<treatment-skill>` and follow it exactly. Invoke it via the Skill tool at the very start, passing the input above, then carry out its steps.

When finished, return two things:
1. The full work product you produced. Paste its markdown inline, and give the file path you wrote it to.
2. A terse, factual execution log: the ordered steps you took, every tool/skill/CLI call you made (name + purpose), and anything that blocked you or that you could not determine.

Proceed with sensible defaults; ask only if you genuinely need a decision from me. If an input or tool is unavailable, record that fact and proceed as far as you can. Report only facts about what you did and what you produced, with no meta-commentary about the task itself.
```
