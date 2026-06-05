import type { Metadata } from "next";
import { Geist, Geist_Mono, Vazirmatn } from "next/font/google";
import "./globals.css";

import { LanguageProvider } from "@/i18n/LanguageProvider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const vazirmatn = Vazirmatn({
  variable: "--font-vazirmatn",
  subsets: ["arabic"],
  display: "swap",
  weight: ["500", "600", "700"],
  preload: true,
});

export const metadata: Metadata = {
  title: "BetavanX | Construction Intelligence",
  description:
    "Operational construction intelligence command center",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fa" dir="rtl" data-locale="fa" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${vazirmatn.variable} antialiased`}
      >
        <LanguageProvider>{children}</LanguageProvider>
      </body>
    </html>
  );
}
