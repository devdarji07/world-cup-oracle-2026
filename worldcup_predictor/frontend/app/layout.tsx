import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "World Cup Oracle 2026",
  description: "AI-powered FIFA World Cup 2026 predictions and simulation platform.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
