import { describe, it, expect } from "vitest";
import { detectPlatform, isScannedPath, scanFile } from "./scan.js";

const ANDROID = "Bitwarden.Android.Tests/Vault/ItemTests.cs";

describe("isScannedPath", () => {
  it("accepts .cs files under a top-level *.Tests folder", () => {
    expect(isScannedPath(`Bitwarden.Web.Tests/Vault/A.cs`)).toBe(true);
  });

  it("rejects other folders, other extensions, and TestBase", () => {
    expect(isScannedPath("Bitwarden.Core/Vault/A.cs")).toBe(false);
    expect(isScannedPath("Bitwarden.Web.Tests/Vault/A.txt")).toBe(false);
    expect(isScannedPath("Bitwarden.Web.Tests/TestBase.cs")).toBe(false);
    expect(isScannedPath("Bitwarden.Web.Tests/Vault/TestBase.cs")).toBe(false);
  });

  it("excludes ProdSmoke, which reuses functional IDs on purpose", () => {
    expect(isScannedPath("Bitwarden.Web.Tests/ProdSmoke/Login.cs")).toBe(false);
  });
});

describe("detectPlatform", () => {
  it("names the platform from the folder names", () => {
    expect(detectPlatform(ANDROID)).toBe("Android");
    expect(detectPlatform("Bitwarden.iOS.Tests/A.cs")).toBe("iOS");
    expect(detectPlatform("Bitwarden.Web.Tests/A.cs")).toBe("Web");
    expect(detectPlatform("Bitwarden.Authenticator.Android.Tests/A.cs")).toBe(
      "Authenticator - Android",
    );
    expect(detectPlatform("Bitwarden.Core.Tests/A.cs")).toBeNull();
  });
});

describe("scanFile", () => {
  it("reads a Description whose whole string is the case ID", () => {
    const text = [
      '[Description("20213")]',
      "public async Task Shows_menu()",
    ].join("\n");

    const hits = scanFile(ANDROID, text);

    expect(hits.map((hit) => [hit.id, hit.attribute, hit.line])).toEqual([
      [20213, "Description", 1],
    ]);
    expect(hits[0].platform).toBe("Android");
  });

  it("does not read a Description that has the ID inside other text", () => {
    const text = [
      '[Description("Login 2")]',
      "public async Task Shows_menu()",
      '[Description("9891533 and 9891534")]',
      "public async Task Shows_two()",
    ].join("\n");

    expect(scanFile(ANDROID, text)).toEqual([]);
  });

  it("reads a Covers argument that is exactly the case ID", () => {
    const text = ["[Covers(9891535)]", "public async Task Covers_it()"].join(
      "\n",
    );

    const hits = scanFile("Bitwarden.Web.Tests/A.cs", text);

    expect(hits.map((hit) => [hit.id, hit.attribute])).toEqual([
      [9891535, "Covers"],
    ]);
  });

  it("matches each Covers argument on its own, so only exact IDs count", () => {
    const text = [
      "[Covers(20213, Login 2, 20214)]",
      "public async Task Covers_many()",
    ].join("\n");

    const hits = scanFile("Bitwarden.Web.Tests/A.cs", text);

    expect(hits.map((hit) => [hit.id, hit.attribute, hit.line])).toEqual([
      [20213, "Covers", 1],
      [20214, "Covers", 1],
    ]);
  });

  it("does not read a Covers argument such as Login 2 as case 2", () => {
    const text = ["[Covers(Login 2)]", "public async Task Covers_name()"].join(
      "\n",
    );

    expect(scanFile("Bitwarden.Web.Tests/A.cs", text)).toEqual([]);
  });

  it("reads each quoted Covers argument as its own ID", () => {
    const text = [
      '[Covers("21066", "21067")]',
      "public async Task Covers_quoted()",
    ].join("\n");

    const hits = scanFile("Bitwarden.Web.Tests/A.cs", text);

    expect(hits.map((hit) => [hit.id, hit.attribute, hit.line])).toEqual([
      [21066, "Covers", 1],
      [21067, "Covers", 1],
    ]);
  });

  it("splits one quoted Covers string that holds a list", () => {
    const text = [
      '[Covers("21066, 21067")]',
      "public async Task Covers_quoted_list()",
    ].join("\n");

    const hits = scanFile("Bitwarden.Web.Tests/A.cs", text);

    expect(hits.map((hit) => [hit.id, hit.attribute, hit.line])).toEqual([
      [21066, "Covers", 1],
      [21067, "Covers", 1],
    ]);
  });

  it("marks a quoted Covers hit ignored when [Ignore] sits below it", () => {
    const text = [
      '[Covers("21066")]',
      '[Ignore("flaky")]',
      "public async Task Covers_skipped()",
    ].join("\n");

    const [hit] = scanFile("Bitwarden.Web.Tests/A.cs", text);

    expect(hit.id).toBe(21066);
    expect(hit.ignored).toBe(true);
  });

  it("does not read a quoted Covers argument that is not an ID", () => {
    const text = ['[Covers("abc")]', "public async Task Covers_text()"].join(
      "\n",
    );

    expect(scanFile("Bitwarden.Web.Tests/A.cs", text)).toEqual([]);
  });

  it("reads SetDescription only when the string is exactly digits", () => {
    const text = [
      '        .SetDescription("20213")',
      '        .SetDescription("Login 20214")',
    ].join("\n");

    const hits = scanFile("Bitwarden.API.Tests/A.cs", text);

    expect(hits.map((hit) => [hit.id, hit.attribute, hit.line])).toEqual([
      [20213, "SetDescription", 1],
    ]);
  });

  it("marks a method ignored when [Ignore] sits on it", () => {
    const text = [
      '[Description("100")]',
      '[Ignore("flaky")]',
      "public async Task Skipped()",
    ].join("\n");

    const [hit] = scanFile(ANDROID, text);

    expect(hit.ignored).toBe(true);
    expect(hit.knownBug).toBe(false);
  });

  it("marks a method ignored when its class carries [Ignore]", () => {
    const text = [
      '[Ignore("not ready")]',
      "public class VaultTests",
      "{",
      '    [Description("101")]',
      "    public async Task Inherits()",
    ].join("\n");

    const [hit] = scanFile(ANDROID, text);

    expect(hit.ignored).toBe(true);
  });

  it("reads KnownBug on the method", () => {
    const text = [
      '[Description("102")]',
      '[KnownBug("PM-12345")]',
      "public async Task Broken()",
    ].join("\n");

    const [hit] = scanFile(ANDROID, text);

    expect(hit.knownBug).toBe(true);
    expect(hit.ignored).toBe(false);
  });

  it("marks a method ignored when [Ignore] sits above the Description", () => {
    const text = [
      '[Ignore("flaky")]',
      '[Description("104")]',
      "public async Task Skipped_above()",
    ].join("\n");

    const [hit] = scanFile(ANDROID, text);

    expect(hit.ignored).toBe(true);
    expect(hit.knownBug).toBe(false);
  });

  it("reads KnownBug when it sits above the Covers", () => {
    const text = [
      '[KnownBug("PM-12345")]',
      "[Covers(105)]",
      "public async Task Broken_above()",
    ].join("\n");

    const [hit] = scanFile("Bitwarden.Web.Tests/A.cs", text);

    expect(hit.knownBug).toBe(true);
    expect(hit.ignored).toBe(false);
  });

  it("marks a method ignored for the combined [Test, Ignore(...)] form", () => {
    const text = [
      '[Description("106")]',
      '[Test, Ignore("x")]',
      "public async Task Skipped_combined()",
    ].join("\n");

    const [hit] = scanFile(ANDROID, text);

    expect(hit.ignored).toBe(true);
  });

  it("does not mark a method ignored for another attribute above the ID", () => {
    const text = [
      '[Category("Regression")]',
      '[IgnoreOnSimulator("slow")]',
      '[Description("107")]',
      "public async Task Runs_with_category()",
    ].join("\n");

    const [hit] = scanFile(ANDROID, text);

    expect(hit.ignored).toBe(false);
    expect(hit.knownBug).toBe(false);
  });

  it("does not look past the method signature for ignore", () => {
    const text = [
      '[Description("103")]',
      "public async Task Runs()",
      '[Ignore("another test")]',
      "public async Task Other()",
    ].join("\n");

    const [hit] = scanFile("Bitwarden.Web.Tests/A.cs", text);

    expect(hit.ignored).toBe(false);
  });

  it("returns no hits for a file without test IDs", () => {
    expect(scanFile(ANDROID, "public class Helper {}")).toEqual([]);
  });
});
