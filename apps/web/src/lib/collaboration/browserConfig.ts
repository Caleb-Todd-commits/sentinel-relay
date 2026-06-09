import type { CollaborationProviderConfig } from "./types";

export function getBrowserCollaborationConfig(): Partial<CollaborationProviderConfig> {
  const requestedMode = process.env.NEXT_PUBLIC_COLLABORATION_MODE === "band" ? "band" : "mock";
  const bandModeEnabled = process.env.NEXT_PUBLIC_ENABLE_BAND_MODE === "true";

  if (requestedMode === "band" && bandModeEnabled) {
    return {
      mode: "band",
      preferServerProxy: true,
      internalApiBasePath: process.env.NEXT_PUBLIC_COLLABORATION_API_BASE_PATH ?? "/api/collaboration",
    };
  }

  return { mode: "mock" };
}
