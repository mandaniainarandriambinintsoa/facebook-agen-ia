"use client";

import { PlatformsList } from "@/components/platforms/PlatformsList";
import { ConnectWhatsappForm } from "@/components/platforms/ConnectWhatsappForm";
import { ReconnectFacebookCard } from "@/components/platforms/ReconnectFacebookCard";

export default function PlatformsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Plateformes</h2>
        <p className="text-sm text-muted-foreground">
          Gérez les canaux connectés à votre agent IA
        </p>
      </div>
      <PlatformsList />
      <ReconnectFacebookCard />
      <ConnectWhatsappForm />
    </div>
  );
}
