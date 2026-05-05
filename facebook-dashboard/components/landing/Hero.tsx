import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";
import { ChatMockup } from "./ChatMockup";

export function Hero() {
  return (
    <section className="relative pt-32 pb-20 md:pt-40 md:pb-28 overflow-hidden">
      <div
        aria-hidden
        className="absolute inset-0 -z-10 bg-gradient-to-b from-slate-50 via-white to-white"
      />
      <div
        aria-hidden
        className="absolute -top-24 left-1/2 -translate-x-1/2 -z-10 h-96 w-[60rem] rounded-full bg-emerald-500/10 blur-3xl"
      />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 grid md:grid-cols-2 gap-12 items-center">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 mb-6">
            <Sparkles className="h-3.5 w-3.5" />
            Setup en 10 minutes, sans code
          </div>

          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-slate-900 leading-tight">
            Tes clients posent leur question{" "}
            <span className="bg-gradient-to-r from-emerald-600 to-amber-500 bg-clip-text text-transparent">
              pendant que tu dors.
            </span>
          </h1>

          <p className="mt-6 text-lg text-slate-600 leading-relaxed max-w-xl">
            Valina-Bot répond, vend et collecte les commandes 24/7 sur tes pages
            Facebook, Instagram et WhatsApp. L&apos;agent IA qui transforme ta
            messagerie en machine à vente automatique.
          </p>

          <div className="mt-8 flex flex-col sm:flex-row gap-3">
            <Button
              asChild
              size="lg"
              className="bg-amber-500 hover:bg-amber-600 text-white shadow-lg shadow-amber-500/20"
            >
              <Link href="/login">
                Démarrer l&apos;essai gratuit
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button
              asChild
              variant="outline"
              size="lg"
              className="border-slate-300"
            >
              <a href="#how">Voir comment ça marche</a>
            </Button>
          </div>

          <p className="mt-4 text-sm text-slate-500">
            7 jours gratuits · Pas de carte bancaire · Annulable en 1 clic
          </p>
        </div>

        <div className="relative flex justify-center md:justify-end">
          <ChatMockup />
        </div>
      </div>
    </section>
  );
}
