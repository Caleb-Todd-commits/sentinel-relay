import type { CollaborationProvider } from "./CollaborationProvider";
import type { CollaborationRoomSnapshot } from "./types";
import type { WorkflowViewModel } from "@/lib/workflow/types";

export type SyncMockWorkflowResult = {
  roomId: string;
  syncedStep: number;
  snapshot?: CollaborationRoomSnapshot;
};

/**
 * Sends only the messages that are new at this workflow step.
 *
 * In Mock Mode the provider is in-memory so a full reset+replay is fine.
 * In Band Mode we send each message exactly once as the user advances steps,
 * so Band sees a natural flowing conversation rather than a flood of resets.
 */
export async function syncMockWorkflowToProvider(
  provider: CollaborationProvider,
  roomId: string,
  workflow: WorkflowViewModel,
): Promise<SyncMockWorkflowResult> {
  const isMock = provider.mode === "mock";

  if (isMock) {
    // Mock provider is in-memory — full reset+replay keeps it consistent.
    await provider.resetRoom(roomId);

    for (const message of workflow.messages) {
      await provider.sendMessage(roomId, message);
    }
  } else {
    // Band provider — send only the message introduced at this step.
    const currentMessage = workflow.messages.find(
      (m) => m.sequence === workflow.stepIndex,
    );
    if (currentMessage) {
      await provider.sendMessage(roomId, currentMessage);
    }
  }

  if (workflow.approvalRequest) {
    await provider.requestHumanApproval(roomId, workflow.approvalRequest);
  }

  if (workflow.approvalDecision) {
    await provider.submitHumanDecision(roomId, workflow.approvalDecision);
  }

  for (const task of workflow.remediationTasks) {
    await provider.updateTaskStatus(roomId, task.id, task.status);
  }

  const snapshot = await provider.getRoomSnapshot(roomId);
  return { roomId, syncedStep: workflow.stepIndex, snapshot };
}
