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
  previewMode?: boolean;
}

export function Step5Test({ pageName, onBack, onNext, previewMode = false }: Step5Props) {
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
      if (previewMode) {
        await new Promise((r) => setTimeout(r, 800));
        setResponse({
          response_text:
            "Bonjour ! La robe rouge est en M, L et XL à 80 000 Ar. Mvola, Orange Money et Airtel Money acceptés. Livraison Tana 24h. Tu veux laquelle ?",
          confidence_level: "high",
          confidence_score: 0.87,
          image_would_be_sent: true,
          prospect_detected: text.toLowerCase().includes("mvola") || text.toLowerCase().includes("achat"),
          elapsed_ms: 1240,
        });
        return;
      }
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
      ? "#16A34A"
      : response?.confidence_level === "medium"
      ? "#F4B83A"
      : "#1877F2";

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-10">
        <span className="font-mono text-xs text-[#1877F2] uppercase tracking-widest mb-4 block">
          04 — Test
        </span>
        <h2 className="text-3xl md:text-5xl text-[#1C1E21] tracking-tight leading-[1.05] mb-4">
          Pose une question{" "}
          <span className="italic text-[#1877F2]">comme un client</span>
        </h2>
        <p className="text-[#1C1E21]/70 leading-relaxed">
          On teste le bot avant de l&apos;activer. Tu vois la réponse, sa confiance, et tu peux
          ajuster avant que les vrais clients arrivent.
        </p>
      </div>

      {/* Suggestions */}
      <div className="mb-6">
        <p className="font-mono text-xs uppercase tracking-widest text-[#1C1E21]/50 mb-3">
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
              className="text-xs px-3 py-1.5 rounded-full border border-[#1C1E21]/15 bg-[#F7F8FA] hover:border-[#1877F2] hover:text-[#1877F2] text-[#1C1E21]/80 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="mb-6">
        <div className="flex items-center gap-2 p-3 rounded-2xl border-2 border-[#1C1E21]/15 bg-[#F7F8FA] focus-within:border-[#1877F2] transition-colors">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendTest(message)}
            placeholder="Tape une question comme un client..."
            className="flex-1 px-3 py-2 bg-transparent focus:outline-none text-[#1C1E21] placeholder:text-[#1C1E21]/30"
          />
          <button
            onClick={() => sendTest(message)}
            disabled={!message.trim() || loading}
            className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-[#1C1E21] text-[#F7F8FA] hover:bg-[#1877F2] disabled:opacity-30 transition-colors"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Response */}
      {loading && (
        <div className="rounded-2xl bg-[#F0F2F5] p-6 text-center text-[#1C1E21]/60 text-sm">
          <Sparkles className="h-5 w-5 mx-auto mb-2 animate-pulse text-[#1877F2]" />
          Le bot réfléchit...
        </div>
      )}

      {error && (
        <div className="rounded-2xl bg-[#1877F2]/10 border border-[#1877F2]/30 p-5 text-sm text-[#1877F2]">
          {error}
        </div>
      )}

      {response && !loading && (
        <div className="rounded-2xl bg-[#E4E6EA] p-5 mb-6">
          {/* Conversation preview */}
          <div className="space-y-3">
            <div className="flex justify-end">
              <div className="max-w-[80%] bg-white rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm text-[#1C1E21] shadow-sm">
                {message}
              </div>
            </div>
            <div className="flex justify-start">
              <div className="max-w-[80%] bg-[#1C1E21] text-[#F7F8FA] rounded-2xl rounded-tl-sm px-4 py-2.5 text-sm leading-relaxed shadow-sm">
                {response.response_text}
              </div>
            </div>
          </div>

          {/* Diagnostic */}
          <div className="mt-5 pt-4 border-t border-[#1C1E21]/10 grid grid-cols-3 gap-3 text-xs">
            <div>
              <p className="font-mono uppercase tracking-widest text-[#1C1E21]/50 mb-1">Confiance</p>
              <p
                className="text-base font-semibold"
                style={{ color: confidenceColor }}
              >
                {response.confidence_level} ({Math.round(response.confidence_score * 100)}%)
              </p>
            </div>
            <div>
              <p className="font-mono uppercase tracking-widest text-[#1C1E21]/50 mb-1">Photo</p>
              <p className="text-base font-semibold text-[#1C1E21]">
                {response.image_would_be_sent ? "envoyée" : "aucune"}
              </p>
            </div>
            <div>
              <p className="font-mono uppercase tracking-widest text-[#1C1E21]/50 mb-1">Latence</p>
              <p className="text-base font-semibold text-[#1C1E21]">
                {(response.elapsed_ms / 1000).toFixed(1)}s
              </p>
            </div>
          </div>

          {response.prospect_detected && (
            <div className="mt-3 inline-flex items-center gap-2 text-xs text-[#16A34A] bg-[#16A34A]/10 rounded-full px-3 py-1">
              <span className="h-1.5 w-1.5 rounded-full bg-[#16A34A]" />
              Prospect chaud détecté
            </div>
          )}
        </div>
      )}

      <div className="flex items-center justify-between pt-6 border-t border-[#1C1E21]/10">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-2 text-[#1C1E21]/70 hover:text-[#1C1E21] text-sm"
        >
          <ArrowLeft className="h-4 w-4" />
          Précédent
        </button>

        <button
          onClick={onNext}
          className="group inline-flex items-center gap-3 rounded-full bg-[#1C1E21] text-[#F7F8FA] pl-6 pr-2 py-2 text-base font-medium hover:bg-[#1877F2] transition-all"
        >
          {response ? "Activer le bot" : "Activer sans tester"}
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-[#F4B83A] text-[#1C1E21] group-hover:translate-x-0.5 transition-transform">
            <ArrowRight className="h-4 w-4" />
          </span>
        </button>
      </div>
    </div>
  );
}
