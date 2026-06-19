import { getRoomSnapshot } from "@/lib/band/bandRoomStore";
import { getScenarioSnapshot } from "@/lib/scenarios";

export const dynamic = "force-dynamic";

function eventBlock(eventName: string, data: unknown): string {
  return `event: ${eventName}\ndata: ${JSON.stringify(data)}\n\n`;
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const roomId = searchParams.get("roomId");
  if (!roomId) {
    return new Response(eventBlock("error", { error: "roomId query parameter is required." }), {
      status: 400,
      headers: { "Content-Type": "text/event-stream" },
    });
  }

  const encoder = new TextEncoder();
  let interval: ReturnType<typeof setInterval> | undefined;

  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      const sendSnapshot = () => {
        const snapshot = getRoomSnapshot(roomId) ?? getScenarioSnapshot(roomId);
        if (snapshot) {
          controller.enqueue(encoder.encode(eventBlock("snapshot", { snapshot })));
        } else {
          controller.enqueue(encoder.encode(eventBlock("heartbeat", { roomId, status: "waiting_for_room" })));
        }
      };

      sendSnapshot();
      interval = setInterval(sendSnapshot, 1000);

      request.signal.addEventListener("abort", () => {
        if (interval) clearInterval(interval);
        try {
          controller.close();
        } catch {
          // The connection may already be closed by the browser.
        }
      });
    },
    cancel() {
      if (interval) clearInterval(interval);
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
