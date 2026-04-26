"use client";

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
  auto_comment_reply: z.boolean(),
});

const DEFAULT_CONFIG: BotConfig = {
  welcome_message: "",
  bot_type: "ecommerce",
  delivery_enabled: false,
  phone_numbers: "",
  custom_system_prompt: "",
  conversation_mode: "catalog",
  auto_comment_reply: false,
};

function normalizeConfig(raw: Partial<BotConfig> | null | undefined): BotConfig {
  if (!raw) return DEFAULT_CONFIG;
  return {
    welcome_message: raw.welcome_message ?? "",
    bot_type: raw.bot_type ?? "ecommerce",
    delivery_enabled: raw.delivery_enabled ?? false,
    phone_numbers: Array.isArray(raw.phone_numbers)
      ? raw.phone_numbers.join(", ")
      : (raw.phone_numbers ?? ""),
    custom_system_prompt: raw.custom_system_prompt ?? "",
    conversation_mode: raw.conversation_mode ?? "catalog",
    auto_comment_reply: raw.auto_comment_reply ?? false,
  };
}

export function BotConfigForm() {
  const { config, isLoading, updateConfig } = useConfig();

  if (isLoading) {
    return <p className="text-muted-foreground">Chargement...</p>;
  }

  return <BotConfigFormInner initial={normalizeConfig(config)} onSubmit={updateConfig} />;
}

function BotConfigFormInner({
  initial,
  onSubmit,
}: {
  initial: BotConfig;
  onSubmit: (data: BotConfig) => Promise<void>;
}) {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<BotConfig>({
    resolver: zodResolver(schema),
    defaultValues: initial,
  });

  const handleFormSubmit = async (data: BotConfig) => {
    try {
      const phonesArr = (data.phone_numbers ?? "")
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      await onSubmit({ ...data, phone_numbers: phonesArr as unknown as string });
      toast.success("Configuration sauvegardée");
    } catch {
      toast.error("Erreur lors de la sauvegarde");
    }
  };

  const deliveryEnabled = watch("delivery_enabled");
  const conversationMode = watch("conversation_mode");
  const autoCommentReply = watch("auto_comment_reply");

  return (
    <Card>
      <CardHeader>
        <CardTitle>Configuration du bot</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
          <div className="space-y-2">
            <Label>Message d&apos;accueil</Label>
            <Textarea {...register("welcome_message")} rows={3} />
            {errors.welcome_message && (
              <p className="text-sm text-red-500">
                {errors.welcome_message.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label>Type de bot</Label>
            <Select
              value={watch("bot_type")}
              onValueChange={(v) => setValue("bot_type", v)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Sélectionner un type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ecommerce">E-commerce</SelectItem>
                <SelectItem value="support">Support client</SelectItem>
                <SelectItem value="sales">Vente</SelectItem>
                <SelectItem value="info">Information</SelectItem>
                <SelectItem value="custom">Personnalisé</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Mode de conversation</Label>
            <Select
              value={conversationMode}
              onValueChange={(v) =>
                setValue("conversation_mode", v as "catalog" | "classic")
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="catalog">
                  Catalogue — produits + boutons
                </SelectItem>
                <SelectItem value="classic">
                  Classique — conversation texte
                </SelectItem>
              </SelectContent>
            </Select>
            <p className="text-sm text-muted-foreground">
              {conversationMode === "classic"
                ? "Le bot répond uniquement en texte, comme un agent humain. Idéal pour SAV et support conversationnel."
                : "Le bot propose des produits, boutons et quick replies. Idéal pour e-commerce et conversion."}
            </p>
          </div>

          <div className="flex items-center gap-3 pt-2">
            <Switch
              checked={deliveryEnabled}
              onCheckedChange={(v) => setValue("delivery_enabled", v)}
            />
            <Label>Livraison activée</Label>
          </div>

          <div className="space-y-2 pt-2">
            <div className="flex items-center gap-3">
              <Switch
                checked={autoCommentReply}
                onCheckedChange={(v) => setValue("auto_comment_reply", v)}
              />
              <Label>Réponse automatique aux commentaires Facebook</Label>
            </div>
            <p className="text-sm text-muted-foreground">
              {autoCommentReply
                ? "L'IA classe chaque commentaire et engage uniquement les vrais prospects (questions, prix, demande MP) en envoyant une réponse publique courte + un message privé personnalisé."
                : "Activez pour que le bot réponde automatiquement sous vos posts et ouvre une conversation Messenger avec les prospects intéressés."}
            </p>
          </div>

          <div className="space-y-2">
            <Label>Numéros de téléphone (séparés par des virgules)</Label>
            <Input {...register("phone_numbers")} />
          </div>

          <div className="space-y-2">
            <Label>System prompt personnalisé</Label>
            <Textarea {...register("custom_system_prompt")} rows={5} />
          </div>

          <div className="pt-2">
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Enregistrement..." : "Sauvegarder"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
