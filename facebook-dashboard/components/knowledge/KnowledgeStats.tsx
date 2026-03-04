"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Brain, Package } from "lucide-react";
import type { KnowledgeStats as KnowledgeStatsType } from "@/lib/types";

interface Props {
  knowledge: KnowledgeStatsType | undefined;
  isLoading: boolean;
}

export function KnowledgeStatsCards({ knowledge, isLoading }: Props) {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Embeddings
          </CardTitle>
          <Brain className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {isLoading ? "..." : knowledge?.embeddings_count ?? 0}
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Produits indexés
          </CardTitle>
          <Package className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {isLoading ? "..." : knowledge?.products_count ?? 0}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
