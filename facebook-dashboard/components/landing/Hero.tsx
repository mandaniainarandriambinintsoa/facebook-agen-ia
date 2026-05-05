import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { ChatMockup } from "./ChatMockup";
import { DashedLine } from "./DashedLine";

export function Hero() {
  return (
    <section className="relative pt-28 pb-12 md:pt-36 md:pb-20 overflow-hidden bg-[#FAF9F5]">
      {/* Background atmosphere */}
      <div
        aria-hidden
        className="absolute -top-32 -left-32 w-[500px] h-[500px] rounded-full bg-[#F4B83A]/10 blur-3xl pointer-events-none"
      />
      <div
        aria-hidden
        className="absolute top-32 -right-40 w-[450px] h-[450px] rounded-full bg-[#B7481E]/8 blur-3xl pointer-events-none"
      />

      <div className="relative max-w-6xl mx-auto px-5 sm:px-8">
        <div className="grid md:grid-cols-12 gap-6 md:gap-10 items-end">
          {/* Left : editorial headline */}
          <div className="md:col-span-7 relative z-10 pt-12 md:pt-20">
            <div className="inline-flex items-center gap-3 mb-8">
              <span className="h-px w-12 bg-[#0F0E0C]/40" />
              <span className="font-mono text-[11px] uppercase tracking-[0.2em] text-[#0F0E0C]/60">
                Made in Madagascar
              </span>
            </div>

            <h1 className="font-display text-[3rem] sm:text-6xl md:text-[5.5rem] lg:text-[6.5rem] leading-[0.9] text-[#0F0E0C] tracking-[-0.02em]">
              Vendre
              <br />
              <em className="not-italic font-display italic text-[#B7481E]">pendant</em> que tu
              <br />
              dors<span className="text-[#B7481E]">.</span>
            </h1>

            <p className="mt-8 text-lg md:text-xl text-[#0F0E0C]/75 max-w-md leading-relaxed">
              Valina-Bot répond aux messages de tes clients sur Messenger
              Facebook 24h/24. Il comprend le malgache, prend les commandes en{" "}
              <span className="font-display italic text-[#B7481E]">Mvola</span>, et te laisse dormir.
            </p>

            <div className="mt-10 flex flex-col sm:flex-row items-start sm:items-center gap-5">
              <Link
                href="/login"
                className="group inline-flex items-center gap-3 rounded-full bg-[#0F0E0C] text-[#FAF9F5] pl-7 pr-2 py-2.5 text-base font-medium hover:bg-[#B7481E] transition-all duration-300"
              >
                Démarrer l&apos;essai gratuit
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-[#F4B83A] text-[#0F0E0C] group-hover:translate-x-0.5 transition-transform">
                  <ArrowRight className="h-4 w-4" />
                </span>
              </Link>
              <a
                href="#story"
                className="text-[#0F0E0C]/70 hover:text-[#0F0E0C] underline underline-offset-4 decoration-[#B7481E] decoration-2 transition-colors"
              >
                Découvrir l&apos;histoire
              </a>
            </div>

            <p className="mt-6 text-sm text-[#0F0E0C]/55">
              7 jours gratuits · Sans carte bancaire · 10 min pour activer
            </p>
          </div>

          {/* Right : mockup */}
          <div className="md:col-span-5 relative z-10 flex justify-center md:justify-end items-end pt-8 md:pt-0">
            <ChatMockup />
          </div>
        </div>

        {/* Dashed line connecting headline to mockup (desktop only) */}
        <DashedLine
          variant="hero-cta"
          className="absolute hidden md:block top-[42%] left-[55%] w-[18%] h-[28%] -z-0 opacity-40"
          color="#0F0E0C"
        />
      </div>

      {/* Marquee bar */}
      <div className="relative mt-16 md:mt-24 overflow-hidden border-t border-b border-[#0F0E0C]/12 bg-[#0F0E0C]">
        <div
          className="flex gap-12 py-3.5 whitespace-nowrap text-[#FAF9F5] font-display italic text-lg"
          style={{ animation: "marquee 40s linear infinite" }}
        >
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex gap-12 items-center shrink-0">
              <span>Misy ihany ny taille M</span>
              <span className="text-[#F4B83A]">✦</span>
              <span>Mvola accepté</span>
              <span className="text-[#F4B83A]">✦</span>
              <span>Livraison Tana en 24h</span>
              <span className="text-[#F4B83A]">✦</span>
              <span>Réponse en 5 secondes</span>
              <span className="text-[#F4B83A]">✦</span>
              <span>Salama ô tompoko</span>
              <span className="text-[#F4B83A]">✦</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
