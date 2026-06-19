import { NextResponse } from "next/server";
import {
  addApprovalDecisionToRoom,
  addApprovalRequestToRoom,
  addMessageToRoom,
  createLocalRoomRecord,
  getRoomRecord,
  resetRoomRecord,
  updateTaskStatusInRoom,
} from "@/lib/band/bandRoomStore";
import { getScenario } from "@/lib/scenarios";

// Give Vercel enough time to post all 18 messages
export const maxDuration = 60;

function stableRoomId(caseId: string): string {
  return `scenario-room-${caseId}`;
}

export async function POST(request: Request) {
  let body: { incidentId?: string } = {};
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body." }, { status: 400 });
  }

  const incidentId = (body.incidentId ?? "INC-1042").toUpperCase();
  const scenario = getScenario(incidentId);

  if (!scenario) {
    return NextResponse.json(
      { error: `Unknown incident: ${incidentId}. Available: INC-1042, INC-1043.` },
      { status: 400 },
    );
  }

  const roomId = stableRoomId(scenario.caseId);

  // Reset or create the room so replays work cleanly
  if (getRoomRecord(roomId)) {
    resetRoomRecord(roomId);
  } else {
    createLocalRoomRecord({
      caseId: scenario.caseId,
      title: scenario.title,
      roomId,
      createdBy: "scenarios-ui",
    });
  }

  // Post all 18 messages into the room store (persists in globalThis across requests)
  for (const message of scenario.messages) {
    addMessageToRoom(roomId, { ...message, roomId });
  }

  // Record approval request, decision, and task statuses
  addApprovalRequestToRoom(roomId, { ...scenario.approvalRequest, caseId: scenario.caseId });
  addApprovalDecisionToRoom(roomId, scenario.approvalDecision);
  for (const { taskId, status } of scenario.remediationTaskStatuses) {
    updateTaskStatusInRoom(roomId, taskId, status);
  }

  return NextResponse.json({
    ok: true,
    incidentId,
    roomId,
    messagesPosted: scenario.messages.length,
  });
}
