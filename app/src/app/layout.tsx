import type { Metadata, Viewport } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "QuantumEAR — AI Voice Deepfake Detection",
  description: "Hybrid quantum-classical system that detects AI-generated voice deepfakes.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover",
  themeColor: "#000000",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <head>
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="color-scheme" content="dark light" />
      </head>
      <body style={{ fontFamily: "var(--font-sans)", minHeight: "100vh" }}>
        <Navbar />
        <main
          style={{
            width: "100%",
            maxWidth: 520,
            margin: "0 auto",
            paddingTop: "calc(var(--safe-top, 0px) + 12px)",
            paddingLeft: 16,
            paddingRight: 16,
            paddingBottom: "calc(84px + var(--safe-bottom, 0px))",
          }}
        >
          {children}
        </main>
      </body>
    </html>
  );
}
