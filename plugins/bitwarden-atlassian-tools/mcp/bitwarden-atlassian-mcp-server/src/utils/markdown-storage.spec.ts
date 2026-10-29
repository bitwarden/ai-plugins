import { describe, it, expect } from "vitest";

import { markdownToStorage } from "./markdown-storage.js";

const convert = (markdown: string) => markdownToStorage(markdown).storage;

/**
 * Throw unless `xml` is well-formed: every tag closed in order, CDATA closed,
 * and every `&` starting a known entity. Storage format is XHTML, and
 * Confluence rejects a body that is not.
 */
function assertWellFormed(xml: string): void {
  const stack: string[] = [];
  const pattern =
    /<!\[CDATA\[[\s\S]*?\]\]>|<(\/?)([\w:-]+)((?:\s+[\w:-]+="[^"<]*")*)\s*(\/?)>|<|&(?!(?:amp|lt|gt|quot|#\d+);)/g;
  let match: RegExpExecArray | null;

  while ((match = pattern.exec(xml)) !== null) {
    const [token, closing, name, , selfClosing] = token_(match);
    if (token.startsWith("<![CDATA[")) continue;
    if (name === undefined) {
      throw new Error(
        `Stray "${token}" at ${match.index}: ${xml.slice(match.index, match.index + 40)}`,
      );
    }
    if (selfClosing) continue;
    if (closing) {
      const open = stack.pop();
      if (open !== name) throw new Error(`</${name}> closes <${open}>`);
    } else {
      stack.push(name);
    }
  }
  if (stack.length > 0) throw new Error(`Unclosed: ${stack.join(", ")}`);

  function token_(m: RegExpExecArray) {
    return [m[0], m[1], m[2], m[3], m[4]] as const;
  }
}

describe("markdownToStorage blocks", () => {
  it("converts headings and paragraphs, joining soft-wrapped lines", () => {
    expect(convert("# Title\n\nFirst line\nsecond line.\n\n### Sub")).toBe(
      "<h1>Title</h1>\n<p>First line second line.</p>\n<h3>Sub</h3>",
    );
  });

  it("turns a trailing double space or backslash into a hard break", () => {
    expect(convert("one  \ntwo\\\nthree")).toBe(
      "<p>one<br />two<br />three</p>",
    );
  });

  it("does not treat #word as a heading", () => {
    expect(convert("#hashtag")).toBe("<p>#hashtag</p>");
  });

  it("converts a tight bulleted list without paragraph wrappers", () => {
    expect(convert("- one\n- two\n* three")).toBe(
      "<ul><li>one</li><li>two</li><li>three</li></ul>",
    );
  });

  it("wraps items of a loose list in paragraphs", () => {
    expect(convert("- one\n\n- two")).toBe(
      "<ul><li><p>one</p></li><li><p>two</p></li></ul>",
    );
  });

  it("nests a bulleted list under a numbered item", () => {
    expect(convert("1. first\n   - a\n   - b\n2. second")).toBe(
      "<ol><li>first\n<ul><li>a</li><li>b</li></ul></li><li>second</li></ol>",
    );
  });

  it("keeps wrapped continuation lines inside their list item", () => {
    expect(
      convert(
        "- **Bold start.** text that\n  wraps onto a second line\n- next",
      ),
    ).toBe(
      "<ul><li><strong>Bold start.</strong> text that wraps onto a second line</li><li>next</li></ul>",
    );
  });

  it("lets a list start straight after a paragraph line", () => {
    expect(convert("Two parts:\n- one\n- two")).toBe(
      "<p>Two parts:</p>\n<ul><li>one</li><li>two</li></ul>",
    );
  });

  it("does not start a list from a wrapped line beginning with a number", () => {
    expect(convert("Ship it before\n2027. Then stop.")).toBe(
      "<p>Ship it before 2027. Then stop.</p>",
    );
  });

  it("ends a list at a heading that follows without a blank line", () => {
    expect(convert("- one\n## Next")).toBe(
      "<ul><li>one</li></ul>\n<h2>Next</h2>",
    );
  });

  it("converts a GFM table, padding short rows and unescaping pipes", () => {
    expect(
      convert("| A | B |\n| --- | :-: |\n| `x` | a \\| b |\n| only |"),
    ).toBe(
      "<table><tbody><tr><th>A</th><th>B</th></tr>" +
        "<tr><td><code>x</code></td><td>a | b</td></tr>" +
        "<tr><td>only</td><td></td></tr></tbody></table>",
    );
  });

  it("keeps a table indented inside a list item", () => {
    const out = convert(
      "- Intro:\n\n  | A | B |\n  | --- | --- |\n  | 1 | 2 |\n\n- After",
    );
    expect(out).toBe(
      "<ul><li><p>Intro:</p>\n<table><tbody><tr><th>A</th><th>B</th></tr>" +
        "<tr><td>1</td><td>2</td></tr></tbody></table></li><li><p>After</p></li></ul>",
    );
  });

  it("converts a fenced code block to a code macro with its language", () => {
    expect(convert("```bash\necho <hi> & bye\n```")).toBe(
      '<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">bash</ac:parameter>' +
        "<ac:plain-text-body><![CDATA[echo <hi> & bye]]></ac:plain-text-body></ac:structured-macro>",
    );
  });

  it("splits a CDATA terminator inside code so the section stays closed", () => {
    const out = convert("~~~\na]]>b\n~~~");
    expect(out).toContain("<![CDATA[a]]]]><![CDATA[>b]]>");
    assertWellFormed(out);
  });

  it("does not format markdown inside a code block", () => {
    expect(convert("```\n**not bold**\n```")).toContain(
      "<![CDATA[**not bold**]]>",
    );
  });

  it("converts block quotes and horizontal rules", () => {
    expect(convert("> quoted\n> text\n\n---")).toBe(
      "<blockquote><p>quoted text</p></blockquote>\n<hr />",
    );
  });

  it("returns an empty body for blank input", () => {
    expect(convert("\n  \n")).toBe("");
  });
});

describe("markdownToStorage inline", () => {
  it("converts bold, italic, strikethrough, and code", () => {
    expect(convert("**b** __b__ *i* _i_ ~~s~~ `c`")).toBe(
      "<p><strong>b</strong> <strong>b</strong> <em>i</em> <em>i</em> " +
        '<span style="text-decoration: line-through;">s</span> <code>c</code></p>',
    );
  });

  it("leaves underscores inside words and spaced asterisks alone", () => {
    expect(convert("snake_case_name and 2 * 3 * 4")).toBe(
      "<p>snake_case_name and 2 * 3 * 4</p>",
    );
  });

  it("does not format inside code spans", () => {
    expect(convert("`**x** <b>`")).toBe("<p><code>**x** &lt;b&gt;</code></p>");
  });

  it("honours backslash escapes", () => {
    expect(convert("\\*not italic\\*")).toBe("<p>*not italic*</p>");
  });

  it("escapes raw HTML rather than passing it through", () => {
    expect(convert('<script>alert("x")</script> & more')).toBe(
      "<p>&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt; &amp; more</p>",
    );
  });

  it("keeps absolute links, with formatting inside the link text", () => {
    expect(
      convert(
        "**[SHOT-331](https://example.atlassian.net/browse/SHOT-331): reload**",
      ),
    ).toBe(
      '<p><strong><a href="https://example.atlassian.net/browse/SHOT-331">SHOT-331</a>: reload</strong></p>',
    );
  });

  it("escapes an ampersand in a link URL", () => {
    expect(convert("[q](https://x.test/?a=1&b=2)")).toBe(
      '<p><a href="https://x.test/?a=1&amp;b=2">q</a></p>',
    );
  });

  it("links bare and angle-bracket URLs", () => {
    expect(convert("See https://x.test/a. Or <mailto:me@x.test>")).toBe(
      '<p>See <a href="https://x.test/a">https://x.test/a</a>. ' +
        'Or <a href="mailto:me@x.test">mailto:me@x.test</a></p>',
    );
  });

  it("renders relative and non-http links as text, with a warning", () => {
    const result = markdownToStorage(
      "[README](README.md) and [x](javascript:alert(1))",
    );

    expect(result.storage).toBe("<p>README and x</p>");
    expect(result.warnings).toHaveLength(2);
    expect(result.warnings[0]).toContain('Link "README" (README.md)');
  });

  it("converts an absolute image and reports a relative one", () => {
    const result = markdownToStorage(
      "![logo](https://x.test/l.png) ![local](l.png)",
    );

    expect(result.storage).toBe(
      '<p><ac:image ac:alt="logo"><ri:url ri:value="https://x.test/l.png" /></ac:image> local</p>',
    );
    expect(result.warnings).toEqual([
      expect.stringContaining('Image "local" (l.png)'),
    ]);
  });

  it("reports each dropped link once", () => {
    const result = markdownToStorage("[a](a.md) [a](a.md)");
    expect(result.warnings).toHaveLength(1);
  });

  it("drops control characters XML cannot carry", () => {
    expect(convert("a\u0000b\u0001c\u001Fd")).toBe("<p>abcd</p>");
  });
});

describe("markdownToStorage on a spike write-up", () => {
  // Shaped like a real spike summary: wrapped list items, a table nested in a
  // loose list, a numbered list with nested bullets, relative links, and a
  // list straight after a paragraph.
  const writeUp = [
    "# Spike summary: certificate renewal (draft, 2026-10-29)",
    "",
    "Scope: Docker Compose self-host (`bitwarden.sh`). Full working:",
    "[README.md](README.md), [lab log](lab.log).",
    "",
    "## AC1: Problem confirmed",
    "",
    "- **Certificates renew only on `start`.** `update` skips the restart when",
    "  no new release exists.",
    "- **The client renews in the last third of the certificate's life.** That gives:",
    "",
    "  | From | Lifetime | Longest safe gap |",
    "  | --- | --- | --- |",
    "  | Today | 90 days | ~30 days |",
    "  | 2027-02-10 | 64 days | ~21 days |",
    "",
    "- *Not done:* the original thread hasn't been reviewed.",
    "",
    "## AC3: Recommendation",
    "",
    "1. **[SHOT-331](https://bitwarden.atlassian.net/browse/SHOT-331): apply renewed certificates with",
    "   an nginx reload.** Prototyped:",
    "   - Real renewals were served with no dropped requests.",
    "   - Bad keys are refused, while the old certificate keeps being served.",
    "2. **Fallback** if the change can't land before 2027-02-10 (B1).",
    "",
    'The help page says renewal "checks occur each time Bitwarden is restarted".',
    "Capture this as a docs ticket with two parts:",
    "- **Now:** state that a restart is needed.",
    "- **When `renew-check` ships:** document the daily schedule.",
  ].join("\n");

  it("produces well-formed storage", () => {
    assertWellFormed(markdownToStorage(writeUp).storage);
  });

  it("keeps the structure", () => {
    const out = convert(writeUp);

    expect(out).toContain(
      "<h1>Spike summary: certificate renewal (draft, 2026-10-29)</h1>",
    );
    expect(out).toContain(
      "<li><p><strong>Certificates renew only on <code>start</code>.</strong> " +
        "<code>update</code> skips the restart when no new release exists.</p></li>",
    );
    expect(out).toContain(
      "<tr><td>2027-02-10</td><td>64 days</td><td>~21 days</td></tr></tbody></table></li>",
    );
    expect(out).toContain(
      '<ol><li><strong><a href="https://bitwarden.atlassian.net/browse/SHOT-331">SHOT-331</a>: ' +
        "apply renewed certificates with an nginx reload.</strong> Prototyped:\n<ul><li>",
    );
    expect(out).toContain(
      "Capture this as a docs ticket with two parts:</p>\n<ul><li><strong>Now:</strong>",
    );
  });

  it("reports the relative links it could not keep", () => {
    expect(markdownToStorage(writeUp).warnings).toEqual([
      expect.stringContaining('"README.md" (README.md)'),
      expect.stringContaining('"lab log" (lab.log)'),
    ]);
  });
});

describe("markdownToStorage keeps inline markup well-formed", () => {
  it("does not pull a code span or link that follows a URL into its href", () => {
    expect(convert("Endpoint: https://api.example.com/v2/pages/`{id}`")).toBe(
      '<p>Endpoint: <a href="https://api.example.com/v2/pages/">' +
        "https://api.example.com/v2/pages/</a><code>{id}</code></p>",
    );
    assertWellFormed(
      convert("See https://example.com/[the docs](https://example.com/docs)"),
    );
    assertWellFormed(convert("<https://x.com/`a`>"));
  });

  it("nests bold italic", () => {
    expect(convert("***bold italic***")).toBe(
      "<p><strong><em>bold italic</em></strong></p>",
    );
  });

  it("still nests emphasis inside bold", () => {
    expect(convert("**a *b* c**")).toBe(
      "<p><strong>a <em>b</em> c</strong></p>",
    );
  });

  it("leaves an overlapping marker literal rather than crossing tags", () => {
    expect(convert("**a*b**c*")).toBe("<p><strong>a*b</strong>c*</p>");
    assertWellFormed(convert("*see **this* now**"));
    assertWellFormed(convert("~~a **b~~ c**"));
  });

  it("stays well-formed for random combinations of inline markers", () => {
    // Fixed seed, so a failure reproduces exactly.
    let seed = 42;
    const next = () => (seed = (seed * 1103515245 + 12345) % 2 ** 31);
    const tokens = [
      "*",
      "**",
      "***",
      "_",
      "__",
      "~~",
      "`",
      "a",
      "b",
      " ",
      "&",
      "<",
      ">",
      "[x](https://e.com)",
      "https://e.com/",
      "<https://e.com>",
      "\\*",
    ];

    for (let run = 0; run < 5000; run++) {
      let input = "";
      const length = 1 + (next() % 14);
      for (let i = 0; i < length; i++) {
        input += tokens[next() % tokens.length];
      }
      try {
        assertWellFormed(convert(input));
      } catch (error) {
        throw new Error(
          `${JSON.stringify(input)}: ${(error as Error).message}`,
        );
      }
    }
  });
});
