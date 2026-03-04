"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { useMessages } from "@/hooks/useMessages";

function confidenceBadge(confidence: number) {
  if (confidence >= 0.8) return <Badge className="bg-green-500">Haute</Badge>;
  if (confidence >= 0.5) return <Badge className="bg-yellow-500">Moyenne</Badge>;
  return <Badge className="bg-red-500">Basse</Badge>;
}

export function RecentMessages() {
  const { data, isLoading } = useMessages(10, 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Derniers messages</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p className="text-muted-foreground">Chargement...</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Message</TableHead>
                <TableHead>Réponse</TableHead>
                <TableHead>Confiance</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(data?.messages || []).map((msg) => (
                <TableRow key={msg.id}>
                  <TableCell className="whitespace-nowrap text-sm">
                    {new Date(msg.created_at).toLocaleDateString("fr-FR")}
                  </TableCell>
                  <TableCell className="max-w-[200px] truncate text-sm">
                    {msg.message}
                  </TableCell>
                  <TableCell className="max-w-[200px] truncate text-sm">
                    {msg.response}
                  </TableCell>
                  <TableCell>{confidenceBadge(msg.confidence)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
