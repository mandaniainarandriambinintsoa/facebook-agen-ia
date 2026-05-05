"use client";

import { useState, useEffect } from "react";
import { ArrowRight, ArrowLeft } from "lucide-react";

const TEMPLATES: Record<string, string> = {
  ecommerce:
    "Salama tompoko ! Bienvenue chez {{nom_page}}. Je suis l'assistant qui répond aux questions sur nos produits. Demande-moi les tailles, prix, dispo, livraison.",
  food:
    "Salama ! Bienvenue chez {{nom_page}}. Je peux te renseigner sur nos plats, horaires, livraison et réservations. Que souhaites-tu commander ?",
  electronics:
    "Bonjour ! Bienvenue sur la page {{nom_page}}. Pose-moi tes questions sur nos téléphones et accessoires : modèle, prix, dispo, garantie.",
  beauty:
    "Salama tompoko ! Bienvenue chez {{nom_page}}. Je peux te renseigner sur nos prestations, tarifs, prendre tes RDV. Comment puis-je t'aider ?",
  service:
    "Bonjour ! Bienvenue sur la page {{nom_page}}. Je suis là pour répondre à tes questions sur nos services et tarifs.",
  other:
    "Salama ! Bienvenue chez {{nom_page}}. Comment puis-je t'aider aujourd'hui ?",
};

interface Step3Props {
  pageName: string;
  botType: string;
  initial?: string;
  onBack: () => void;
  onNext: (welcomeMessage: string) => void;
}

export function Step3WelcomeMessage({
  pageName,
  botType,
  initial,
  onBack,
  onNext,
}: Step3Props) {
  const template = (TEMPLATES[botType] || TEMPLATES.other).replace(
    "{{nom_page}}",
    pageName
  );
  const [message, setMessage] = useState(initial || template);

  useEffect(() => {
    if (!initial) {
      setMessage((TEMPLATES[botType] || TEMPLATES.other).replace("{{nom_page}}", pageName));
    }
  }, [botType, pageName, initial]);

  const charCount = message.length;
  const charLimit = 500;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-10">
        <span className="font-mono text-xs text-[#1877F2] uppercase tracking-widest mb-4 block">
          02 — Message d&apos;accueil
        </span>
        <h2 className="text-3xl md:text-5xl text-[#1C1E21] tracking-tight leading-[1.05] mb-4">
          Comment ton bot accueille
          <br />
          tes <span className="italic text-[#1877F2]">clients</span> ?
        </h2>
        <p className="text-[#1C1E21]/70 leading-relaxed">
          Le premier message qu&apos;ils reçoivent quand ils ouvrent ta conversation.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 mb-10">
        {/* Editor */}
        <div>
          <label className="font-mono text-xs uppercase tracking-widest text-[#1C1E21]/60 mb-3 block">
            Texte
          </label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value.slice(0, charLimit))}
            rows={8}
            className="w-full p-4 rounded-2xl border border-[#1C1E21]/15 bg-[#F7F8FA] focus:border-[#1877F2] focus:outline-none focus:ring-2 focus:ring-[#1877F2]/20 transition-colors resize-none font-sans text-[#1C1E21] leading-relaxed"
          />
          <div className="flex items-center justify-between mt-2 text-xs">
            <span className="text-[#1C1E21]/40">
              Conseil : reste court (1-3 phrases). Les clients lisent vite.
            </span>
            <span
              className={`font-mono ${
                charCount > charLimit * 0.9 ? "text-[#1877F2]" : "text-[#1C1E21]/40"
              }`}
            >
              {charCount} / {charLimit}
            </span>
          </div>
        </div>

        {/* Preview */}
        <div>
          <label className="font-mono text-xs uppercase tracking-widest text-[#1C1E21]/60 mb-3 block">
            Aperçu Messenger
          </label>
          <div className="rounded-2xl bg-[#E4E6EA] p-4 min-h-[14rem]">
            <div className="flex items-center gap-3 mb-4 pb-3 border-b border-[#1C1E21]/10">
              <div className="h-9 w-9 rounded-full bg-gradient-to-br from-[#1877F2] to-[#F4B83A] flex items-center justify-center text-white font-semibold text-sm">
                {pageName.slice(0, 1).toUpperCase()}
              </div>
              <div>
                <p className="font-semibold text-[#1C1E21] text-sm">{pageName}</p>
                <p className="text-xs text-[#16A34A]">en ligne</p>
              </div>
            </div>
            <div className="flex justify-start">
              <div className="max-w-[85%] bg-white rounded-2xl rounded-tl-sm px-4 py-3 text-sm text-[#1C1E21] shadow-sm leading-relaxed">
                {message || (
                  <span className="text-[#1C1E21]/30 italic">
                    Le message apparaîtra ici...
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between pt-6 border-t border-[#1C1E21]/10">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-2 text-[#1C1E21]/70 hover:text-[#1C1E21] text-sm"
        >
          <ArrowLeft className="h-4 w-4" />
          Précédent
        </button>

        <button
          onClick={() => message.trim() && onNext(message.trim())}
          disabled={!message.trim()}
          className="group inline-flex items-center gap-3 rounded-full bg-[#1C1E21] text-[#F7F8FA] pl-6 pr-2 py-2 text-base font-medium hover:bg-[#1877F2] transition-all disabled:opacity-30"
        >
          Suivant
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-[#F4B83A] text-[#1C1E21] group-hover:translate-x-0.5 transition-transform">
            <ArrowRight className="h-4 w-4" />
          </span>
        </button>
      </div>
    </div>
  );
}
