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
import { useProspects, updateProspectStatus } from "@/hooks/useProspects";
import { toast } from "sonner";

const STATUS_COLORS: Record<string, string> = {
  new: "bg-red-100 text-red-800",
  contacted: "bg-blue-100 text-blue-800",
  converted: "bg-green-100 text-green-800",
  lost: "bg-gray-100 text-gray-800",
};

const STATUS_LABELS: Record<string, string> = {
  new: "Nouveau",
  contacted: "Contacte",
  converted: "Converti",
  lost: "Perdu",
};

const CHANNEL_LABELS: Record<string, string> = {
  messenger: "Messenger",
  instagram: "Instagram",
  whatsapp: "WhatsApp",
};

export function ProspectsTable() {
  const [filter, setFilter] = useState<string | undefined>(undefined);
  const { prospects, isLoading, mutate } = useProspects(filter);

  const handleStatusChange = async (prospectId: string, newStatus: string) => {
    try {
      await updateProspectStatus(prospectId, newStatus);
      toast.success(`Prospect mis a jour: ${STATUS_LABELS[newStatus]}`);
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
            <SelectItem value="all">Tous</SelectItem>
            <SelectItem value="new">Nouveaux</SelectItem>
            <SelectItem value="contacted">Contactes</SelectItem>
            <SelectItem value="converted">Convertis</SelectItem>
            <SelectItem value="lost">Perdus</SelectItem>
          </SelectContent>
        </Select>
        <span className="text-sm text-muted-foreground">
          {prospects?.total ?? 0} prospect(s)
        </span>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Client</TableHead>
              <TableHead>Canal</TableHead>
              <TableHead>Mot-cle</TableHead>
              <TableHead>Message</TableHead>
              <TableHead>Statut</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8">
                  Chargement...
                </TableCell>
              </TableRow>
            ) : !prospects?.prospects?.length ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                  Aucun prospect detecte pour le moment.
                  Les prospects apparaitront automatiquement quand un client mentionnera un moyen de paiement ou demandera une livraison.
                </TableCell>
              </TableRow>
            ) : (
              prospects.prospects.map((p) => (
                <TableRow key={p.id}>
                  <TableCell className="font-medium">
                    {p.sender_name || p.sender_id}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {CHANNEL_LABELS[p.channel] ?? p.channel}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className="bg-orange-100 text-orange-800">
                      {p.trigger_keyword}
                    </Badge>
                  </TableCell>
                  <TableCell className="max-w-[200px] truncate" title={p.trigger_message}>
                    {p.trigger_message}
                  </TableCell>
                  <TableCell>
                    <Badge className={STATUS_COLORS[p.status]}>
                      {STATUS_LABELS[p.status] ?? p.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {p.created_at
                      ? new Date(p.created_at).toLocaleDateString("fr-FR", {
                          day: "2-digit",
                          month: "short",
                          hour: "2-digit",
                          minute: "2-digit",
                        })
                      : "-"}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      {p.status === "new" && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleStatusChange(p.id, "contacted")}
                        >
                          Contacte
                        </Button>
                      )}
                      {(p.status === "new" || p.status === "contacted") && (
                        <Button
                          size="sm"
                          variant="default"
                          className="bg-green-600 hover:bg-green-700"
                          onClick={() => handleStatusChange(p.id, "converted")}
                        >
                          Converti
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
