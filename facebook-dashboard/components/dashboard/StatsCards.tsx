"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useStats } from "@/hooks/useStats";
import { MessageSquare, TrendingUp, Target, Package } from "lucide-react";

export function StatsCards() {
  const { stats, isLoading } = useStats();

  const cards = [
    {
      title: "Messages aujourd'hui",
      value: stats?.messages_today ?? 0,
      icon: MessageSquare,
    },
    {
      title: "Messages totaux",
      value: stats?.messages_total ?? 0,
      icon: TrendingUp,
    },
    {
      title: "Confiance moyenne",
      value: stats ? `${(stats.avg_confidence * 100).toFixed(0)}%` : "0%",
      icon: Target,
    },
    {
      title: "Produits",
      value: stats?.products_count ?? 0,
      icon: Package,
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {card.title}
            </CardTitle>
            <card.icon className="h-4 w-4 text-muted-foreground" />
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
