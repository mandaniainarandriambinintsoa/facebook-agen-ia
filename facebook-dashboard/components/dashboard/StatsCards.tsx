"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useStats } from "@/hooks/useStats";
import { MessageSquare, TrendingUp, Target, Package, Flame, ShoppingCart } from "lucide-react";

export function StatsCards() {
  const { stats, isLoading } = useStats();

  const cards = [
    {
      title: "Messages aujourd'hui",
      value: stats?.messages_today ?? 0,
      icon: MessageSquare,
      color: "",
    },
    {
      title: "Prospects aujourd'hui",
      value: stats?.prospects_today ?? 0,
      icon: Flame,
      color: "text-red-500",
    },
    {
      title: "Commandes en attente",
      value: stats?.orders_pending ?? 0,
      icon: ShoppingCart,
      color: "text-orange-500",
    },
    {
      title: "Taux conversion",
      value: `${stats?.conversion_rate ?? 0}%`,
      icon: TrendingUp,
      color: "text-green-500",
    },
    {
      title: "Confiance moyenne",
      value: stats ? `${(stats.avg_confidence * 100).toFixed(0)}%` : "0%",
      icon: Target,
      color: "",
    },
    {
      title: "Produits",
      value: stats?.products_count ?? 0,
      icon: Package,
      color: "",
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {card.title}
            </CardTitle>
            <card.icon className={`h-4 w-4 ${card.color || "text-muted-foreground"}`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? "..." : card.value}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
