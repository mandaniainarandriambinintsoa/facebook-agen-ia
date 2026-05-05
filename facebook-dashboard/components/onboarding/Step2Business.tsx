"use client";

import { useState } from "react";
import { ArrowRight, ArrowLeft } from "lucide-react";

const BUSINESS_TYPES = [
  { id: "ecommerce", label: "Mode et accessoires", desc: "Vêtements, chaussures, bijoux", emoji: "👕" },
  { id: "food", label: "Restauration", desc: "Resto, fast-food, livraison repas", emoji: "🍽️" },
  { id: "electronics", label: "Électronique", desc: "Téléphones, accessoires tech", emoji: "📱" },
  { id: "beauty", label: "Beauté et soin", desc: "Salon, cosmétiques, RDV", emoji: "💄" },
  { id: "service", label: "Services", desc: "Coaching, formation, conseil", emoji: "🎓" },
  { id: "other", label: "Autre commerce", desc: "Tu nous diras plus tard", emoji: "📦" },
];

interface Step2Props {
  initial?: string;
  onBack: () => void;
  onNext: (botType: string) => void;
}

export function Step2Business({ initial, onBack, onNext }: Step2Props) {
  const [selected, setSelected] = useState<string | null>(initial || null);

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-12">
        <span className="font-mono text-xs text-[#B7481E] uppercase tracking-widest mb-4 block">
          01 — Type de commerce
        </span>
        <h2 className="font-display text-3xl md:text-5xl text-[#1A1614] tracking-tight leading-[1.05] mb-4">
          Quel est ton <span className="italic text-[#B7481E]">métier</span> ?
        </h2>
        <p className="text-[#1A1614]/70 leading-relaxed">
          On adapte le ton et les exemples du bot selon le type de commerce. Tu peux changer plus tard.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-10">
        {BUSINESS_TYPES.map((b) => {
          const isSelected = selected === b.id;
          return (
            <button
              key={b.id}
              onClick={() => setSelected(b.id)}
              className={`group text-left p-5 rounded-2xl border-2 transition-all duration-200 ${
                isSelected
                  ? "border-[#B7481E] bg-[#FBF6EE] shadow-md"
                  : "border-[#1A1614]/10 hover:border-[#1A1614]/30 bg-[#FBF6EE]/50"
              }`}
            >
              <span className="text-3xl block mb-3">{b.emoji}</span>
              <h3 className={`font-display text-lg mb-1 leading-tight ${isSelected ? "text-[#B7481E]" : "text-[#1A1614]"}`}>
                {b.label}
              </h3>
              <p className="text-xs text-[#1A1614]/60 leading-relaxed">{b.desc}</p>
            </button>
          );
        })}
      </div>

      <div className="flex items-center justify-between pt-6 border-t border-[#1A1614]/10">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-2 text-[#1A1614]/70 hover:text-[#1A1614] text-sm"
        >
          <ArrowLeft className="h-4 w-4" />
          Précédent
        </button>

        <button
          onClick={() => selected && onNext(selected)}
          disabled={!selected}
          className="group inline-flex items-center gap-3 rounded-full bg-[#1A1614] text-[#FBF6EE] pl-6 pr-2 py-2 text-base font-medium hover:bg-[#B7481E] transition-all disabled:opacity-30 disabled:cursor-not-allowed"
        >
          Suivant
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-[#F4B83A] text-[#1A1614] group-hover:translate-x-0.5 transition-transform">
            <ArrowRight className="h-4 w-4" />
          </span>
        </button>
      </div>
    </div>
  );
}
