import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Smart Analytics Data Mining Platform",
  description: "Premium AI analytics SaaS for automated data mining, visualization, and intelligent reporting.",
  keywords: ["analytics", "data mining", "clustering", "PCA", "association rules", "time series"]
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} min-h-screen bg-background font-sans`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
