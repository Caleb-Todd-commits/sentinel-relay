import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@sentinel-relay/schemas"],
};

export default nextConfig;
