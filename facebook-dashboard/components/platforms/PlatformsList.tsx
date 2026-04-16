"use client";

import { usePlatforms } from "@/hooks/usePlatforms";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Facebook, Instagram, MessageCircle } from "lucide-react";
import type { TenantPlatform } from "@/lib/types";

const PLATFORM_META = {
  messenger: {
    label: "Facebook Messenger",
    icon: Facebook,
    color: "text-blue-600",
  },
  instagram: {
    label: "Instagram Direct",
    icon: Instagram,
    color: "text-pink-600",
  },
  whatsapp: {
    label: "WhatsApp Business",
    icon: MessageCircle,
    color: "text-green-600",
  },
} as const;

export function PlatformsList() {
  const { platforms, isLoading, error } = usePlatforms();

  if (isLoading) return <p className="text-muted-foreground">Chargement...</p>;
  if (error)
    return <p className="text-red-500">Erreur de chargement des plateformes</p>;

  const list = platforms ?? [];

  if (list.length === 0) {
    return (
      <Card>
        <CardContent className="p-6 text-center text-muted-foreground">
          Aucune plateforme connectée pour l&apos;instant.
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {list.map((p) => (
        <PlatformCard key={p.id} platform={p} />
      ))}
    </div>
  );
}

function PlatformCard({ platform }: { platform: TenantPlatform }) {
  const meta = PLATFORM_META[platform.platform];
  const Icon = meta.icon;

  return (
    <Card>
      <CardContent className="p-5 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Icon className={`h-5 w-5 ${meta.color}`} />
            <span className="font-medium">{meta.label}</span>
          </div>
          <Badge variant={platform.is_active ? "default" : "secondary"}>
            {platform.is_active ? "Actif" : "Inactif"}
          </Badge>
        </div>
        <div className="text-sm text-muted-foreground">
          <div className="truncate font-medium text-foreground">
            {platform.platform_name}
          </div>
          <div className="font-mono text-xs break-all">{platform.platform_id}</div>
        </div>
      </CardContent>
    </Card>
  );
}
