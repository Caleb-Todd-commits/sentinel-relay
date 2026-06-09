import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Sentinel Relay",
    template: "%s · Sentinel Relay",
  },
  description:
    "A Band-powered multi-agent cybersecurity incident command center for high-stakes enterprise workflows.",
  applicationName: "Sentinel Relay",
  authors: [{ name: "Sentinel Relay Team" }],
  keywords: [
    "Band",
    "multi-agent",
    "cybersecurity",
    "incident response",
    "hackathon",
    "AI agents",
  ],
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#06101f",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
