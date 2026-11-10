import { describe, it, expect } from "vitest";
import { tlsGuardMessage } from "./config.js";

describe("tlsGuardMessage", () => {
  it("refuses to start when NODE_TLS_REJECT_UNAUTHORIZED is 0", () => {
    const message = tlsGuardMessage({ NODE_TLS_REJECT_UNAUTHORIZED: "0" });
    expect(message).toMatch(
      /^Refusing to start: NODE_TLS_REJECT_UNAUTHORIZED is 0/,
    );
  });

  it("allows start when the variable is unset or set to 1", () => {
    expect(tlsGuardMessage({})).toBeUndefined();
    expect(
      tlsGuardMessage({ NODE_TLS_REJECT_UNAUTHORIZED: "1" }),
    ).toBeUndefined();
  });
});
