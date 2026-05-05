"use client";

import { useState } from "react";
import { ArrowRight, ArrowLeft, Send, Sparkles } from "lucide-react";
import { tenantApi } from "@/lib/api";

interface TestBotResponse {
  response_text: string;
  confidence_level: string;
  confidence_score: number;
  image_would_be_sent: boolean;
  prospect_detected: boolean;
  elapsed_ms: number;
}

const SUGGESTIONS = [
  "Bonjour, c'est combien la robe rouge ?",
  "Vous livrez à Toamasina ?",
  "Salama, mety ny Mvola ?",
  "Vous êtes ouverts ce dimanche ?",
];

interface Step5Props {
  pageName: string;
  onBack: () => void;
  onNext: () => void;
}

export function Step5Test({ pageName, onBack, onNext }: Step5Props) {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState<TestBotResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendTest = async (text: string) => {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    setResponse(null);
    try {
      const res = await tenantApi<TestBotResponse>("/test-bot", {
        method: "POST",
        body: JSON.stringify({ message: text, channel: "messenger" }),
      });
      setResponse(res);
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Erreur lors du test. Réessaie dans un instant."
      );
    } finally {
      setLoading(false);
    }
  };

  const confidenceColor =
    response?.confidence_level === "high"
      ? "#2D4A3E"
      : response?.confidence_level === "medium"
      ? "#F4B83A"
      : "#B7481E";

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-10">
        <span className="font-mono text-xs text-[#B7481E] uppercase tracking-widest mb-4 block">
          04 — Test
        </span>
        <h2 className="font-display text-3xl md:text-5xl text-[#1A1614] tracking-tight leading-[1.05] mb-4">
          Pose une question{" "}
          <span className="italic text-[#B7481E]">comme un client</span>
        </h2>
        <p className="text-[#1A1614]/70 leading-relaxed">
          On teste le bot avant de l&apos;activer. Tu vois la réponse, sa confiance, et tu peux
          ajuster avant que les vrais clients arrivent.
        </p>
      </div>

      {/* Suggestions */}
      <div className="mb-6">
        <p className="font-mono text-xs uppercase tracking-widest text-[#1A1614]/50 mb-3">
          Idées de questions
        </p>
        <div className="flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => {
                setMessage(s);
                sendTest(s);
              }}
              className="text-xs px-3 py-1.5 rounded-full border border-[#1A1614]/15 bg-[#FBF6EE] hover:border-[#B7481E] hover:text-[#B7481E] text-[#1A1614]/80 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="mb-6">
        <div className="flex items-center gap-2 p-3 rounded-2xl border-2 border-[#1A1614]/15 bg-[#FBF6EE] focus-within:border-[#B7481E] transition-colors">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendTest(message)}
            placeholder="Tape une question comme un client..."
            className="flex-1 px-3 py-2 bg-transparent focus:outline-none text-[#1A1614] placeholder:text-[#1A1614]/30"
          />
          <button
            onClick={() => sendTest(message)}
            disabled={!message.trim() || loading}
            className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-[#1A1614] text-[#FBF6EE] hover:bg-[#B7481E] disabled:opacity-30 transition-colors"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Response */}
      {loading && (
        <div className="rounded-2xl bg-[#F5E9D9] p-6 text-center text-[#1A1614]/60 text-sm">
          <Sparkles className="h-5 w-5 mx-auto mb-2 animate-pulse text-[#B7481E]" />
          Le bot réfléchit...
        </div>
      )}

      {error && (
        <div className="rounded-2xl bg-[#B7481E]/10 border border-[#B7481E]/30 p-5 text-sm text-[#B7481E]">
          {error}
        </div>
      )}

      {response && !loading && (
        <div className="rounded-2xl bg-[#F0EAE3] p-5 mb-6">
          {/* Conversation preview */}
          <div className="space-y-3">
            <div className="flex justify-end">
              <div className="max-w-[80%] bg-white rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm text-[#1A1614] shadow-sm">
                {message}
              </div>
            </div>
            <div className="flex justify-start">
              <div className="max-w-[80%] bg-[#1A1614] text-[#FBF6EE] rounded-2xl rounded-tl-sm px-4 py-2.5 text-sm leading-relaxed shadow-sm">
                {response.response_text}
              </div>
            </div>
          </div>

          {/* Diagnostic */}
          <div className="mt-5 pt-4 border-t border-[#1A1614]/10 grid grid-cols-3 gap-3 text-xs">
            <div>
              <p className="font-mono uppercase tracking-widest text-[#1A1614]/50 mb-1">Confiance</p>
              <p
                className="font-display text-base font-semibold"
                style={{ color: confidenceColor }}
              >
                {response.confidence_level} ({Math.round(response.confidence_score * 100)}%)
              </p>
            </div>
            <div>
              <p className="font-mono uppercase tracking-widest text-[#1A1614]/50 mb-1">Photo</p>
              <p className="font-display text-base font-semibold text-[#1A1614]">
                {response.image_would_be_sent ? "envoyée" : "aucune"}
              </p>
            </div>
            <div>
              <p className="font-mono uppercase tracking-widest text-[#1A1614]/50 mb-1">Latence</p>
              <p className="font-display text-base font-semibold text-[#1A1614]">
                {(response.elapsed_ms / 1000).toFixed(1)}s
              </p>
            </div>
          </div>

          {response.prospect_detected && (
            <div className="mt-3 inline-flex items-center gap-2 text-xs text-[#2D4A3E] bg-[#2D4A3E]/10 rounded-full px-3 py-1">
              <span className="h-1.5 w-1.5 rounded-full bg-[#2D4A3E]" />
              Prospect chaud détecté
            </div>
          )}
        </div>
      )}

      <div className="flex items-center justify-between pt-6 border-t border-[#1A1614]/10">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-2 text-[#1A1614]/70 hover:text-[#1A1614] text-sm"
        >
          <ArrowLeft className="h-4 w-4" />
          Précédent
        </button>

        <button
          onClick={onNext}
          className="group inline-flex items-center gap-3 rounded-full bg-[#1A1614] text-[#FBF6EE] pl-6 pr-2 py-2 text-base font-medium hover:bg-[#B7481E] transition-all"
        >
          {response ? "Activer le bot" : "Activer sans tester"}
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-[#F4B83A] text-[#1A1614] group-hover:translate-x-0.5 transition-transform">
            <ArrowRight className="h-4 w-4" />
          </span>
        </button>
      </div>
    </div>
  );
}
