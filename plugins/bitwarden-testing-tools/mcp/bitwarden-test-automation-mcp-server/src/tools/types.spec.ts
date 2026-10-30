import { describe, it, expect } from "vitest";
import { caseCount } from "./types.js";

describe("caseCount", () => {
  it("uses the singular only for exactly one case", () => {
    expect(caseCount(0)).toBe("0 cases");
    expect(caseCount(1)).toBe("1 case");
    expect(caseCount(2)).toBe("2 cases");
  });
});
