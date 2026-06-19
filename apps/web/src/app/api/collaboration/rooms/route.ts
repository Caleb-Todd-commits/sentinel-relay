import { NextResponse } from "next/server";
import type { AgentProfile } from "@/lib/types";
import type { CollaborationRoomSnapshot } from "@/lib/collaboration/types";
import { BandRestClient } from "@/lib/band/bandRestClient";
import { getBandRuntimeConfig, getConfiguredAgentForProfile, getBandConfigurationSummary } from "@/lib/band/bandConfig";
import { addRemoteWarning, createLocalRoomRecord, getRoomSnapshot, hydrateRoomRecord, registerAgentInRoom, resetRoomRecord, toSnapshot } from "@/lib/band/bandRoomStore";
import { requireBandReady, routeErrorResponse } from "@/lib/band/routeResponses";
import { getScenarioSnapshot } from "@/lib/scenarios";

type RoomPostBody =
  | { action: "createIncidentRoom"; input: { caseId: string; title?: string; requestedBy?: string } }
  | { action: "registerAgent"; roomId: string; agent: AgentProfile | string }
  | { action: "resetRoom"; roomId: string }
  | { action: "hydrateRoomSnapshot"; roomId: string; snapshot: Partial<CollaborationRoomSnapshot> };

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const roomId = searchParams.get("roomId");

  if (!roomId) {
    return NextResponse.json({ health: getBandConfigurationSummary() });
  }

  const snapshot = getRoomSnapshot(roomId) ?? getScenarioSnapshot(roomId);
  if (!snapshot) {
    return NextResponse.json({ code: "BAND_ROOM_NOT_FOUND", error: `No local Band room mirror found for ${roomId}.`, recoverable: true }, { status: 404 });
  }

  return NextResponse.json({ snapshot, health: getBandConfigurationSummary() });
}

export async function POST(request: Request) {
  const notReady = requireBandReady();
  if (notReady) return notReady;

  const body = (await request.json().catch(() => ({}))) as Partial<RoomPostBody>;
  const client = new BandRestClient();
  const config = getBandRuntimeConfig();

  try {
    switch (body.action) {
      case "createIncidentRoom": {
        const input = body.input;
        if (!input?.caseId) {
          return NextResponse.json({ code: "INVALID_ROOM_INPUT", error: "createIncidentRoom requires input.caseId.", recoverable: true }, { status: 400 });
        }

        const createResult = await client.createAgentChat();
        if (!createResult.ok || !createResult.data?.id) {
          return NextResponse.json(
            {
              code: "BAND_CREATE_CHAT_FAILED",
              error: createResult.error ?? "Band did not return a chat id.",
              recoverable: true,
              status: createResult.status,
              raw: createResult.raw,
            },
            { status: createResult.status >= 400 ? createResult.status : 502 },
          );
        }

        const record = createLocalRoomRecord({
          caseId: input.caseId,
          title: input.title,
          roomId: createResult.data.id,
          bandChat: createResult.data,
          createdBy: input.requestedBy ?? "war-room-ui",
        });

        const metadataEvent = await client.postAgentEvent(record.bandChatId ?? record.room.id, {
          event: {
            content: `Sentinel Relay opened ${input.caseId}: ${input.title ?? "Untitled incident"}`,
            message_type: "task",
            metadata: {
              source_system: "sentinel_relay",
              envelope_type: "sentinel_relay.room_created",
              case_id: input.caseId,
              room_id: record.room.id,
              title: input.title,
            },
          },
        });

        if (!metadataEvent.ok) {
          addRemoteWarning(record.room.id, metadataEvent.error ?? "Band room metadata event failed.", { status: metadataEvent.status, raw: metadataEvent.raw });
        }

        return NextResponse.json(record.room);
      }

      case "registerAgent": {
        if (!body.roomId || !body.agent) {
          return NextResponse.json({ code: "INVALID_REGISTER_AGENT_INPUT", error: "registerAgent requires roomId and agent.", recoverable: true }, { status: 400 });
        }

        if (typeof body.agent === "string") {
          const configuredAgent = config.configuredAgents[body.agent];
          if (!configuredAgent?.participantId) {
            addRemoteWarning(body.roomId, `No Band participant id configured for ${body.agent}; local registration only.`, { agentId: body.agent });
            return NextResponse.json({ ok: true, localOnly: true });
          }
          const addResult = await client.addAgentParticipant(body.roomId, configuredAgent.participantId);
          if (!addResult.ok) {
            addRemoteWarning(body.roomId, addResult.error ?? `Unable to add ${body.agent} as Band participant.`, { agentId: body.agent, status: addResult.status, raw: addResult.raw });
          }
          return NextResponse.json({ ok: true, remote: addResult.ok, warning: addResult.ok ? undefined : addResult.error });
        }

        const record = registerAgentInRoom(body.roomId, body.agent);
        const configuredAgent = getConfiguredAgentForProfile(body.agent, config);

        if (configuredAgent?.participantId) {
          const addResult = await client.addAgentParticipant(body.roomId, configuredAgent.participantId);
          if (!addResult.ok) {
            addRemoteWarning(body.roomId, addResult.error ?? `Unable to add ${body.agent.name} as Band participant.`, { agentId: body.agent.id, status: addResult.status, raw: addResult.raw });
          }
        } else {
          addRemoteWarning(body.roomId, `No Band participant id configured for ${body.agent.id}; local mirror registration only.`, { agentId: body.agent.id });
        }

        return NextResponse.json({ ok: true, snapshot: toSnapshot(record) });
      }

      case "resetRoom": {
        if (!body.roomId) {
          return NextResponse.json({ code: "INVALID_RESET_INPUT", error: "resetRoom requires roomId.", recoverable: true }, { status: 400 });
        }
        const record = resetRoomRecord(body.roomId);
        const eventResult = await client.postAgentEvent(body.roomId, {
          event: {
            content: "Sentinel Relay replay reset the local incident mirror.",
            message_type: "task",
            metadata: { source_system: "sentinel_relay", envelope_type: "sentinel_relay.room_reset", room_id: body.roomId },
          },
        });
        if (!eventResult.ok) {
          addRemoteWarning(body.roomId, eventResult.error ?? "Unable to post reset event to Band.", { status: eventResult.status, raw: eventResult.raw });
        }
        return NextResponse.json({ ok: true, snapshot: toSnapshot(record) });
      }

      case "hydrateRoomSnapshot": {
        if (!body.roomId) {
          return NextResponse.json({ code: "INVALID_HYDRATE_INPUT", error: "hydrateRoomSnapshot requires roomId.", recoverable: true }, { status: 400 });
        }
        const record = hydrateRoomRecord(body.roomId, body.snapshot ?? {});
        return NextResponse.json({ ok: true, snapshot: toSnapshot(record) });
      }

      default:
        return NextResponse.json({ code: "UNKNOWN_COLLABORATION_ROOM_ACTION", error: `Unknown rooms action: ${String(body.action)}`, recoverable: true }, { status: 400 });
    }
  } catch (error) {
    return routeErrorResponse(error, "BAND_ROOMS_ROUTE_ERROR");
  }
}
