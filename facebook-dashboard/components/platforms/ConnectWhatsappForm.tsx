"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { usePlatforms } from "@/hooks/usePlatforms";
import { toast } from "sonner";

export function ConnectWhatsappForm() {
  const { connectWhatsapp } = usePlatforms();
  const [phoneNumberId, setPhoneNumberId] = useState("");
  const [accessToken, setAccessToken] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [saving, setSaving] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phoneNumberId || !accessToken) {
      toast.error("phone_number_id et access_token requis");
      return;
    }
    setSaving(true);
    try {
      await connectWhatsapp({
        phone_number_id: phoneNumberId.trim(),
        access_token: accessToken.trim(),
        display_name: displayName.trim() || undefined,
      });
      toast.success("WhatsApp connecté");
      setPhoneNumberId("");
      setAccessToken("");
      setDisplayName("");
    } catch {
      toast.error("Erreur de connexion WhatsApp");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Connecter WhatsApp Business</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <Label>Phone Number ID</Label>
            <Input
              value={phoneNumberId}
              onChange={(e) => setPhoneNumberId(e.target.value)}
              placeholder="1234567890123456"
            />
          </div>
          <div>
            <Label>Access Token</Label>
            <Input
              type="password"
              value={accessToken}
              onChange={(e) => setAccessToken(e.target.value)}
              placeholder="EAAG..."
            />
          </div>
          <div>
            <Label>Nom affiché (optionnel)</Label>
            <Input
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="Mon WhatsApp Business"
            />
          </div>
          <Button type="submit" disabled={saving}>
            {saving ? "Connexion..." : "Connecter WhatsApp"}
          </Button>
          <p className="text-xs text-muted-foreground">
            Récupérez ces valeurs depuis la WhatsApp Business Platform sur
            developers.facebook.com.
          </p>
        </form>
      </CardContent>
    </Card>
  );
}
