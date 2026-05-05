"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useConfig } from "@/hooks/useConfig";
import { tenantApi } from "@/lib/api";
import { ProgressBar } from "./ProgressBar";
import { Step1Welcome } from "./Step1Welcome";
import { Step2Business } from "./Step2Business";
import { Step3WelcomeMessage } from "./Step3WelcomeMessage";
import { Step4Catalog } from "./Step4Catalog";
import { Step5Test } from "./Step5Test";
import { StepDone } from "./StepDone";

const STEP_LABELS = ["Bienvenue", "Métier", "Accueil", "Catalogue", "Test", "Activé"];

export function OnboardingFlow() {
  const router = useRouter();
  const { authenticated } = useAuth();
  const { config, isLoading } = useConfig();

  const [step, setStep] = useState(1);
  const [pageName, setPageName] = useState("ta page");
  const [botType, setBotType] = useState<string | null>(null);
  const [welcomeMessage, setWelcomeMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!authenticated) {
      router.replace("/login");
    }
  }, [authenticated, router]);

  useEffect(() => {
    if (config) {
      if (config.bot_type) setBotType(config.bot_type);
      if (config.welcome_message) setWelcomeMessage(config.welcome_message);
    }
  }, [config]);

  useEffect(() => {
    const fetchTenantName = async () => {
      try {
        const stats = await tenantApi<{ page_name?: string }>("/stats");
        if (stats?.page_name) setPageName(stats.page_name);
      } catch {
        // silent
      }
    };
    if (authenticated) fetchTenantName();
  }, [authenticated]);

  const persistConfig = async (updates: Record<string, unknown>) => {
    try {
      await tenantApi("/config", {
        method: "PUT",
        body: JSON.stringify(updates),
      });
    } catch (e) {
      console.warn("persistConfig failed", e);
    }
  };

  const goNext = () => setStep((s) => Math.min(s + 1, 6));
  const goBack = () => setStep((s) => Math.max(s - 1, 1));

  const handleStep2 = async (type: string) => {
    setBotType(type);
    await persistConfig({ bot_type: type });
    goNext();
  };

  const handleStep3 = async (msg: string) => {
    setWelcomeMessage(msg);
    await persistConfig({ welcome_message: msg });
    goNext();
  };

  const handleActivate = async () => {
    await persistConfig({ onboarding_step: "complete" });
    goNext();
  };

  const skipForLater = () => router.replace("/dashboard");

  if (!authenticated || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FBF6EE]">
        <p className="font-display italic text-[#1A1614]/50">Chargement...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FBF6EE] flex flex-col">
      {/* Header minimal */}
      <header className="border-b border-[#1A1614]/10 px-5 sm:px-8 py-5">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <span className="font-display text-2xl italic font-semibold text-[#1A1614]">
            Valina<span className="text-[#B7481E]">.</span>
          </span>
          <button
            onClick={skipForLater}
            className="text-xs text-[#1A1614]/50 hover:text-[#1A1614] transition-colors"
          >
            Passer pour l&apos;instant
          </button>
        </div>
      </header>

      {/* Progress bar */}
      <div className="border-b border-[#1A1614]/10 px-5 sm:px-8 py-5">
        <div className="max-w-5xl mx-auto">
          <ProgressBar current={step} total={6} labels={STEP_LABELS} />
        </div>
      </div>

      {/* Step content */}
      <main className="flex-1 px-5 sm:px-8 py-12 md:py-20">
        {step === 1 && (
          <Step1Welcome
            pageName={pageName}
            onNext={goNext}
            onSkip={skipForLater}
          />
        )}
        {step === 2 && (
          <Step2Business
            initial={botType || undefined}
            onBack={goBack}
            onNext={handleStep2}
          />
        )}
        {step === 3 && (
          <Step3WelcomeMessage
            pageName={pageName}
            botType={botType || "other"}
            initial={welcomeMessage || undefined}
            onBack={goBack}
            onNext={handleStep3}
          />
        )}
        {step === 4 && <Step4Catalog onBack={goBack} onNext={goNext} />}
        {step === 5 && (
          <Step5Test pageName={pageName} onBack={goBack} onNext={handleActivate} />
        )}
        {step === 6 && <StepDone pageName={pageName} />}
      </main>
    </div>
  );
}
