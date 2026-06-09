import { NextResponse } from "next/server";
import type { AgentMessage, TaskStatus } from "@/lib/types";
import { BandRestClient } from "@/lib/band/bandRestClient";
import { addMessageToRoom, addRemoteWarning, getRoomSnapshot, hasRemotePostedMessage, hasRemotePostedTaskStatus, markRemotePostedMessage, markRemotePostedTaskStatus, toSnapshot, updateTaskStatusInRoom } from "@/lib/band/bandRoomStore";
import { buildMentions, buildRoutedTextContent, toBandEventFromAgentMessage, toBandEventFromTaskStatus } from "@/lib/band/bandMappers";
import { requireBandReady, routeErrorResponse } from "@/lib/band/routeResponses";

type MessagesPostBody =
  | { action: "sendMessage"; roomId: string; message: AgentMessage }
  | { action: "updateTaskStatus"; roomId: string; taskId: string; status: TaskStatus };

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const roomId = searchParams.get("roomId");
  if (!roomId) {
    return NextResponse.json({ code: "ROOM_ID_REQUIRED", error: "roomId query parameter is required.", recoverable: true }, { status: 400 });
  }

  const snapshot = getRoomSnapshot(roomId);
  if (!snapshot) {
    return NextResponse.json({ code: "BAND_ROOM_NOT_FOUND", error: `No local Band room mirror found for ${roomId}.`, recoverable: true }, { status: 404 });
  }

  return NextResponse.json({ messages: snapshot.messages, snapshot });
}

export async function POST(request: Request) {
  const notReady = requireBandReady();
  if (notReady) return notReady;

  const body = (await request.json().catch(() => ({}))) as Partial<MessagesPostBody>;
  const client = new BandRestClient();

  try {
    switch (body.action) {
      case "sendMessage": {
        if (!body.roomId || !body.message) {
          return NextResponse.json({ code: "INVALID_SEND_MESSAGE_INPUT", error: "sendMessage requires roomId and message.", recoverable: true }, { status: 400 });
        }

        const record = addMessageToRoom(body.roomId, body.message);
        const alreadyPosted = hasRemotePostedMessage(body.roomId, body.message.id);

        if (!alreadyPosted) {
          const eventResult = await client.postAgentEvent(record.bandChatId ?? body.roomId, toBandEventFromAgentMessage(body.message));
          if (!eventResult.ok) {
            addRemoteWarning(body.roomId, eventResult.error ?? "Unable to post structured message event to Band.", { status: eventResult.status, raw: eventResult.raw, messageId: body.message.id });
          }

          const mentions = buildMentions(body.message.targetAgentIds);
          if (mentions.length > 0) {
            const textResult = await client.sendAgentTextMessage(record.bandChatId ?? body.roomId, buildRoutedTextContent(body.message, mentions), mentions);
            if (!textResult.ok) {
              addRemoteWarning(body.roomId, textResult.error ?? "Unable to post routed Band text message.", { status: textResult.status, raw: textResult.raw, messageId: body.message.id });
            }
          } else {
            addRemoteWarning(body.roomId, `Message ${body.message.id} was stored as a Band event only because no configured target @mentions were available.`, { messageId: body.message.id, targetAgentIds: body.message.targetAgentIds ?? [] });
          }

          markRemotePostedMessage(body.roomId, body.message.id);
        }

        const snapshot = getRoomSnapshot(body.roomId);
        return NextResponse.json({ ok: true, snapshot, remoteSkippedDuplicate: alreadyPosted });
      }

      case "updateTaskStatus": {
        if (!body.roomId || !body.taskId || !body.status) {
          return NextResponse.json({ code: "INVALID_TASK_STATUS_INPUT", error: "updateTaskStatus requires roomId, taskId, and status.", recoverable: true }, { status: 400 });
        }

        const record = updateTaskStatusInRoom(body.roomId, body.taskId, body.status);
        const alreadyPosted = hasRemotePostedTaskStatus(body.roomId, body.taskId, body.status);
        if (!alreadyPosted) {
          const eventResult = await client.postAgentEvent(record.bandChatId ?? body.roomId, toBandEventFromTaskStatus(body.roomId, body.taskId, body.status));
          if (!eventResult.ok) {
            addRemoteWarning(body.roomId, eventResult.error ?? "Unable to post task status event to Band.", { status: eventResult.status, raw: eventResult.raw, taskId: body.taskId });
          }
          markRemotePostedTaskStatus(body.roomId, body.taskId, body.status);
        }

        return NextResponse.json({ ok: true, snapshot: toSnapshot(record), remoteSkippedDuplicate: alreadyPosted });
      }

      default:
        return NextResponse.json({ code: "UNKNOWN_COLLABORATION_MESSAGE_ACTION", error: `Unknown messages action: ${String(body.action)}`, recoverable: true }, { status: 400 });
    }
  } catch (error) {
    return routeErrorResponse(error, "BAND_MESSAGES_ROUTE_ERROR");
  }
}
