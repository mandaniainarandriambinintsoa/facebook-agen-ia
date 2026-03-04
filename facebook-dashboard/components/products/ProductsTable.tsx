"use client";

import { useState, useMemo } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useProducts } from "@/hooks/useProducts";
import { ProductEditDialog } from "./ProductEditDialog";
import { UploadCatalogButton } from "./UploadCatalogButton";
import { Pencil, Trash2, Search } from "lucide-react";
import { toast } from "sonner";
import type { Product } from "@/lib/types";

export function ProductsTable() {
  const { products, isLoading, updateProduct, deleteProduct, deleteProducts, uploadCatalog } =
    useProducts();
  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState<Product | null>(null);
  const [deleting, setDeleting] = useState<Product | null>(null);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [bulkDeleting, setBulkDeleting] = useState(false);

  const filtered = useMemo(() => {
    if (!products) return [];
    if (!search) return products;
    const q = search.toLowerCase();
    return products.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.category.toLowerCase().includes(q)
    );
  }, [products, search]);

  const allSelected = filtered.length > 0 && filtered.every((p) => selected.has(p.id));

  const toggleAll = () => {
    if (allSelected) {
      setSelected(new Set());
    } else {
      setSelected(new Set(filtered.map((p) => p.id)));
    }
  };

  const toggleOne = (id: string) => {
    const next = new Set(selected);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    setSelected(next);
  };

  const handleDelete = async () => {
    if (!deleting) return;
    try {
      await deleteProduct(deleting.id);
      selected.delete(deleting.id);
      setSelected(new Set(selected));
      toast.success("Produit supprime");
    } catch {
      toast.error("Erreur lors de la suppression");
    }
    setDeleting(null);
  };

  const handleBulkDelete = async () => {
    try {
      await deleteProducts(Array.from(selected));
      setSelected(new Set());
      toast.success(`${selected.size} produit(s) supprime(s)`);
    } catch {
      toast.error("Erreur lors de la suppression");
    }
    setBulkDeleting(false);
  };

  const handleSave = async (id: string, data: Partial<Product>) => {
    try {
      await updateProduct(id, data);
      toast.success("Produit mis a jour");
    } catch {
      toast.error("Erreur lors de la mise a jour");
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-4 justify-between">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Rechercher par nom ou categorie..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="flex gap-2">
          {selected.size > 0 && (
            <Button
              variant="destructive"
              size="sm"
              onClick={() => setBulkDeleting(true)}
            >
              <Trash2 className="h-4 w-4 mr-1" />
              Supprimer ({selected.size})
            </Button>
          )}
          <UploadCatalogButton onUpload={uploadCatalog} />
        </div>
      </div>

      {isLoading ? (
        <p className="text-muted-foreground">Chargement...</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[40px]">
                <input
                  type="checkbox"
                  checked={allSelected}
                  onChange={toggleAll}
                  className="h-4 w-4 rounded border-gray-300"
                />
              </TableHead>
              <TableHead>Nom</TableHead>
              <TableHead>Categorie</TableHead>
              <TableHead>Prix</TableHead>
              <TableHead>Description</TableHead>
              <TableHead className="w-[100px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((product) => (
              <TableRow
                key={product.id}
                className={selected.has(product.id) ? "bg-muted/50" : ""}
              >
                <TableCell>
                  <input
                    type="checkbox"
                    checked={selected.has(product.id)}
                    onChange={() => toggleOne(product.id)}
                    className="h-4 w-4 rounded border-gray-300"
                  />
                </TableCell>
                <TableCell className="font-medium">{product.name}</TableCell>
                <TableCell>{product.category}</TableCell>
                <TableCell>{product.price || "-"}</TableCell>
                <TableCell className="max-w-[250px] truncate">
                  {product.description}
                </TableCell>
                <TableCell>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setEditing(product)}
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setDeleting(product)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <ProductEditDialog
        product={editing}
        open={!!editing}
        onClose={() => setEditing(null)}
        onSave={handleSave}
      />

      {/* Single delete */}
      <AlertDialog open={!!deleting} onOpenChange={() => setDeleting(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Supprimer le produit</AlertDialogTitle>
            <AlertDialogDescription>
              Voulez-vous vraiment supprimer &quot;{deleting?.name}&quot; ? Cette
              action est irreversible.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Annuler</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete}>
              Supprimer
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Bulk delete */}
      <AlertDialog open={bulkDeleting} onOpenChange={() => setBulkDeleting(false)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Supprimer {selected.size} produit(s)</AlertDialogTitle>
            <AlertDialogDescription>
              Voulez-vous vraiment supprimer les {selected.size} produit(s) selectionne(s) ?
              Cette action est irreversible.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Annuler</AlertDialogCancel>
            <AlertDialogAction onClick={handleBulkDelete}>
              Supprimer tout
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
