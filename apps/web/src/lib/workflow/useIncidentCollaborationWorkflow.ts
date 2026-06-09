"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { sentinelRelayDemo } from "@/lib/demo/sentinelRelayDemo";
import { getBrowserCollaborationConfig, getCollaborationProvider } from "@/lib/collaboration";
import type { CollaborationProvider, CollaborationProviderHealth, CollaborationRoomSnapshot } from "@/lib/collaboration";
import { syncMockWorkflowToProvider } from "@/lib/collaboration/syncMockWorkflowToProvider";
import { deriveWorkflowViewModel } from "./deriveWorkflowState";
import type { WorkflowCollaborationState } from "./types";

const APPROVAL_DECISION_STEP = 8;

function getStableProvider(): CollaborationProvider {
  return getCollaborationProvider(getBrowserCollaborationConfig());
}

export function useIncidentCollaborationWorkflow(initialStep = 0) {
  const provider = useMemo(() => getStableProvider(), []);
  const [stepIndex, setStepIndex] = useState(initialStep);
  const [roomId, setRoomId] = useState<string | undefined>();
  const [providerHealth, setProviderHealth] = useState<CollaborationProviderHealth>(() => provider.getHealth());
  const [snapshot, setSnapshot] = useState<CollaborationRoomSnapshot | undefined>();
  const [syncStatus, setSyncStatus] = useState<WorkflowCollaborationState["syncStatus"]>("initializing");
  const [providerError, setProviderError] = useState<string | undefined>();
  const [lastSyncedStep, setLastSyncedStep] = useState(-1);
  const activeSyncToken = useRef(0);

  const baseWorkflow = useMemo(() => deriveWorkflowViewModel(stepIndex), [stepIndex]);

  useEffect(() => {
    let cancelled = false;

    async function initializeRoom() {
      try {
        setProviderHealth(provider.getHealth());
        setSyncStatus("initializing");
        const room = await provider.createIncidentRoom({
          caseId: sentinelRelayDemo.case.id,
          title: sentinelRelayDemo.case.title,
          requestedBy: "war-room-ui",
        });

        for (const agent of sentinelRelayDemo.agents) {
          await provider.registerAgent(room.id, agent);
        }

        if (!cancelled) {
          setRoomId(room.id);
          setProviderError(undefined);
        }
      } catch (error) {
        if (!cancelled) {
          setProviderError(error instanceof Error ? error.message : "Unable to initialize collaboration provider.");
          setSyncStatus("error");
        }
      }
    }

    void initializeRoom();

    return () => {
      cancelled = true;
    };
  }, [provider]);

  useEffect(() => {
    if (!roomId) return undefined;
    return provider.subscribeToRoomSnapshot(roomId, (nextSnapshot: CollaborationRoomSnapshot) => {
      setSnapshot(nextSnapshot);
    });
  }, [provider, roomId]);

  useEffect(() => {
    if (!roomId) return;

    const syncToken = activeSyncToken.current + 1;
    activeSyncToken.current = syncToken;

    async function syncStep() {
      try {
        setSyncStatus("syncing");
        const result = await syncMockWorkflowToProvider(provider, roomId, baseWorkflow);
        if (activeSyncToken.current !== syncToken) return;
        setSnapshot(result.snapshot);
        setLastSyncedStep(result.syncedStep);
        setProviderHealth(provider.getHealth());
        setProviderError(undefined);
        setSyncStatus("ready");
      } catch (error) {
        if (activeSyncToken.current !== syncToken) return;
        setProviderError(error instanceof Error ? error.message : "Unable to sync workflow step to collaboration provider.");
        setProviderHealth(provider.getHealth());
        setSyncStatus("error");
      }
    }

    void syncStep();
  }, [baseWorkflow, provider, roomId]);

  function start() {
    setStepIndex(1);
  }

  function advance() {
    setStepIndex((current: number) => {
      const state = deriveWorkflowViewModel(current);
      if (!state.canAdvance) return current;
      return Math.min(current + 1, state.totalSteps);
    });
  }

  function approveContainment() {
    setStepIndex((current: number) => Math.max(current, APPROVAL_DECISION_STEP));
  }

  function replay() {
    setStepIndex(0);
  }

  function completeDemo() {
    setStepIndex(deriveWorkflowViewModel(stepIndex).totalSteps);
  }

  function jumpToStep(nextStepIndex: number) {
    const totalSteps = deriveWorkflowViewModel(stepIndex).totalSteps;
    setStepIndex(Math.max(0, Math.min(nextStepIndex, totalSteps)));
  }

  const providerMessages = snapshot?.messages;
  const shouldUseProviderMessages = lastSyncedStep === stepIndex && providerMessages;
  const collaboration: WorkflowCollaborationState = {
    providerMode: provider.mode,
    providerHealth,
    roomId,
    syncStatus,
    lastSyncedStep,
    error: providerError,
    snapshot,
    auditEventCount: snapshot?.auditEvents.length ?? 0,
    registeredAgentCount: snapshot?.registeredAgents.length ?? 0,
  };

  return {
    ...baseWorkflow,
    messages: shouldUseProviderMessages ? providerMessages : baseWorkflow.messages,
    modeLabel: `${providerHealth.label} · ${syncStatus}`,
    collaboration,
    actions: {
      start,
      advance,
      approveContainment,
      replay,
      completeDemo,
      jumpToStep,
    },
  };
}
