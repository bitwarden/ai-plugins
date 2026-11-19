---
name: standard-review
description: Abacus review slot (standard depth) for Bitwarden. Runs the bitwarden-code-review reviewer once on a bead's uncommitted change and writes its review files into the folder Abacus names. Used by Abacus's review stage, not invoked by people directly.
user-invocable: false
context: fork
agent: bitwarden-code-review:bitwarden-code-reviewer
arguments: [base, output_dir]
---

OUTPUT: local files
BASE: $base
OUTPUT_DIR: $output_dir

Review the uncommitted changes in this working tree. This is an unattended run: never ask questions and never post to GitHub.
