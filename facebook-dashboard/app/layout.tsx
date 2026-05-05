import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Toaster } from "sonner";
import { AuthProvider } from "@/contexts/AuthContext";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Valina-Bot - L'agent IA pour ta page Messenger Facebook",
  description:
    "Réponds aux messages clients 24/7 sur Messenger, convertis en commandes Mvola, Orange Money, Airtel Money. Setup en 10 min, 7 jours d'essai gratuit. Pour commerçants malgaches et francophones.",
  openGraph: {
    title: "Valina-Bot - L'agent IA qui répond à tes clients sur Messenger 24/7",
    description:
      "Transforme ta page Facebook Messenger en machine à vente automatique. Setup en 10 min, essai gratuit 7 jours.",
    locale: "fr_FR",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <AuthProvider>
          {children}
          <Toaster richColors position="top-right" />
        </AuthProvider>
      </body>
    </html>
  );
}
