type BadgeTone = "neutral" | "success" | "warning" | "danger" | "accent";

const toneClass: Record<BadgeTone, string> = {
  neutral: "border-slate-700 bg-slate-950/40 text-slate-300",
  success: "border-emerald-400/30 bg-emerald-400/10 text-emerald-200",
  warning: "border-amber-400/30 bg-amber-400/10 text-amber-200",
  danger: "border-rose-400/30 bg-rose-400/10 text-rose-200",
  accent: "border-sky-400/30 bg-sky-400/10 text-sky-200",
};

export function Badge({ children, tone = "neutral" }: { children: React.ReactNode; tone?: BadgeTone }) {
  return <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-medium ${toneClass[tone]}`}>{children}</span>;
}
