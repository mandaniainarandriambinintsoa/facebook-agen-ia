"use client";

import { useState } from "react";
import { ArrowRight, Mail } from "lucide-react";
import { tenantApi } from "@/lib/api";

interface Step1ContactProps {
  initialEmail?: string;
  initialPhone?: string;
  onNext: () => void;
}

const FB_FALLBACK_RE = /@facebook\.com$/i;

export function Step1Contact({ initialEmail, initialPhone, onNext }: Step1ContactProps) {
  const startEmail = initialEmail && !FB_FALLBACK_RE.test(initialEmail) ? initialEmail : "";

  const [email, setEmail] = useState(startEmail);
  const [phone, setPhone] = useState(initialPhone || "");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isValidEmail = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);

  const handleSubmit = async () => {
    if (!isValidEmail) {
      setError("Adresse email invalide");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      await tenantApi("/contact", {
        method: "PATCH",
        body: JSON.stringify({ email, phone: phone || undefined }),
      });
      onNext();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erreur inconnue");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto">
      <div className="text-center mb-10">
        <span className="font-mono text-xs text-[#1877F2] uppercase tracking-widest mb-4 block">
          On reste en contact
        </span>
        <h2 className="text-3xl md:text-4xl text-[#1C1E21] tracking-tight leading-[1.05] mb-4">
          Ton email pour les <span className="italic text-[#1877F2]">conseils utiles</span>
        </h2>
        <p className="text-[#1C1E21]/70 leading-relaxed">
          On t&apos;envoie tes stats hebdo, des astuces pour optimiser ton bot et un check-in à 3 jours.
          Pas de spam, juste l&apos;essentiel.
        </p>
      </div>

      <div className="space-y-5 mb-8">
        <div>
          <label className="block text-sm font-medium text-[#1C1E21] mb-2">
            Email pro <span className="text-[#1877F2]">*</span>
          </label>
          <div className="relative">
            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-[#1C1E21]/40" />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="contact@taboutique.com"
              className="w-full pl-11 pr-4 py-3 rounded-xl border-2 border-[#1C1E21]/10 bg-white focus:border-[#1877F2] focus:outline-none transition-colors text-[#1C1E21]"
              autoFocus
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-[#1C1E21] mb-2">
            WhatsApp <span className="text-[#1C1E21]/50 text-xs font-normal">(optionnel — pour les alertes urgentes)</span>
          </label>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+261 32 00 000 00"
            className="w-full px-4 py-3 rounded-xl border-2 border-[#1C1E21]/10 bg-white focus:border-[#1877F2] focus:outline-none transition-colors text-[#1C1E21]"
          />
        </div>

        {error && (
          <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
            {error}
          </p>
        )}
      </div>

      <div className="flex justify-end">
        <button
          onClick={handleSubmit}
          disabled={!isValidEmail || submitting}
          className="group inline-flex items-center gap-3 rounded-full bg-[#1C1E21] text-[#F7F8FA] pl-6 pr-2 py-2 text-base font-medium hover:bg-[#1877F2] transition-all disabled:opacity-30 disabled:cursor-not-allowed"
        >
          {submitting ? "Enregistrement..." : "Continuer"}
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-[#F4B83A] text-[#1C1E21] group-hover:translate-x-0.5 transition-transform">
            <ArrowRight className="h-4 w-4" />
          </span>
        </button>
      </div>

      <p className="mt-8 text-xs text-[#1C1E21]/40 text-center">
        On ne partage jamais ton email. Tu peux te désabonner en 1 clic dans chaque mail.
      </p>
    </div>
  );
}
