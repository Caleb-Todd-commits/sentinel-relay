import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        relay: {
          ink: "#06101f",
          panel: "#0b1628",
          border: "#243149",
          muted: "#94a3b8",
          text: "#e5edf8",
          accent: "#8bd5ff",
          success: "#8ff0bc",
          warning: "#facc6b",
          danger: "#ff9b9b"
        }
      },
      boxShadow: {
        panel: "0 24px 80px rgba(0, 0, 0, 0.28)"
      }
    }
  },
  plugins: []
};

export default config;
