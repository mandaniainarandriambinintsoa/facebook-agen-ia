"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
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
      <Link href="/" className="mb-6 text-sm text-muted-foreground hover:text-foreground transition">
        ← Retour à l&apos;accueil
      </Link>

      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Connexion Valina-Bot</CardTitle>
          <CardDescription>
            Connectez-vous avec votre compte Facebook pour accéder à votre tableau de bord
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
          <p className="mt-4 text-center text-xs text-muted-foreground">
            Pas encore de compte ?{" "}
            <Link href="/" className="underline font-medium">
              Démarrer l&apos;essai gratuit
            </Link>
          </p>
        </CardContent>
      </Card>

      <footer className="mt-8 text-center text-xs text-muted-foreground space-y-1">
        <p>
          © 2026 <strong>RANDRIAMBININTSOA MANDANIAINA</strong>
        </p>
        <p>
          Contact : contact@manda-ia.com ·{" "}
          <Link href="/privacy" className="underline">Confidentialité</Link> ·{" "}
          <Link href="/terms" className="underline">Conditions</Link>
        </p>
      </footer>
    </div>
  );
}
