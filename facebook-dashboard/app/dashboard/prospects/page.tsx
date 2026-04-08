"use client";

import { ProspectsTable } from "@/components/prospects/ProspectsTable";
import { ProspectsStats } from "@/components/prospects/ProspectsStats";

export default function ProspectsPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Prospects (Hot Leads)</h2>
      <ProspectsStats />
      <ProspectsTable />
    </div>
  );
}
