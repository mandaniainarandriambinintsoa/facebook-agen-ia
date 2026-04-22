"use client";

import { BotConfigForm } from "@/components/config/BotConfigForm";

export default function ConfigPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="space-y-1">
        <h2 className="text-2xl font-bold tracking-tight">Configuration</h2>
        <p className="text-sm text-muted-foreground">
          Personnalisez le comportement de votre assistant IA.
        </p>
      </div>
      <BotConfigForm />
    </div>
  );
}
