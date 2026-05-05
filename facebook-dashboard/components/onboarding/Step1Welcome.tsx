"use client";

import { ArrowRight } from "lucide-react";

interface Step1Props {
  pageName: string;
  onNext: () => void;
  onSkip: () => void;
}

export function Step1Welcome({ pageName, onNext, onSkip }: Step1Props) {
  return (
    <div className="max-w-2xl mx-auto text-center">
      <span className="font-mono text-xs text-[#B7481E] uppercase tracking-widest mb-4 block">
        Bienvenue
      </span>

      <h1 className="font-display text-4xl md:text-6xl text-[#1A1614] tracking-tight leading-[1.05] mb-6">
        On va activer Valina-Bot
        <br />
        sur <span className="italic text-[#B7481E]">{pageName}</span>.
      </h1>

      <p className="text-lg text-[#1A1614]/70 leading-relaxed mb-10 max-w-xl mx-auto">
        Cinq petites étapes, environ dix minutes. À la fin, ton bot répond aux
        messages de tes clients en autonomie. Tu pourras tout modifier ensuite
        depuis ton dashboard.
      </p>

      <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
        <button
          onClick={onNext}
          className="group inline-flex items-center gap-3 rounded-full bg-[#1A1614] text-[#FBF6EE] pl-7 pr-2 py-2.5 text-base font-medium hover:bg-[#B7481E] transition-all duration-300"
        >
          Commencer la configuration
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-[#F4B83A] text-[#1A1614] group-hover:translate-x-0.5 transition-transform">
            <ArrowRight className="h-4 w-4" />
          </span>
        </button>

        <button
          onClick={onSkip}
          className="text-[#1A1614]/60 hover:text-[#1A1614] underline underline-offset-4 decoration-[#1A1614]/30 text-sm transition-colors"
        >
          Plus tard, j&apos;explore le dashboard d&apos;abord
        </button>
      </div>

      <p className="mt-12 text-xs text-[#1A1614]/40 max-w-md mx-auto">
        Tu peux quitter à tout moment et reprendre où tu en étais. Les étapes
        sont sauvegardées au fur et à mesure.
      </p>
    </div>
  );
}
