"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useOrdersStats } from "@/hooks/useOrders";
import { ShoppingCart, Clock, CheckCircle, TrendingUp } from "lucide-react";

export function OrdersStats() {
  const { stats, isLoading } = useOrdersStats();

  const cards = [
    {
      title: "Aujourd'hui",
      value: stats?.today ?? 0,
      icon: ShoppingCart,
      color: "text-blue-500",
    },
    {
      title: "En attente",
      value: stats?.by_status?.pending ?? 0,
      icon: Clock,
      color: "text-orange-500",
    },
    {
      title: "Livrees",
      value: stats?.by_status?.delivered ?? 0,
      icon: CheckCircle,
      color: "text-green-500",
    },
    {
      title: "Taux conversion",
      value: `${stats?.conversion_rate ?? 0}%`,
      icon: TrendingUp,
      color: "text-purple-500",
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
            <card.icon className={`h-4 w-4 ${card.color}`} />
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
