"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useConfig } from "@/hooks/useConfig";
import { toast } from "sonner";
import type { BotConfig } from "@/lib/types";

const schema = z.object({
  welcome_message: z.string().min(1, "Message d'accueil requis"),
  bot_type: z.string(),
  delivery_enabled: z.boolean(),
  phone_numbers: z.string(),
  custom_system_prompt: z.string(),
  conversation_mode: z.enum(["catalog", "classic"]),
});

export function BotConfigForm() {
  const { config, isLoading, updateConfig } = useConfig();
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<BotConfig>({
    resolver: zodResolver(schema),
    defaultValues: {
      welcome_message: "",
      bot_type: "support",
      delivery_enabled: false,
      phone_numbers: "",
      custom_system_prompt: "",
      conversation_mode: "catalog",
    },
  });

  useEffect(() => {
    if (config) reset(config);
  }, [config, reset]);

  const deliveryEnabled = watch("delivery_enabled");

  const onSubmit = async (data: BotConfig) => {
    try {
      await updateConfig(data);
      toast.success("Configuration sauvegardée");
    } catch {
      toast.error("Erreur lors de la sauvegarde");
    }
  };

  if (isLoading) {
    return <p className="text-muted-foreground">Chargement...</p>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Configuration du bot</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div>
            <Label>Message d&apos;accueil</Label>
            <Textarea {...register("welcome_message")} rows={3} />
            {errors.welcome_message && (
              <p className="text-sm text-red-500">
                {errors.welcome_message.message}
              </p>
            )}
          </div>

          <div>
            <Label>Type de bot</Label>
            <Select
              value={watch("bot_type")}
              onValueChange={(v) => setValue("bot_type", v)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="support">Support client</SelectItem>
                <SelectItem value="sales">Vente</SelectItem>
                <SelectItem value="info">Information</SelectItem>
                <SelectItem value="custom">Personnalisé</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Mode de conversation</Label>
            <Select
              value={watch("conversation_mode")}
              onValueChange={(v) =>
                setValue("conversation_mode", v as "catalog" | "classic")
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="catalog">
                  Catalogue — présente produits + boutons/quick replies
                </SelectItem>
                <SelectItem value="classic">
                  Classique — conversation texte pure, sans boutons
                </SelectItem>
              </SelectContent>
            </Select>
            <p className="mt-1 text-xs text-muted-foreground">
              {watch("conversation_mode") === "classic"
                ? "Le bot répondra uniquement en texte, comme un agent humain. Idéal pour SAV et support conversationnel."
                : "Le bot propose des produits, boutons et quick replies. Idéal pour e-commerce et conversion."}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Switch
              checked={deliveryEnabled}
              onCheckedChange={(v) => setValue("delivery_enabled", v)}
            />
            <Label>Livraison activée</Label>
          </div>

          <div>
            <Label>Numéros de téléphone (séparés par des virgules)</Label>
            <Input {...register("phone_numbers")} />
          </div>

          <div>
            <Label>System prompt personnalisé</Label>
            <Textarea {...register("custom_system_prompt")} rows={5} />
          </div>

          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Enregistrement..." : "Sauvegarder"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
