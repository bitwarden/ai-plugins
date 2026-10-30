/**
 * Finds Testmo case IDs in test source. Matching rules, all exact:
 *   - [Description("N")]: the string must be exactly the case ID.
 *   - [Covers("N", "M")]: each argument, trimmed and with one pair of
 *     surrounding double quotes removed, must be exactly the case ID. A
 *     quoted argument may hold a list, as in [Covers("N, M")], and each ID in
 *     it is matched on its own. Bare [Covers(N, M)] is read the same way.
 *   - .SetDescription("N"): the string must be exactly the case ID.
 * "Login 2" is not case 2, and "9891533 and 9891534" is not a match.
 * Only .cs files under a top-level *.Tests folder are scanned, except the
 * ProdSmoke folder, which reuses functional IDs on purpose.
 */

export type CodeAttribute = "Description" | "Covers" | "SetDescription";

export interface CodeHit {
  id: number;
  /** Repository-relative path, forward slashes. */
  path: string;
  /** 1-based line of the attribute or call. */
  line: number;
  attribute: CodeAttribute;
  /** Platform from the folder names, or null when the path does not say. */
  platform: string | null;
  /** True when [Ignore] sits on the test method or its class. */
  ignored: boolean;
  /** True when [KnownBug(...)] sits on the test method. */
  knownBug: boolean;
}

// The lookbehind keeps .SetDescription("N") from also matching as a Description.
const DESCRIPTION = /(?<!Set)Description\("([^"]+)"\)/g;
const COVERS = /Covers\(([^)]+)\)/g;
// One Covers argument: a quoted string, which may hold commas, or bare text up
// to the next comma. An unbalanced quote falls to the bare form and keeps its
// quote, so it is not read as an ID.
const COVERS_ARGUMENT = /\s*"[^"]*"|[^,]+/g;
const SET_DESCRIPTION = /\.SetDescription\("(\d+)"\)/g;
const TEST_METHOD =
  /(?:public|private|protected|internal)\s+(?:void|Task|async\s+Task)\s+\w+\s*\(/;
const CLASS_DECLARATION = /\bclass\s+\w+/;
// An attribute name after "[" or ",", so [Test, Ignore("x")] counts and
// [IgnoreOnSimulator(...)] or a call such as Assert.Ignore(...) does not.
const IGNORE_ATTRIBUTE = /[[,]\s*Ignore\s*[(\],]/;
const KNOWN_BUG_ATTRIBUTE = /[[,]\s*KnownBug\s*[(\],]/;

/** Lines searched after an attribute for the test method it belongs to. */
const METHOD_LOOKAHEAD_LINES = 10;
/** Lines searched above a class declaration for a class-level [Ignore]. */
const CLASS_LOOKBEHIND_LINES = 5;

const PLATFORM_RULES: ReadonlyArray<{ patterns: string[]; platform: string }> =
  [
    {
      patterns: ["Android.Tests", "Authenticator"],
      platform: "Authenticator - Android",
    },
    {
      patterns: ["iOS.Tests", "Authenticator"],
      platform: "Authenticator - iOS",
    },
    { patterns: ["Mobile", "Authenticator"], platform: "Authenticator" },
    { patterns: ["Android.Tests"], platform: "Android" },
    { patterns: ["iOS.Tests"], platform: "iOS" },
    { patterns: ["Web.Tests"], platform: "Web" },
    { patterns: ["Extension.Tests"], platform: "Extension" },
    { patterns: ["Desktop.Tests"], platform: "Desktop" },
    { patterns: ["CommandLine.Tests"], platform: "CLI" },
    { patterns: ["Passwordless.Tests"], platform: "Passwordless" },
    { patterns: ["Authenticator.Tests"], platform: "Authenticator" },
    { patterns: ["API.Tests"], platform: "API" },
  ];

/** Platform from the path, using the first rule whose folder names all appear. */
export function detectPlatform(path: string): string | null {
  const rule = PLATFORM_RULES.find(({ patterns }) =>
    patterns.every((pattern) => path.includes(pattern)),
  );
  return rule?.platform ?? null;
}

/** True for .cs files that the code check reads. */
export function isScannedPath(path: string): boolean {
  const segments = path.split("/");
  if (segments.length < 2) {
    return false;
  }
  if (!segments[0].includes(".Tests")) {
    return false;
  }
  if (!path.endsWith(".cs") || path.endsWith("TestBase.cs")) {
    return false;
  }
  return !segments.includes("ProdSmoke");
}

/** The case ID when the whole text is digits, otherwise no ID. */
function exactId(text: string): number[] {
  return /^\d+$/.test(text) ? [Number(text)] : [];
}

/** Each Covers argument, or each entry in a quoted list, as its own exact ID. */
function coversIds(text: string): number[] {
  return [...text.matchAll(COVERS_ARGUMENT)].flatMap(([match]) => {
    const argument = match.trim();
    const quoted = /^"(.*)"$/.exec(argument);
    if (!quoted) {
      return exactId(argument);
    }
    return quoted[1].split(",").flatMap((entry) => exactId(entry.trim()));
  });
}

/**
 * Ignore and KnownBug on the test method. C# allows attributes in any order,
 * so the scan starts at the top of the attribute block that holds `index`
 * (the contiguous lines above it that start with "[") and reads down to the
 * method signature.
 */
function methodAttributes(
  lines: string[],
  index: number,
): { ignored: boolean; knownBug: boolean } {
  let start = index;
  while (start > 0 && lines[start - 1].trim().startsWith("[")) {
    start--;
  }
  const end = Math.min(lines.length, index + METHOD_LOOKAHEAD_LINES);
  let ignored = false;
  let knownBug = false;
  for (let i = start; i < end; i++) {
    ignored ||= IGNORE_ATTRIBUTE.test(lines[i]);
    knownBug ||= KNOWN_BUG_ATTRIBUTE.test(lines[i]);
    if (TEST_METHOD.test(lines[i])) {
      break;
    }
  }
  return { ignored, knownBug };
}

/** True when the nearest class declaration above `index` carries [Ignore]. */
function classIgnored(lines: string[], index: number): boolean {
  for (let i = index; i >= 0; i--) {
    if (CLASS_DECLARATION.test(lines[i])) {
      const start = Math.max(0, i - CLASS_LOOKBEHIND_LINES);
      return lines.slice(start, i).some((line) => IGNORE_ATTRIBUTE.test(line));
    }
  }
  return false;
}

/** Every Testmo case ID the file names, with where it appears. */
export function scanFile(path: string, text: string): CodeHit[] {
  const lines = text.split(/\r?\n/);
  const platform = detectPlatform(path);
  const hits: CodeHit[] = [];

  lines.forEach((line, index) => {
    const found: Array<{ ids: number[]; attribute: CodeAttribute }> = [];
    for (const match of line.matchAll(DESCRIPTION)) {
      found.push({ ids: exactId(match[1]), attribute: "Description" });
    }
    for (const match of line.matchAll(COVERS)) {
      found.push({ ids: coversIds(match[1]), attribute: "Covers" });
    }
    for (const match of line.matchAll(SET_DESCRIPTION)) {
      found.push({ ids: exactId(match[1]), attribute: "SetDescription" });
    }

    for (const { ids, attribute } of found) {
      // A SetDescription call sits inside a TestCaseSource, so it has no method
      // line to stop at. Its ignore state is read from the lines around it.
      const attributes =
        attribute === "SetDescription"
          ? nearbyAttributes(lines, index)
          : methodAttributes(lines, index);
      const ignored = attributes.ignored || classIgnored(lines, index);
      for (const id of ids) {
        hits.push({
          id,
          path,
          line: index + 1,
          attribute,
          platform,
          ignored,
          knownBug: attributes.knownBug,
        });
      }
    }
  });

  return hits;
}

function nearbyAttributes(
  lines: string[],
  index: number,
): { ignored: boolean; knownBug: boolean } {
  const start = Math.max(0, index - METHOD_LOOKAHEAD_LINES);
  const end = Math.min(lines.length, index + METHOD_LOOKAHEAD_LINES);
  const window = lines.slice(start, end);
  return {
    ignored: window.some((line) => IGNORE_ATTRIBUTE.test(line)),
    knownBug: window.some((line) => KNOWN_BUG_ATTRIBUTE.test(line)),
  };
}
