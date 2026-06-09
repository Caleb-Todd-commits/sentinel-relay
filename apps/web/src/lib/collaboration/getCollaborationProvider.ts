import type { CollaborationProvider } from "./CollaborationProvider";
import type { CollaborationProviderConfig } from "./types";
import { BandCollaborationProvider } from "./BandCollaborationProvider";
import { MockCollaborationProvider } from "./MockCollaborationProvider";

let singletonProvider: CollaborationProvider | undefined;

export function getCollaborationProvider(config?: Partial<CollaborationProviderConfig>): CollaborationProvider {
  if (singletonProvider && !config) {
    return singletonProvider;
  }

  const requestedMode = config?.mode ?? "mock";
  const preferServerProxy = config?.preferServerProxy ?? true;

  if (requestedMode === "band" && preferServerProxy) {
    const provider = new BandCollaborationProvider(config?.internalApiBasePath ?? "/api/collaboration");
    if (!config) singletonProvider = provider;
    return provider;
  }

  const provider = new MockCollaborationProvider();
  if (!config) singletonProvider = provider;
  return provider;
}

export function resetCollaborationProviderForTests(): void {
  singletonProvider = undefined;
}
