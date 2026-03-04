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
import type { Upload } from "@/lib/types";

interface Props {
  uploads: Upload[] | undefined;
}

export function UploadsHistory({ uploads }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Historique des imports</CardTitle>
      </CardHeader>
      <CardContent>
        {!uploads || uploads.length === 0 ? (
          <p className="text-sm text-muted-foreground">Aucun import</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Fichier</TableHead>
                <TableHead>Produits</TableHead>
                <TableHead>Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {uploads.map((u) => (
                <TableRow key={u.id}>
                  <TableCell>{u.filename}</TableCell>
                  <TableCell>{u.products_count}</TableCell>
                  <TableCell>
                    {new Date(u.created_at).toLocaleDateString("fr-FR")}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
