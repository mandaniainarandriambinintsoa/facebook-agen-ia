"use client";

import { useState } from "react";
import Link from "next/link";
import { StepBadge } from "./StepBadge";

type Region = "mada" | "afrique" | "europe";

const REGIONS: { id: Region; label: string; currency: string }[] = [
  { id: "mada", label: "Madagascar", currency: "MGA" },
  { id: "afrique", label: "Afrique francophone", currency: "FCFA" },
  { id: "europe", label: "France · Europe", currency: "EUR" },
];

const PLANS = {
  starter: {
    name: "Starter",
    tagline: "Pour démarrer et valider",
    prices: { mada: "30 000", afrique: "6 000", europe: "25" },
    features: [
      "1 page Facebook Messenger",
      "1 000 messages traités / mois",
      "Catalogue jusqu'à 100 produits",
      "Détection prospects + commandes",
      "Bilingue Français + Malgache",
      "Support par email",
    ],
    highlighted: false,
  },
  pro: {
    name: "Pro",
    tagline: "Pour scaler ton activité",
    prices: { mada: "80 000", afrique: "15 000", europe: "60" },
    features: [
      "Jusqu'à 3 pages Messenger",
      "10 000 messages traités / mois",
      "Catalogue illimité",
      "Custom prompt avancé",
      "Notifs Telegram prospects chauds",
      "Auto-reply commentaires",
      "Support prioritaire",
    ],
    highlighted: true,
  },
};

export function Pricing() {
  const [region, setRegion] = useState<Region>("mada");
  const currency = REGIONS.find((r) => r.id === region)!.currency;

  return (
    <section id="pricing" className="py-24 md:py-36 bg-[#F7F8FA]">
      <div className="max-w-5xl mx-auto px-5 sm:px-8">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <div className="mb-6">
            <StepBadge>Tarifs</StepBadge>
          </div>
          <h2 className="text-4xl md:text-5xl text-[#1C1E21] tracking-[-0.02em] leading-[1.05]">
            Un prix juste,{" "}
            <em className="not-italic italic text-[#1877F2]">honnête</em>,
            <br />
            sans surprise<span className="text-[#1877F2]">.</span>
          </h2>
          <p className="mt-6 text-[#1C1E21]/70 text-lg">
            Choisis ton marché. Tu peux changer de plan à tout moment.
          </p>
        </div>

        {/* Region toggle */}
        <div className="flex justify-center mb-12">
          <div className="inline-flex rounded-full border border-[#1C1E21]/15 bg-[#F7F8FA] p-1.5 shadow-sm">
            {REGIONS.map((r) => (
              <button
                key={r.id}
                onClick={() => setRegion(r.id)}
                className={`px-4 sm:px-6 py-2.5 text-sm font-medium rounded-full transition-all duration-200 ${
                  region === r.id
                    ? "bg-[#1C1E21] text-[#F7F8FA] shadow"
                    : "text-[#1C1E21]/60 hover:text-[#1C1E21]"
                }`}
              >
                {r.label}
              </button>
            ))}
          </div>
        </div>

        {/* Plans */}
        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {(Object.entries(PLANS) as [keyof typeof PLANS, typeof PLANS.starter][]).map(
            ([key, plan]) => (
              <article
                key={key}
                className={`relative rounded-3xl p-8 md:p-10 ${
                  plan.highlighted
                    ? "bg-[#1C1E21] text-[#F7F8FA] shadow-2xl"
                    : "bg-[#F0F2F5] text-[#1C1E21] border border-[#1C1E21]/10"
                }`}
              >
                {plan.highlighted && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 inline-flex items-center rounded-full bg-[#F4B83A] text-[#1C1E21] text-[11px] font-medium px-4 py-1.5 font-mono uppercase tracking-[0.2em]">
                    Recommandé
                  </span>
                )}

                <div className="flex items-baseline justify-between mb-6">
                  <h3
                    className={`text-3xl tracking-[-0.01em] ${
                      plan.highlighted ? "text-[#F7F8FA]" : "text-[#1C1E21]"
                    }`}
                  >
                    {plan.name}
                  </h3>
                  <span
                    className={`font-mono text-[10px] uppercase tracking-[0.2em] ${
                      plan.highlighted ? "text-[#F4B83A]" : "text-[#1877F2]"
                    }`}
                  >
                    {plan.tagline}
                  </span>
                </div>

                <div className="mb-8">
                  <div className="flex items-baseline gap-2 mb-2">
                    <span
                      className={`text-5xl md:text-6xl tracking-[-0.02em] ${
                        plan.highlighted ? "text-[#F7F8FA]" : "text-[#1C1E21]"
                      }`}
                    >
                      {plan.prices[region]}
                    </span>
                    <span
                      className={`text-lg ${
                        plan.highlighted ? "text-[#F7F8FA]/70" : "text-[#1C1E21]/60"
                      }`}
                    >
                      {currency}
                    </span>
                  </div>
                  <span
                    className={`text-sm ${
                      plan.highlighted ? "text-[#F7F8FA]/60" : "text-[#1C1E21]/60"
                    }`}
                  >
                    par mois
                  </span>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-3 text-sm">
                      <span
                        className={`italic mt-0.5 ${
                          plan.highlighted ? "text-[#F4B83A]" : "text-[#1877F2]"
                        }`}
                      >
                        ✓
                      </span>
                      <span
                        className={
                          plan.highlighted ? "text-[#F7F8FA]/85" : "text-[#1C1E21]/80"
                        }
                      >
                        {f}
                      </span>
                    </li>
                  ))}
                </ul>

                <Link
                  href="/login"
                  className={`block w-full text-center rounded-full px-6 py-3.5 text-base font-medium transition-all duration-300 ${
                    plan.highlighted
                      ? "bg-[#F4B83A] text-[#1C1E21] hover:bg-[#FFE9A8]"
                      : "bg-[#1C1E21] text-[#F7F8FA] hover:bg-[#1877F2]"
                  }`}
                >
                  Démarrer l&apos;essai gratuit
                </Link>
              </article>
            )
          )}
        </div>

        <p className="text-center mt-10 text-sm text-[#1C1E21]/55 font-medium">
          7 jours gratuits sur tous les plans · Sans carte bancaire · Annulable en 1 clic
        </p>
      </div>
    </section>
  );
}
