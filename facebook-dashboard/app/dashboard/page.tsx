"use client";

import { useState } from "react";
import { StatsCards } from "@/components/dashboard/StatsCards";
import { MessagesChart } from "@/components/dashboard/MessagesChart";
import { RecentMessages } from "@/components/dashboard/RecentMessages";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const PERIOD_OPTIONS = [
  { value: "7", label: "7 jours" },
  { value: "30", label: "30 jours" },
  { value: "90", label: "90 jours" },
];

export default function DashboardPage() {
  const [days, setDays] = useState(30);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-2xl font-bold">Vue d&apos;ensemble</h2>
        <Select
          value={String(days)}
          onValueChange={(v) => setDays(Number(v))}
        >
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="Periode" />
          </SelectTrigger>
          <SelectContent>
            {PERIOD_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <StatsCards days={days} />
      <MessagesChart days={days} />
      <RecentMessages />
    </div>
  );
}
