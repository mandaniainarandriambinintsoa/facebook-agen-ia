"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { apiUrl } from "@/lib/api";
import { Facebook } from "lucide-react";

export function ReconnectFacebookCard() {
  const handleReconnect = () => {
    const callbackUrl = `${window.location.origin}/auth/callback`;
    window.location.href = apiUrl(
      `/auth/facebook/login?state=${encodeURIComponent(callbackUrl)}`
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Ajouter une Page Facebook / Instagram</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-muted-foreground">
          Reconnectez-vous à Facebook pour ajouter une nouvelle page ou un compte
          Instagram Business. L&apos;agent sera automatiquement abonné aux
          messages.
        </p>
        <Button
          onClick={handleReconnect}
          className="text-white"
          style={{ backgroundColor: "#1877F2" }}
        >
          <Facebook className="h-4 w-4 mr-2" />
          Connecter avec Facebook
        </Button>
      </CardContent>
    </Card>
  );
}
