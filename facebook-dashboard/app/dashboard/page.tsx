"use client";

import { StatsCards } from "@/components/dashboard/StatsCards";
import { MessagesChart } from "@/components/dashboard/MessagesChart";
import { RecentMessages } from "@/components/dashboard/RecentMessages";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Vue d&apos;ensemble</h2>
      <StatsCards />
      <MessagesChart />
      <RecentMessages />
    </div>
  );
}
