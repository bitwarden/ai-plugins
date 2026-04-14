---
name: validating-codebase-references
description: Use when verifying that file paths, classes, methods, patterns, or namespaces referenced in a technical document actually exist in the codebase. Performs systematic anti-hallucination checks. Apply when reviewing plans, generated code references, or any technical content that names specific codebase elements.
---

# Validating Codebase References

A systematic process for confirming that every concrete reference in a technical document maps to real code. Apply this to each reference extracted from the document under review.

<thinking>
Before running any verification steps, enumerate all instances of each reference type you'll find in steps 1–5 below. Categorize every reference in the document before checking any of them — this prevents partial verification where some categories get missed.
</thinking>

## Verification Steps

1. **File existence** — Use `Glob` to confirm each referenced file path resolves to a real file. If the path doesn't match exactly, try variations (different casing, adjacent directories).

2. **Class/interface definitions** — Use `Grep` to search for `class <Name>`, `interface <Name>`, or equivalent in the expected location. Confirm the type is defined where the document claims it is.

3. **Method/property existence** — Use `Grep` to confirm methods the document says to call, override, or extend are present on the referenced type. Check the exact method signature if possible.

4. **Pattern verification** — For each "follow the pattern of X" claim, `Read` the referenced example file and verify the described approach actually matches what is in that file. Do not assume the description is accurate.

5. **Namespace/import accuracy** — Verify namespaces, module paths, and package names match the actual codebase. Check adjacent files, `package.json`, or `.csproj` as appropriate to confirm the correct import path.

<thinking>
Before assigning severity to a mismatch, reason through its actual impact:
- Will this cause a compilation or build failure? → Critical
- Will this cause a runtime error or subtle bug that's hard to detect? → High
- Is this an inaccuracy that won't break anything but will mislead? → Medium
Resist defaulting to Critical for everything — reserve it for mismatches that will cause the implementation to fail outright.
</thinking>

## Recording Mismatches

For each mismatch found, record:
- **What the document claims** — the specific reference as written
- **What actually exists** — what is in the codebase, or that it does not exist at all
- **Correct name or path** — the actual correct name/path if determinable from the codebase
- **Severity**:
  - **Critical** — coding agent will fail or produce broken code if this is wrong
  - **High** — likely to cause agent confusion or a subtle bug
  - **Medium** — minor inaccuracy that won't break compilation but may mislead

## Verification Principles

- Be specific: name the exact file, stage, class, or method where each issue lives.
- When a hallucination is found, search the codebase for the correct API before reporting — provide the actual correct name, not just "update the reference."
- Only flag issues that would cause an implementation problem. Do not flag style preferences.
- If the document is ambiguous, look at the actual code to resolve the ambiguity, then recommend the specific concrete answer.
