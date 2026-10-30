import { z } from "zod";
import { CodeSourceError, CODE_BRANCH, CODE_REPO } from "../github/archive.js";
import { loadCodeIndex, type ToolContext } from "../context.js";
import type { CodeHit } from "../code/scan.js";
import { parseInput, type ToolDefinition } from "./types.js";

const FindAutomatedCasesSchema = z.object({
  caseIds: z.array(z.number().int().positive()).min(1).max(50),
});

function hitLine(hit: CodeHit): string {
  return (
    `  - ${hit.path}:${hit.line} [${hit.attribute}] ` +
    `platform ${hit.platform ?? "unknown"}, ` +
    `ignored ${hit.ignored ? "yes" : "no"}, ` +
    `KnownBug ${hit.knownBug ? "yes" : "no"}`
  );
}

async function handler(input: unknown, ctx: ToolContext): Promise<string> {
  const args = parseInput(FindAutomatedCasesSchema, input);

  let index;
  try {
    index = await loadCodeIndex(ctx);
  } catch (error) {
    const reason =
      error instanceof CodeSourceError
        ? error.message
        : "the code source failed for an unexpected reason";
    return (
      `Code not checked: ${reason}. List these cases as not checked for code: ` +
      args.caseIds.join(", ")
    );
  }

  const read = new Date(ctx.now()).toISOString();
  const header = [
    `Source: ${CODE_REPO}, ${CODE_BRANCH} at ${index.sha} (read ${read}).`,
    `Scanned ${index.filesScanned} .cs files under *.Tests folders. ProdSmoke is excluded on purpose.`,
    'Matches are exact: [Description("N")], each [Covers(N)] argument, and .SetDescription("N"), where N is the whole value. ' +
      "Ignored and KnownBug are read from the attributes near each match.",
  ];

  const body = args.caseIds.map((id) => {
    const hits = index.hits.get(id) ?? [];
    if (hits.length === 0) {
      return `${id}: not found`;
    }
    return [
      `${id}: found, ${hits.length} match(es)`,
      ...hits.map(hitLine),
    ].join("\n");
  });

  return [header.join("\n"), body.join("\n")].join("\n\n");
}

const findAutomatedCases: ToolDefinition = {
  name: "find_automated_cases",
  description:
    "Finds which Testmo case IDs are automated in the bitwarden/test repository on its main branch. " +
    "Takes the case IDs from the caller and never calls Testmo. " +
    "Reads GitHub through the user's gh login and never uses a local clone. For each ID it reports " +
    "found or not found, and for each match the file, line, attribute, platform, and whether the test is ignored or has a KnownBug. " +
    "If GitHub cannot be read, the result starts with 'Code not checked' and gives the reason. Read-only.",
  inputSchema: {
    type: "object",
    properties: {
      caseIds: {
        type: "array",
        items: { type: "integer" },
        minItems: 1,
        maxItems: 50,
        description: "Testmo case IDs to look for in the test code.",
      },
    },
    required: ["caseIds"],
  },
  handler,
};

export default findAutomatedCases;
