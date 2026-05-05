import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { LambaPattern } from "./LambaPattern";
import { DashedLine } from "./DashedLine";

export function FinalCTA() {
  return (
    <section className="py-24 md:py-32 bg-[#FAF9F5]">
      <div className="max-w-6xl mx-auto px-5 sm:px-8">
        <div className="relative overflow-hidden rounded-[2rem] bg-[#B7481E] text-[#FAF9F5] px-8 py-20 md:px-20 md:py-28">
          <LambaPattern color="#FAF9F5" opacity={0.07} />

          <div className="relative max-w-3xl">
            <span className="font-mono text-[11px] text-[#F4B83A] uppercase tracking-[0.2em] mb-6 block">
              Prêt ? Allez.
            </span>

            <h2 className="font-display text-4xl md:text-6xl lg:text-7xl tracking-[-0.02em] leading-[0.95]">
              Mets Valina-Bot
              <br />
              <em className="not-italic font-display italic">sur ta page</em> en
              <br />
              dix minutes<span className="text-[#F4B83A]">.</span>
            </h2>

            <p className="mt-8 text-lg md:text-xl text-[#FAF9F5]/85 max-w-xl leading-relaxed">
              Pas de carte bancaire, pas d&apos;engagement. Tu testes pendant 7
              jours, tu décides après. La seule chose que tu risques, c&apos;est
              de mieux dormir.
            </p>

            <div className="mt-10 flex flex-col sm:flex-row items-start sm:items-center gap-5 relative">
              <Link
                href="/login"
                className="group inline-flex items-center gap-3 rounded-full bg-[#FAF9F5] text-[#0F0E0C] pl-7 pr-2 py-2.5 text-base font-medium hover:bg-[#F4B83A] transition-all duration-300"
              >
                Démarrer l&apos;essai gratuit
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-[#0F0E0C] text-[#FAF9F5] group-hover:translate-x-0.5 transition-transform">
                  <ArrowRight className="h-4 w-4" />
                </span>
              </Link>
              <a
                href="mailto:contact@manda-ia.com"
                className="text-[#FAF9F5]/85 hover:text-[#FAF9F5] underline underline-offset-4 decoration-[#F4B83A] decoration-2"
              >
                Parler à Manda d&apos;abord
              </a>

              {/* Decorative dashed arrow pointing to CTA */}
              <DashedLine
                variant="hero-cta"
                className="absolute hidden md:block -top-32 -right-8 w-32 h-40 opacity-50"
                color="#FAF9F5"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
