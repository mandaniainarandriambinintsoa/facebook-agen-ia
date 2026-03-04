"use client";

import { BotConfigForm } from "@/components/config/BotConfigForm";

export default function ConfigPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Configuration</h2>
      <BotConfigForm />
    </div>
  );
}
