"use client";

import Link from "next/link";
import { Check, ArrowRight, Settings, MessageCircle, Package } from "lucide-react";
import { SunBurst } from "@/components/landing/LambaPattern";

interface StepDoneProps {
  pageName: string;
}

const NEXT_ACTIONS = [
  {
    icon: MessageCircle,
    label: "Voir les conversations",
    desc: "Suivre les messages que ton bot a traités",
    href: "/dashboard/messages",
  },
  {
    icon: Package,
    label: "Gérer ton catalogue",
    desc: "Ajouter, modifier, supprimer des produits",
    href: "/dashboard/products",
  },
  {
    icon: Settings,
    label: "Configurer le bot",
    desc: "Custom prompt, ton, automatisations",
    href: "/dashboard/config",
  },
];

export function StepDone({ pageName }: StepDoneProps) {
  return (
    <div className="max-w-3xl mx-auto text-center relative">
      <SunBurst
        size={400}
        color="#1877F2"
        opacity={0.1}
        className="absolute -top-24 left-1/2 -translate-x-1/2 -z-10"
      />

      <div className="relative">
        <div className="inline-flex h-20 w-20 items-center justify-center rounded-full bg-[#16A34A] text-[#F7F8FA] mb-8">
          <Check className="h-10 w-10" />
        </div>

        <span className="font-mono text-xs text-[#16A34A] uppercase tracking-widest mb-4 block">
          Activé
        </span>

        <h1 className="text-4xl md:text-6xl text-[#1C1E21] tracking-tight leading-[1.05] mb-6">
          Valina-Bot répond
          <br />
          sur <span className="italic text-[#1877F2]">{pageName}</span>.
        </h1>

        <p className="text-lg text-[#1C1E21]/70 leading-relaxed mb-12 max-w-xl mx-auto">
          Tes clients qui envoient un message à ta page reçoivent maintenant une
          réponse en moins de 5 secondes, 24h/24. Tu peux dormir.
        </p>

        {/* Next actions */}
        <div className="grid sm:grid-cols-3 gap-4 mb-10">
          {NEXT_ACTIONS.map((a) => (
            <Link
              key={a.href}
              href={a.href}
              className="group text-left p-5 rounded-2xl border border-[#1C1E21]/10 bg-[#F7F8FA]/50 hover:border-[#1877F2]/40 hover:bg-[#F7F8FA] transition-all"
            >
              <a.icon className="h-5 w-5 text-[#1877F2] mb-3" />
              <h3 className="text-base text-[#1C1E21] mb-1 leading-tight">
                {a.label}
              </h3>
              <p className="text-xs text-[#1C1E21]/60 leading-relaxed">{a.desc}</p>
            </Link>
          ))}
        </div>

        <Link
          href="/dashboard"
          className="group inline-flex items-center gap-3 rounded-full bg-[#1C1E21] text-[#F7F8FA] pl-7 pr-2 py-2.5 text-base font-medium hover:bg-[#1877F2] transition-all"
        >
          Aller au dashboard
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-[#F4B83A] text-[#1C1E21] group-hover:translate-x-0.5 transition-transform">
            <ArrowRight className="h-4 w-4" />
          </span>
        </Link>

        <p className="mt-12 text-xs text-[#1C1E21]/40 max-w-md mx-auto">
          Tu reçois le premier email récapitulatif demain matin. Si quelque chose ne va pas,
          écris à <a href="mailto:contact@manda-ia.com" className="underline">contact@manda-ia.com</a>.
        </p>
      </div>
    </div>
  );
}
