import { NextResponse } from "next/server";
import { getBandRuntimeConfig, isBandReady } from "./bandConfig";
import type { BandRouteErrorBody } from "./bandTypes";

export function notConfiguredResponse() {
  const config = getBandRuntimeConfig();
  const body: BandRouteErrorBody = {
    code: config.enabled ? "BAND_MISSING_REQUIRED_ENV" : "BAND_PROVIDER_NOT_ENABLED",
    error: config.enabled
      ? "Band Mode is enabled, but the server is missing required Band environment variables."
      : "Band server routes are present, but Band Mode is not enabled for this deployment.",
    recoverable: true,
    missing: config.missingRequired,
    warnings: config.warnings,
  };
  return NextResponse.json(body, { status: 503 });
}

export function requireBandReady() {
  if (!isBandReady()) {
    return notConfiguredResponse();
  }
  return undefined;
}

export function routeErrorResponse(error: unknown, fallbackCode = "BAND_ROUTE_ERROR") {
  return NextResponse.json(
    {
      code: fallbackCode,
      error: error instanceof Error ? error.message : "Unexpected Band route failure.",
      recoverable: true,
    },
    { status: 500 },
  );
}
