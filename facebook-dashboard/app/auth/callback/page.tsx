"use client";

import { Suspense } from "react";
import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { tenantApi } from "@/lib/api";
import { toast } from "sonner";

function CallbackHandler() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { login } = useAuth();

  useEffect(() => {
    const token = searchParams.get("token");
    const error = searchParams.get("error");

    if (error) {
      toast.error(error, { duration: 8000 });
      router.replace("/");
      return;
    }

    if (token) {
      login(token);

      // Onboarding routing : si l'utilisateur n'a pas termine son onboarding,
      // on l'envoie vers le wizard plutot que directement au dashboard.
      (async () => {
        try {
          const config = await tenantApi<{ onboarding_step?: string }>("/config");
          if (config && config.onboarding_step !== "complete") {
            router.replace("/onboarding");
          } else {
            router.replace("/dashboard");
          }
        } catch {
          router.replace("/dashboard");
        }
      })();
    } else {
      router.replace("/");
    }
  }, [searchParams, login, router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-muted-foreground">Connexion en cours...</p>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <p className="text-muted-foreground">Chargement...</p>
        </div>
      }
    >
      <CallbackHandler />
    </Suspense>
  );
}
