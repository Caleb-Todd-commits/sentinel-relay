import type { ReactNode } from "react";

export function WarRoomSectionHeader({ eyebrow, title, children }: { eyebrow: string; title: string; children?: ReactNode }) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-3">
      <div>
        <p className="relay-label">{eyebrow}</p>
        <h2 className="mt-1 text-xl font-semibold tracking-tight text-slate-100">{title}</h2>
      </div>
      {children}
    </div>
  );
}
