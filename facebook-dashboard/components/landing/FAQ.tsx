"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";

const QUESTIONS = [
  {
    q: "Combien de temps pour configurer Valina-Bot ?",
    a: "10 minutes en moyenne. Tu te connectes via Facebook OAuth, tu uploades ton catalogue Excel, tu valides un message test, et c'est en ligne. Aucune ligne de code à écrire.",
  },
  {
    q: "Mes données sont-elles sécurisées ?",
    a: "Oui. Notre infrastructure est hébergée en UE, conforme RGPD. Pas de transfert de données vers les USA. Tu peux à tout moment exporter ou supprimer toutes tes données depuis le dashboard.",
  },
  {
    q: "Que se passe-t-il si le bot ne sait pas répondre ?",
    a: "Il escalade automatiquement vers toi avec une notification Telegram. Tu reprends la main sur la conversation depuis le dashboard ou tu enrichis ta base de connaissances pour la prochaine fois.",
  },
  {
    q: "Et Instagram, WhatsApp ?",
    a: "Pour le moment, Valina-Bot fonctionne uniquement sur Messenger Facebook (pages business). L'intégration Instagram DMs et WhatsApp Business arrive sur la roadmap. Si tu veux être prévenu, dis-le-moi via contact@manda-ia.com.",
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
    q: "Avez-vous une version FCFA / Mvola ?",
    a: "Oui. Paiement en MGA via Mvola, Orange Money ou Airtel Money à Madagascar. En FCFA via Wave et Orange Money en Afrique de l'Ouest. CB pour la France et l'Europe.",
  },
  {
    q: "Peut-on tester avant de payer ?",
    a: "Oui. 7 jours d'essai gratuit, sans carte bancaire. Tu accèdes à toutes les fonctionnalités du plan Pro pendant l'essai. Si tu ne souscris pas, ton compte est mis en pause sans frais.",
  },
];

export function FAQ() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section id="faq" className="py-20 md:py-28 bg-white">
      <div className="max-w-3xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 tracking-tight">
            Questions fréquentes
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            Tout ce que tu te demandes avant de tester.
          </p>
        </div>

        <div className="divide-y divide-slate-200 border-y border-slate-200">
          {QUESTIONS.map((item, i) => {
            const isOpen = open === i;
            return (
              <div key={i}>
                <button
                  onClick={() => setOpen(isOpen ? null : i)}
                  className="w-full flex items-center justify-between gap-4 py-5 text-left hover:text-emerald-700 transition"
                >
                  <span className="font-semibold text-slate-900">{item.q}</span>
                  <ChevronDown
                    className={`h-5 w-5 text-slate-400 flex-shrink-0 transition-transform ${
                      isOpen ? "rotate-180" : ""
                    }`}
                  />
                </button>
                {isOpen && (
                  <div className="pb-5 text-slate-600 leading-relaxed">
                    {item.a}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <p className="text-center mt-10 text-slate-600">
          Une autre question ?{" "}
          <a
            href="mailto:contact@manda-ia.com"
            className="font-semibold text-emerald-700 underline"
          >
            Écris-moi à contact@manda-ia.com
          </a>
        </p>
      </div>
    </section>
  );
}
