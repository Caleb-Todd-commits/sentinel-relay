import { NextResponse } from "next/server";
import type { ApprovalDecision, ApprovalRequest } from "@/lib/types";
import { BandRestClient } from "@/lib/band/bandRestClient";
import { addApprovalDecisionToRoom, addApprovalRequestToRoom, addRemoteWarning, hasRemotePostedApprovalDecision, hasRemotePostedApprovalRequest, markRemotePostedApprovalDecision, markRemotePostedApprovalRequest, toSnapshot } from "@/lib/band/bandRoomStore";
import { toBandEventFromApprovalDecision, toBandEventFromApprovalRequest } from "@/lib/band/bandMappers";
import { requireBandReady, routeErrorResponse } from "@/lib/band/routeResponses";

type ApprovalsPostBody =
  | { action: "requestHumanApproval"; roomId: string; request: ApprovalRequest }
  | { action: "submitHumanDecision"; roomId: string; decision: ApprovalDecision };

export async function POST(request: Request) {
  const notReady = requireBandReady();
  if (notReady) return notReady;

  const body = (await request.json().catch(() => ({}))) as Partial<ApprovalsPostBody>;
  const client = new BandRestClient();

  try {
    switch (body.action) {
      case "requestHumanApproval": {
        if (!body.roomId || !body.request) {
          return NextResponse.json({ code: "INVALID_APPROVAL_REQUEST_INPUT", error: "requestHumanApproval requires roomId and request.", recoverable: true }, { status: 400 });
        }
        const record = addApprovalRequestToRoom(body.roomId, body.request);
        const alreadyPosted = hasRemotePostedApprovalRequest(body.roomId, body.request.id);
        if (!alreadyPosted) {
          const eventResult = await client.postAgentEvent(record.bandChatId ?? body.roomId, toBandEventFromApprovalRequest(body.request));
          if (!eventResult.ok) {
            addRemoteWarning(body.roomId, eventResult.error ?? "Unable to post approval request event to Band.", { status: eventResult.status, raw: eventResult.raw, requestId: body.request.id });
          }
          markRemotePostedApprovalRequest(body.roomId, body.request.id);
        }
        return NextResponse.json({ ok: true, snapshot: toSnapshot(record), remoteSkippedDuplicate: alreadyPosted });
      }

      case "submitHumanDecision": {
        if (!body.roomId || !body.decision) {
          return NextResponse.json({ code: "INVALID_APPROVAL_DECISION_INPUT", error: "submitHumanDecision requires roomId and decision.", recoverable: true }, { status: 400 });
        }
        const record = addApprovalDecisionToRoom(body.roomId, body.decision);
        const alreadyPosted = hasRemotePostedApprovalDecision(body.roomId, body.decision.id);
        if (!alreadyPosted) {
          const eventResult = await client.postAgentEvent(record.bandChatId ?? body.roomId, toBandEventFromApprovalDecision(body.decision));
          if (!eventResult.ok) {
            addRemoteWarning(body.roomId, eventResult.error ?? "Unable to post approval decision event to Band.", { status: eventResult.status, raw: eventResult.raw, decisionId: body.decision.id });
          }
          markRemotePostedApprovalDecision(body.roomId, body.decision.id);
        }
        return NextResponse.json({ ok: true, snapshot: toSnapshot(record), remoteSkippedDuplicate: alreadyPosted });
      }

      default:
        return NextResponse.json({ code: "UNKNOWN_COLLABORATION_APPROVAL_ACTION", error: `Unknown approvals action: ${String(body.action)}`, recoverable: true }, { status: 400 });
    }
  } catch (error) {
    return routeErrorResponse(error, "BAND_APPROVALS_ROUTE_ERROR");
  }
}
