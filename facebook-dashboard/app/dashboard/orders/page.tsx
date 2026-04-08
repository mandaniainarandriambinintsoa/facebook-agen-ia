"use client";

import { OrdersTable } from "@/components/orders/OrdersTable";
import { OrdersStats } from "@/components/orders/OrdersStats";

export default function OrdersPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Commandes</h2>
      <OrdersStats />
      <OrdersTable />
    </div>
  );
}
