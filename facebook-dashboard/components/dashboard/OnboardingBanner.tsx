"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowRight, X, Sparkles } from "lucide-react";
import { useConfig } from "@/hooks/useConfig";

const DISMISS_KEY = "valina_onboarding_banner_dismissed_v1";

export function OnboardingBanner() {
  const { config, isLoading } = useConfig();
  const [dismissed, setDismissed] = useState(() => {
    if (typeof window === "undefined") return false;
    return localStorage.getItem(DISMISS_KEY) === "true";
  });

  if (isLoading) return null;
  if (!config) return null;
  if (config.onboarding_step === "complete") return null;
  if (dismissed) return null;

  const handleDismiss = () => {
    localStorage.setItem(DISMISS_KEY, "true");
    setDismissed(true);
  };

  return (
    <div className="bg-[#1877F2] text-white px-4 md:px-6 py-3">
      <div className="max-w-5xl mx-auto flex items-center gap-3">
        <Sparkles className="h-4 w-4 shrink-0 text-[#F4B83A]" />

        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium leading-tight">
            <span className="hidden sm:inline">Bienvenue ! </span>
            Configure ton bot en 5 étapes pour qu&apos;il commence à répondre à tes clients.
          </p>
        </div>

        <Link
          href="/onboarding"
          className="hidden sm:inline-flex items-center gap-2 rounded-full bg-white text-[#1877F2] px-4 py-1.5 text-sm font-semibold hover:bg-[#F4B83A] hover:text-[#1C1E21] transition-colors shrink-0"
        >
          Configurer
          <ArrowRight className="h-3.5 w-3.5" />
        </Link>

        <Link
          href="/onboarding"
          className="sm:hidden inline-flex items-center gap-1 rounded-full bg-white text-[#1877F2] px-3 py-1 text-xs font-semibold shrink-0"
        >
          Go
          <ArrowRight className="h-3 w-3" />
        </Link>

        <button
          onClick={handleDismiss}
          aria-label="Masquer"
          className="inline-flex h-7 w-7 items-center justify-center rounded-full hover:bg-white/15 transition-colors shrink-0"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}
