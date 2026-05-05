"use client";

import { useState } from "react";
import Link from "next/link";
import { Check } from "lucide-react";
import { Button } from "@/components/ui/button";

type Region = "mada" | "afrique" | "europe";

const REGIONS: { id: Region; label: string; currency: string }[] = [
  { id: "mada", label: "Madagascar", currency: "MGA" },
  { id: "afrique", label: "Afrique francophone", currency: "FCFA" },
  { id: "europe", label: "France · Europe", currency: "EUR" },
];

const PLANS = {
  starter: {
    name: "Starter",
    description: "Pour démarrer et valider",
    prices: { mada: "30 000", afrique: "6 000", europe: "25" },
    features: [
      "1 page Facebook + WhatsApp + Instagram",
      "1 000 messages traités / mois",
      "Catalogue jusqu'à 100 produits",
      "Détection prospects + commandes",
      "Bilingue Français + Malgache",
      "Support par email",
    ],
    cta: "Démarrer l'essai gratuit",
    highlighted: false,
  },
  pro: {
    name: "Pro",
    description: "Pour scaler ton activité",
    prices: { mada: "80 000", afrique: "15 000", europe: "60" },
    features: [
      "Jusqu'à 3 pages connectées",
      "10 000 messages traités / mois",
      "Catalogue illimité",
      "Custom prompt avancé",
      "Notifs Telegram prospects chauds",
      "Auto-reply commentaires",
      "Support prioritaire WhatsApp",
    ],
    cta: "Démarrer l'essai gratuit",
    highlighted: true,
  },
};

export function Pricing() {
  const [region, setRegion] = useState<Region>("mada");
  const currency = REGIONS.find((r) => r.id === region)!.currency;

  return (
    <section id="pricing" className="py-20 md:py-28 bg-slate-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 tracking-tight">
            Un tarif honnête, sans surprise
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            Choisis ta région. Tu peux changer de plan à tout moment.
          </p>
        </div>

        <div className="flex justify-center mb-10">
          <div className="inline-flex rounded-full border border-slate-200 bg-white p-1 shadow-sm">
            {REGIONS.map((r) => (
              <button
                key={r.id}
                onClick={() => setRegion(r.id)}
                className={`px-4 sm:px-5 py-2 text-sm font-medium rounded-full transition ${
                  region === r.id
                    ? "bg-slate-900 text-white shadow"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                {r.label}
              </button>
            ))}
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {(Object.entries(PLANS) as [keyof typeof PLANS, typeof PLANS.starter][]).map(
            ([key, plan]) => (
              <div
                key={key}
                className={`relative rounded-2xl p-8 ${
                  plan.highlighted
                    ? "bg-gradient-to-br from-slate-900 to-slate-800 text-white shadow-2xl ring-2 ring-amber-400"
                    : "bg-white border border-slate-200"
                }`}
              >
                {plan.highlighted && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 inline-flex items-center gap-1 rounded-full bg-amber-500 text-white text-xs font-semibold px-3 py-1">
                    Recommandé
                  </span>
                )}

                <h3
                  className={`text-2xl font-bold ${
                    plan.highlighted ? "text-white" : "text-slate-900"
                  }`}
                >
                  {plan.name}
                </h3>
                <p
                  className={`mt-1 text-sm ${
                    plan.highlighted ? "text-slate-300" : "text-slate-600"
                  }`}
                >
                  {plan.description}
                </p>

                <div className="mt-6 flex items-baseline gap-2">
                  <span
                    className={`text-4xl font-bold ${
                      plan.highlighted ? "text-white" : "text-slate-900"
                    }`}
                  >
                    {plan.prices[region]}
                  </span>
                  <span
                    className={`text-sm font-medium ${
                      plan.highlighted ? "text-slate-300" : "text-slate-500"
                    }`}
                  >
                    {currency} / mois
                  </span>
                </div>

                <ul className="mt-6 space-y-3">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm">
                      <Check
                        className={`h-5 w-5 flex-shrink-0 ${
                          plan.highlighted ? "text-emerald-400" : "text-emerald-600"
                        }`}
                      />
                      <span
                        className={
                          plan.highlighted ? "text-slate-200" : "text-slate-700"
                        }
                      >
                        {f}
                      </span>
                    </li>
                  ))}
                </ul>

                <Button
                  asChild
                  size="lg"
                  className={`w-full mt-8 ${
                    plan.highlighted
                      ? "bg-amber-500 hover:bg-amber-600 text-white"
                      : "bg-slate-900 hover:bg-slate-800 text-white"
                  }`}
                >
                  <Link href="/login">{plan.cta}</Link>
                </Button>
              </div>
            )
          )}
        </div>

        <p className="text-center mt-8 text-sm text-slate-500">
          7 jours gratuits sur tous les plans · Sans carte bancaire · Annulable
          en 1 clic
        </p>
      </div>
    </section>
  );
}
