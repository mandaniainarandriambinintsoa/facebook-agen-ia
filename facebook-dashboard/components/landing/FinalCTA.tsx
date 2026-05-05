import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { LambaPattern } from "./LambaPattern";

export function FinalCTA() {
  return (
    <section className="py-20 md:py-28 bg-[#FBF6EE]">
      <div className="max-w-7xl mx-auto px-5 sm:px-8">
        <div className="relative overflow-hidden rounded-3xl bg-[#B7481E] text-[#FBF6EE] px-6 py-16 md:px-16 md:py-24">
          <LambaPattern color="#FBF6EE" opacity={0.08} />

          <div className="relative max-w-3xl">
            <span className="font-mono text-xs text-[#F4B83A] uppercase tracking-widest mb-6 block">
              Prêt ? Allez.
            </span>

            <h2 className="font-display text-4xl md:text-6xl lg:text-7xl tracking-tight leading-[1.0]">
              Mets Valina-Bot
              <br />
              <span className="italic">sur ta page</span> en
              <br />
              dix minutes.
            </h2>

            <p className="mt-8 text-lg md:text-xl text-[#FBF6EE]/85 max-w-xl leading-relaxed">
              Pas de carte bancaire, pas d&apos;engagement. Tu testes pendant 7
              jours, tu décides après. La seule chose que tu risques, c&apos;est
              de mieux dormir.
            </p>

            <div className="mt-10 flex flex-col sm:flex-row items-start sm:items-center gap-5">
              <Link
                href="/login"
                className="group inline-flex items-center gap-3 rounded-full bg-[#FBF6EE] text-[#1A1614] pl-7 pr-2 py-2 text-base font-medium hover:bg-[#F4B83A] transition-all duration-300"
              >
                Démarrer l&apos;essai gratuit
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-[#1A1614] text-[#FBF6EE] group-hover:translate-x-0.5 transition-transform">
                  <ArrowRight className="h-4 w-4" />
                </span>
              </Link>
              <a
                href="mailto:contact@manda-ia.com"
                className="text-[#FBF6EE]/85 hover:text-[#FBF6EE] underline underline-offset-4 decoration-[#F4B83A] decoration-2"
              >
                Parler à Manda d&apos;abord
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
