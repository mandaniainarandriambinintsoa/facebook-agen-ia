"use client";

import { ProductsTable } from "@/components/products/ProductsTable";

export default function ProductsPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Produits</h2>
      <ProductsTable />
    </div>
  );
}
