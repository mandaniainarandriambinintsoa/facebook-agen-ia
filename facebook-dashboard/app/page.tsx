"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { apiUrl } from "@/lib/api";

export default function LoginPage() {
  const { authenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (authenticated) router.replace("/dashboard");
  }, [authenticated, router]);

  const handleLogin = () => {
    const callbackUrl = `${window.location.origin}/auth/callback`;
    window.location.href = apiUrl(`/auth/facebook/login?state=${encodeURIComponent(callbackUrl)}`);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-muted/40 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Facebook Agent IA</CardTitle>
          <CardDescription>
            Service opéré par RANDRIAMBININTSOA MANDANIAINA
          </CardDescription>
          <CardDescription>
            Connectez-vous pour gérer votre agent IA
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            onClick={handleLogin}
            className="w-full text-white"
            style={{ backgroundColor: "#1877F2" }}
            size="lg"
          >
            Se connecter avec Facebook
          </Button>
        </CardContent>
      </Card>
      <footer className="mt-8 text-center text-xs text-muted-foreground space-y-1">
        <p>
          © 2026 <strong>RANDRIAMBININTSOA MANDANIAINA</strong>
        </p>
        <p>
          LOT VT 85 HE BIS DB ANDOHANIMANDROSEZA, Antananarivo, Analamanga, 101, Madagascar
        </p>
        <p>
          Contact : contact@manda-ia.com ·{" "}
          <a href="/privacy" className="underline">Confidentialité</a> ·{" "}
          <a href="/terms" className="underline">Conditions</a>
        </p>
      </footer>
    </div>
  );
}
