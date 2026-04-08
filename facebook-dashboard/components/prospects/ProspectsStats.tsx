"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useProspectsStats } from "@/hooks/useProspects";
import { Flame, UserCheck, UserX, Users } from "lucide-react";

export function ProspectsStats() {
  const { stats, isLoading } = useProspectsStats();

  const cards = [
    {
      title: "Aujourd'hui",
      value: stats?.today ?? 0,
      icon: Flame,
      color: "text-red-500",
    },
    {
      title: "Cette semaine",
      value: stats?.this_week ?? 0,
      icon: Users,
      color: "text-orange-500",
    },
    {
      title: "Nouveaux",
      value: stats?.by_status?.new ?? 0,
      icon: Flame,
      color: "text-yellow-500",
    },
    {
      title: "Convertis",
      value: stats?.by_status?.converted ?? 0,
      icon: UserCheck,
      color: "text-green-500",
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
