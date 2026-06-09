import type { AgentMessageType, Severity } from "@/lib/types";

export function formatSeverity(severity: Severity): string {
  return severity.charAt(0).toUpperCase() + severity.slice(1);
}

export function formatStatus(status: string): string {
  return status
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function formatMessageType(type: AgentMessageType): string {
  return type
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function asPercent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function clampStep(step: number, max: number, min = 0): number {
  if (step < min) return min;
  if (step > max) return max;
  return step;
}

export function formatStepFraction(current: number, total: number): string {
  return `${current}/${total}`;
}
