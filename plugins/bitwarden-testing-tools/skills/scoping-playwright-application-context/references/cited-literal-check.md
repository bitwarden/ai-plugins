# Cited-literal check

Run this check on every catalog entry `scoping-playwright-application-context` copies, before copying it. Citations use the form the skill defines: `` `<workspace path>` (`<literal>`, …) ``.

For each citation on the entry (a state's `Source:` lines, a flow's `**Sources:**` bullets):

1. Read the whole cited file, paging through it with `offset` when Read truncates it, and search it for each literal as plain text, in order where the citation ends `in order`. If you use Grep instead, escape every regex metacharacter in the literal first (`\ . ^ $ * + ? ( ) [ ] { } |`).
2. If the cited file does not exist, Glob for its file name. If it moved, check the literals there and treat the move as drift. If it is gone, stop and emit the plain failure report naming the slug and the citation.
3. If every literal matches, copy the entry.
4. If a literal is missing, find what the source shows the fact to be now:
   - If the fact still holds, copy the entry unchanged.
   - If it changed, correct the fact in your copy (an enum value, a step's order, a label), including any copied `Source:` line that cites it.
   - Either way, add a `## Notes` bullet recording the drift: the slug, the citation, and what the source shows now — the fact unchanged, or the fact as the catalog stated it and the corrected fact.
   - If the source does not establish the fact, stop and emit the plain failure report naming the slug and the citation.
