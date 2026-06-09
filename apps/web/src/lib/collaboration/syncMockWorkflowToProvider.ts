import type { CollaborationProvider } from "./CollaborationProvider";
import type { CollaborationRoomSnapshot } from "./types";
import type { WorkflowViewModel } from "@/lib/workflow/types";

export type SyncMockWorkflowResult = {
  roomId: string;
  syncedStep: number;
  snapshot?: CollaborationRoomSnapshot;
};

/**
 * Replays the deterministic demo step into the active collaboration provider.
 *
 * In Mock Mode this gives the War Room a true provider-backed event stream.
 * In Band Mode this will become the adapter handoff point in Step 8.
 */
export async function syncMockWorkflowToProvider(
  provider: CollaborationProvider,
  roomId: string,
  workflow: WorkflowViewModel,
): Promise<SyncMockWorkflowResult> {
  await provider.resetRoom(roomId);

  for (const message of workflow.messages) {
    await provider.sendMessage(roomId, message);
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
