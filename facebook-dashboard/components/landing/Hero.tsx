import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { ChatMockup } from "./ChatMockup";
import { SunBurst } from "./LambaPattern";

export function Hero() {
  return (
    <section className="relative pt-32 pb-16 md:pt-40 md:pb-24 overflow-hidden bg-[#FBF6EE]">
      {/* Background atmosphere */}
      <div
        aria-hidden
        className="absolute -top-40 -left-40 w-[500px] h-[500px] rounded-full bg-[#F4B83A]/15 blur-3xl"
      />
      <div
        aria-hidden
        className="absolute top-20 -right-32 w-[450px] h-[450px] rounded-full bg-[#B7481E]/10 blur-3xl"
      />
      <SunBurst
        size={280}
        color="#B7481E"
        opacity={0.15}
        className="absolute -bottom-32 -right-32 hidden md:block"
      />

      <div className="relative max-w-7xl mx-auto px-5 sm:px-8 grid md:grid-cols-12 gap-8 md:gap-12 items-center">
        {/* Left side - editorial text */}
        <div className="md:col-span-7 relative z-10">
          {/* Kicker */}
          <div className="inline-flex items-center gap-2 mb-8">
            <span className="h-px w-10 bg-[#B7481E]" />
            <span className="font-display italic text-[#B7481E] text-sm tracking-wide">
              Made in Madagascar, pour les commerçants d&apos;ici
            </span>
          </div>

          {/* Headline editorial */}
          <h1 className="font-display text-[2.75rem] sm:text-6xl md:text-7xl lg:text-[5.5rem] leading-[0.95] text-[#1A1614] tracking-tight">
            Vendre
            <br />
            <span className="italic text-[#B7481E]">pendant</span>{" "}
            que tu
            <br />
            dors.
          </h1>

          {/* Sub */}
          <p className="mt-8 text-lg md:text-xl text-[#1A1614]/75 max-w-lg leading-relaxed">
            Valina-Bot répond aux messages de tes clients sur{" "}
            <span className="text-[#1A1614] font-medium">Messenger Facebook</span>{" "}
            24h/24. Il comprend le malgache, prend les commandes en{" "}
            <span className="font-display italic text-[#B7481E]">Mvola</span>, et te laisse dormir tranquille.
          </p>

          {/* CTAs */}
          <div className="mt-10 flex flex-col sm:flex-row items-start sm:items-center gap-4">
            <Link
              href="/login"
              className="group inline-flex items-center gap-3 rounded-full bg-[#1A1614] text-[#FBF6EE] pl-6 pr-2 py-2 text-base font-medium hover:bg-[#B7481E] transition-all duration-300"
            >
              Démarrer l&apos;essai gratuit
              <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-[#F4B83A] text-[#1A1614] group-hover:translate-x-0.5 transition-transform">
                <ArrowRight className="h-4 w-4" />
              </span>
            </Link>
            <a
              href="#story"
              className="text-[#1A1614]/70 hover:text-[#1A1614] underline underline-offset-4 decoration-[#B7481E] decoration-2 transition-colors text-base"
            >
              Voir le constat
            </a>
          </div>

          {/* Trust line */}
          <p className="mt-8 text-sm text-[#1A1614]/60 font-medium">
            7 jours gratuits · Sans carte bancaire · Mise en service en 10 min
          </p>
        </div>

        {/* Right side - mockup */}
        <div className="md:col-span-5 relative z-10 flex justify-center md:justify-end items-center">
          <ChatMockup />
        </div>
      </div>

      {/* Bottom marquee bar */}
      <div className="relative mt-16 md:mt-24 overflow-hidden border-t border-b border-[#1A1614]/10 bg-[#1A1614]">
        <div className="flex gap-12 py-3 whitespace-nowrap animate-[marquee_30s_linear_infinite] text-[#FBF6EE] font-display italic">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex gap-12 items-center">
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
