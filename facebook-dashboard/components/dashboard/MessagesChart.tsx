"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useMessagesChart } from "@/hooks/useMessages";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export function MessagesChart() {
  const { chartData, isLoading } = useMessagesChart(30);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Messages par jour (30j)</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">
            Chargement...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData || []} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis
                dataKey="date"
                tickFormatter={(v) =>
                  new Date(v).toLocaleDateString("fr-FR", {
                    day: "2-digit",
                    month: "2-digit",
                  })
                }
                fontSize={12}
                interval="preserveStartEnd"
                minTickGap={24}
              />
              <YAxis fontSize={12} allowDecimals={false} />
              <Tooltip
                labelFormatter={(v) =>
                  new Date(v).toLocaleDateString("fr-FR")
                }
                cursor={{ fill: "rgba(0,0,0,0.04)" }}
              />
              <Bar
                dataKey="count"
                fill="#0ea5e9"
                radius={[4, 4, 0, 0]}
                maxBarSize={32}
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
