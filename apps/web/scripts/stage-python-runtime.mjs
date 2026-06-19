import { cp, mkdir, rm } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const webRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = path.resolve(webRoot, "../..");
const runtimeRoot = path.join(webRoot, ".python-runtime");

const agentDirectories = [
  "common",
  "mock",
  "commander",
  "forensics",
  "threat_intel",
  "code_review",
  "risk_compliance",
  "remediation",
];

await rm(runtimeRoot, { recursive: true, force: true });
await mkdir(path.join(runtimeRoot, "agents"), { recursive: true });

for (const directory of agentDirectories) {
  await cp(
    path.join(repoRoot, "agents", directory),
    path.join(runtimeRoot, "agents", directory),
    {
      recursive: true,
      filter: (source) => !source.includes("__pycache__") && !source.endsWith(".pyc"),
    },
  );
}

await cp(path.join(repoRoot, "data", "incidents"), path.join(runtimeRoot, "data", "incidents"), {
  recursive: true,
});

console.log("Staged evidence-driven Python runtime for Vercel.");
