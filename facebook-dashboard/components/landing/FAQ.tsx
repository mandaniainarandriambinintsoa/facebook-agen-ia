"use client";

import { useState } from "react";
import { StepBadge } from "./StepBadge";

const QUESTIONS = [
  {
    q: "Combien de temps pour configurer Valina-Bot ?",
    a: "10 minutes en moyenne. Tu te connectes via Facebook OAuth, tu uploades ton catalogue Excel, tu valides un message test, et c'est en ligne. Aucune ligne de code à écrire.",
  },
  {
    q: "Mes données sont-elles sécurisées ?",
    a: "Oui. Notre infrastructure est hébergée en Europe, conforme RGPD. Pas de transfert de données vers les USA. Tu peux à tout moment exporter ou supprimer toutes tes données depuis le dashboard.",
  },
  {
    q: "Que se passe-t-il si le bot ne sait pas répondre ?",
    a: "Il escalade automatiquement vers toi avec une notification Telegram. Tu reprends la main sur la conversation depuis le dashboard ou tu enrichis ta base de connaissances pour la prochaine fois.",
  },
  {
    q: "Et Instagram, WhatsApp ?",
    a: "Pour le moment, Valina-Bot fonctionne uniquement sur Messenger Facebook. L'intégration Instagram DMs et WhatsApp Business arrive sur la roadmap. Pour être prévenu en priorité, écris à contact@valina-bot.com.",
  },
  {
    q: "Puis-je personnaliser le ton du bot ?",
    a: "Bien sûr. Dans Configuration > Custom Prompt, tu peux dicter le ton (familier, formel, expressions préférées). Le bot l'utilise sur toutes ses réponses.",
  },
  {
    q: "Comment se passe la résiliation ?",
    a: "En 1 clic depuis le dashboard. Pas de période d'engagement, pas de frais cachés. Tes données restent disponibles 30 jours après résiliation au cas où tu changerais d'avis.",
  },
  {
    q: "Et le paiement Mvola, Orange Money ?",
    a: "À Madagascar, tu paies en MGA via Mvola, Orange Money ou Airtel Money depuis le dashboard. En Afrique francophone, par Wave et Orange Money. En France et Europe, par carte bancaire.",
  },
  {
    q: "Peut-on tester avant de payer ?",
    a: "Oui. 7 jours d'essai gratuit, sans carte bancaire requise. Tu accèdes à toutes les fonctionnalités du plan Pro pendant l'essai. Si tu ne souscris pas, ton compte est mis en pause sans frais.",
  },
];

export function FAQ() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section id="faq" className="py-24 md:py-36 bg-[#F0F2F5]">
      <div className="max-w-6xl mx-auto px-5 sm:px-8">
        <div className="grid md:grid-cols-12 gap-10 md:gap-20">
          {/* Left: title sticky */}
          <div className="md:col-span-4">
            <div className="md:sticky md:top-32">
              <div className="mb-6">
                <StepBadge>Questions</StepBadge>
              </div>
              <h2 className="text-4xl md:text-5xl text-[#1C1E21] tracking-[-0.02em] leading-[1.05]">
                Avant de{" "}
                <em className="not-italic italic text-[#1877F2]">tester</em>
                <span className="text-[#1877F2]">.</span>
              </h2>
              <p className="mt-6 text-[#1C1E21]/70 leading-relaxed">
                Tout ce que tu te demandes probablement. Si une question manque,{" "}
                <a
                  href="mailto:contact@valina-bot.com"
                  className="underline underline-offset-4 decoration-[#1877F2] decoration-2 text-[#1C1E21] font-medium"
                >
                  écris-nous
                </a>
                .
              </p>
            </div>
          </div>

          {/* Right: questions */}
          <div className="md:col-span-8 divide-y divide-[#1C1E21]/15 border-y border-[#1C1E21]/15">
            {QUESTIONS.map((item, i) => {
              const isOpen = open === i;
              return (
                <article key={i}>
                  <button
                    onClick={() => setOpen(isOpen ? null : i)}
                    className="w-full flex items-start gap-6 py-6 text-left group"
                  >
                    <span className="font-mono text-[10px] text-[#1877F2] uppercase tracking-[0.2em] pt-2 shrink-0">
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <span className="text-xl md:text-[1.625rem] text-[#1C1E21] flex-1 leading-tight tracking-[-0.01em] group-hover:text-[#1877F2] transition-colors">
                      {item.q}
                    </span>
                    <span
                      className={`mt-1.5 inline-flex h-7 w-7 items-center justify-center rounded-full border border-[#1C1E21]/30 text-[#1C1E21] shrink-0 transition-all duration-300 ${
                        isOpen ? "rotate-45 bg-[#1C1E21] text-[#F7F8FA] border-[#1C1E21]" : ""
                      }`}
                    >
                      <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                        <path
                          d="M5 1V9M1 5H9"
                          stroke="currentColor"
                          strokeWidth="1.5"
                          strokeLinecap="round"
                        />
                      </svg>
                    </span>
                  </button>
                  <div
                    className={`grid transition-all duration-300 ease-out ${
                      isOpen ? "grid-rows-[1fr] pb-6" : "grid-rows-[0fr]"
                    }`}
                  >
                    <div className="overflow-hidden">
                      <p className="text-[#1C1E21]/75 leading-relaxed pl-12 max-w-2xl">
                        {item.a}
                      </p>
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
