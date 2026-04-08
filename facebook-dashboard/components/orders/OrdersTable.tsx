"use client";

import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useOrders, updateOrderStatus } from "@/hooks/useOrders";
import { toast } from "sonner";

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-orange-100 text-orange-800",
  confirmed: "bg-blue-100 text-blue-800",
  delivered: "bg-green-100 text-green-800",
  cancelled: "bg-red-100 text-red-800",
};

const STATUS_LABELS: Record<string, string> = {
  pending: "En attente",
  confirmed: "Confirmee",
  delivered: "Livree",
  cancelled: "Annulee",
};

const PAYMENT_LABELS: Record<string, string> = {
  mvola: "MVola",
  orange_money: "Orange Money",
  airtel_money: "Airtel Money",
  cash: "Especes",
  paiement: "Non precise",
};

export function OrdersTable() {
  const [filter, setFilter] = useState<string | undefined>(undefined);
  const { orders, isLoading, mutate } = useOrders(filter);

  const handleStatusChange = async (orderId: string, newStatus: string) => {
    try {
      await updateOrderStatus(orderId, newStatus);
      toast.success(`Commande: ${STATUS_LABELS[newStatus]}`);
      mutate();
    } catch {
      toast.error("Erreur lors de la mise a jour");
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <Select
          value={filter ?? "all"}
          onValueChange={(v) => setFilter(v === "all" ? undefined : v)}
        >
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Filtrer par statut" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Toutes</SelectItem>
            <SelectItem value="pending">En attente</SelectItem>
            <SelectItem value="confirmed">Confirmees</SelectItem>
            <SelectItem value="delivered">Livrees</SelectItem>
            <SelectItem value="cancelled">Annulees</SelectItem>
          </SelectContent>
        </Select>
        <span className="text-sm text-muted-foreground">
          {orders?.total ?? 0} commande(s)
        </span>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Client</TableHead>
              <TableHead>Telephone</TableHead>
              <TableHead>Canal</TableHead>
              <TableHead>Articles</TableHead>
              <TableHead>Montant</TableHead>
              <TableHead>Paiement</TableHead>
              <TableHead>Statut</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={9} className="text-center py-8">
                  Chargement...
                </TableCell>
              </TableRow>
            ) : !orders?.orders?.length ? (
              <TableRow>
                <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">
                  Aucune commande pour le moment.
                  Les commandes apparaitront quand l&apos;IA collectera les informations d&apos;achat des clients.
                </TableCell>
              </TableRow>
            ) : (
              orders.orders.map((o) => (
                <TableRow key={o.id}>
                  <TableCell className="font-medium">
                    {o.customer_name || o.sender_id}
                  </TableCell>
                  <TableCell>{o.customer_phone || "-"}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{o.channel}</Badge>
                  </TableCell>
                  <TableCell>
                    {o.items?.length
                      ? o.items.map((i) => i.product_name).join(", ")
                      : "-"}
                  </TableCell>
                  <TableCell className="font-medium">
                    {o.total_amount || "-"}
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary">
                      {PAYMENT_LABELS[o.payment_method] ?? o.payment_method || "-"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={STATUS_COLORS[o.status]}>
                      {STATUS_LABELS[o.status] ?? o.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {o.created_at
                      ? new Date(o.created_at).toLocaleDateString("fr-FR", {
                          day: "2-digit",
                          month: "short",
                          hour: "2-digit",
                          minute: "2-digit",
                        })
                      : "-"}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      {o.status === "pending" && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleStatusChange(o.id, "confirmed")}
                        >
                          Confirmer
                        </Button>
                      )}
                      {o.status === "confirmed" && (
                        <Button
                          size="sm"
                          className="bg-green-600 hover:bg-green-700"
                          onClick={() => handleStatusChange(o.id, "delivered")}
                        >
                          Livree
                        </Button>
                      )}
                      {o.status !== "cancelled" && o.status !== "delivered" && (
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleStatusChange(o.id, "cancelled")}
                        >
                          Annuler
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
