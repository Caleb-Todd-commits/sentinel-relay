import type { NextConfig } from "next";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

function loadRootEnv() {
  const envPath = resolve(process.cwd(), "../..", ".env");
  if (!existsSync(envPath)) return;

  for (const line of readFileSync(envPath, "utf8").split(/\r?\n/)) {
    const match = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
    if (!match) continue;

    const key = match[1];
    const rawValue = match[2];
    if (!key || rawValue === undefined) continue;

    if (process.env[key] !== undefined) continue;

    const withoutComment = rawValue.replace(/\s+#.*$/, "").trim();
    process.env[key] = withoutComment.replace(/^(['"])(.*)\1$/, "$2");
  }
}

loadRootEnv();

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@sentinel-relay/schemas"],
};

export default nextConfig;
