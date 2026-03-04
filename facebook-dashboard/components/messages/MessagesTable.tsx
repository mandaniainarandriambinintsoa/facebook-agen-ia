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
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useMessages } from "@/hooks/useMessages";
import type { Message } from "@/lib/types";
import { ChevronLeft, ChevronRight } from "lucide-react";

function confidenceBadge(confidence: number) {
  if (confidence >= 0.8) return <Badge className="bg-green-500">Haute</Badge>;
  if (confidence >= 0.5) return <Badge className="bg-yellow-500">Moyenne</Badge>;
  return <Badge className="bg-red-500">Basse</Badge>;
}

export function MessagesTable() {
  const [offset, setOffset] = useState(0);
  const [selected, setSelected] = useState<Message | null>(null);
  const limit = 50;
  const { data, isLoading } = useMessages(limit, offset);

  const total = data?.total ?? 0;
  const messages = data?.messages ?? [];
  const page = Math.floor(offset / limit) + 1;
  const totalPages = Math.ceil(total / limit);

  return (
    <>
      {isLoading ? (
        <p className="text-muted-foreground">Chargement...</p>
      ) : (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Expéditeur</TableHead>
                <TableHead>Message</TableHead>
                <TableHead>Réponse</TableHead>
                <TableHead>Canal</TableHead>
                <TableHead>Confiance</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {messages.map((msg) => (
                <TableRow
                  key={msg.id}
                  className="cursor-pointer hover:bg-muted"
                  onClick={() => setSelected(msg)}
                >
                  <TableCell className="whitespace-nowrap text-sm">
                    {new Date(msg.created_at).toLocaleString("fr-FR")}
                  </TableCell>
                  <TableCell className="text-sm">
                    {msg.sender_id}
                  </TableCell>
                  <TableCell className="max-w-[200px] truncate text-sm">
                    {msg.message_text}
                  </TableCell>
                  <TableCell className="max-w-[200px] truncate text-sm">
                    {msg.response_text}
                  </TableCell>
                  <TableCell className="text-sm">{msg.channel}</TableCell>
                  <TableCell>{confidenceBadge(msg.confidence_score)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <div className="flex items-center justify-between mt-4">
            <p className="text-sm text-muted-foreground">
              Page {page} / {totalPages} ({total} messages)
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setOffset(Math.max(0, offset - limit))}
                disabled={offset === 0}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setOffset(offset + limit)}
                disabled={offset + limit >= total}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </>
      )}

      <Dialog open={!!selected} onOpenChange={() => setSelected(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Détail du message</DialogTitle>
          </DialogHeader>
          {selected && (
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Expéditeur
                </p>
                <p>{selected.sender_id}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Message
                </p>
                <p className="whitespace-pre-wrap">{selected.message_text}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Réponse du bot
                </p>
                <p className="whitespace-pre-wrap">{selected.response_text}</p>
              </div>
              <div className="flex gap-4">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Canal
                  </p>
                  <p>{selected.channel}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Confiance
                  </p>
                  {confidenceBadge(selected.confidence_score)}
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Date
                  </p>
                  <p>{new Date(selected.created_at).toLocaleString("fr-FR")}</p>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
