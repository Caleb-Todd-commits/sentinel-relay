import { NextResponse } from "next/server";
import { BandRestClient } from "@/lib/band/bandRestClient";
import { getBandConfigurationSummary, isBandReady } from "@/lib/band/bandConfig";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const live = searchParams.get("live") === "true";
  const summary = getBandConfigurationSummary();

  if (!live || !isBandReady()) {
    return NextResponse.json({
      status: isBandReady() ? "configured" : "not_configured",
      liveChecked: false,
      summary,
    });
  }

  const client = new BandRestClient();
  const commander = await client.verifyCommanderIdentity();
  const human = await client.verifyHumanIdentity();

  return NextResponse.json({
    status: commander.ok ? "ready" : "error",
    liveChecked: true,
    summary,
    checks: {
      commanderAgentApi: commander,
      humanApi: human,
    },
  });
}
