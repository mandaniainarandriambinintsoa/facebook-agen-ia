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
