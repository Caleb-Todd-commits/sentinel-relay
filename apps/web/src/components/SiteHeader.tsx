import Link from "next/link";

const navItems = [
  { href: "/demo", label: "Scenario" },
  { href: "/scenarios", label: "Run Live" },
  { href: "/war-room", label: "War Room" },
  { href: "/report", label: "Report" },
];

export function SiteHeader() {
  return (
    <header className="relay-shell py-4">
      <div className="flex items-center justify-between gap-4">
        <Link href="/" className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl border border-sky-400/30 bg-sky-400/10 text-sm font-bold text-sky-100">
            SR
          </div>
          <div>
            <p className="text-sm font-semibold leading-none">Sentinel Relay</p>
            <p className="mt-1 text-xs text-slate-500">Band-powered incident command</p>
          </div>
        </Link>
        <nav className="flex items-center gap-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="rounded-xl px-3 py-2 text-sm text-slate-300 transition hover:bg-slate-800/70 hover:text-white"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
