import { execSync } from "node:child_process";
import { readFileSync } from "node:fs";

process.chdir(import.meta.dirname);
const corepackVersion = JSON.parse(
  readFileSync("package.json", "utf8"),
).devDependencies.corepack.trim();
if (!/^\d+\.\d+\.\d+$/.test(corepackVersion)) {
  console.error(
    `package.json devDependencies.corepack must be x.y.z, got "${corepackVersion}"`,
  );
  process.exit(1);
}

// stdout carries MCP traffic, so install and build output goes to stderr.
// The shell lets npm resolve to npm.cmd on Windows.
const pnpm = (args) =>
  execSync(`npm exec --yes corepack@${corepackVersion} -- pnpm ${args}`, {
    stdio: ["ignore", 2, 2],
  });

pnpm("install --frozen-lockfile --prod --silent");
pnpm("run build");
await import("./build/index.js");
