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
    <div className="min-h-screen flex items-center justify-center bg-muted/40 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Facebook Agent IA</CardTitle>
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
    </div>
  );
}
