"use client";

import { useForm, Resolver } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import type { Product } from "@/lib/types";

interface FormValues {
  name: string;
  description: string;
  price: string;
  category: string;
  image_url: string;
}

const schema = z.object({
  name: z.string().min(1, "Nom requis"),
  description: z.string(),
  price: z.string(),
  category: z.string(),
  image_url: z.string(),
});

interface Props {
  product: Product | null;
  open: boolean;
  onClose: () => void;
  onSave: (id: string, data: Partial<Product>) => Promise<void>;
}

export function ProductEditDialog({ product, open, onClose, onSave }: Props) {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormValues>({
    resolver: zodResolver(schema) as Resolver<FormValues>,
    values: product
      ? {
          name: product.name,
          description: product.description,
          price: product.price || "",
          category: product.category || "",
          image_url: product.image_url || "",
        }
      : undefined,
  });

  const onSubmit = async (data: FormValues) => {
    if (!product) return;
    await onSave(product.id, data);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Modifier le produit</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <Label>Nom</Label>
            <Input {...register("name")} />
            {errors.name && (
              <p className="text-sm text-red-500">{errors.name.message}</p>
            )}
          </div>
          <div>
            <Label>Description</Label>
            <Textarea {...register("description")} rows={3} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Prix</Label>
              <Input {...register("price")} placeholder="ex: 15000 Ar" />
            </div>
            <div>
              <Label>Catégorie</Label>
              <Input {...register("category")} />
            </div>
          </div>
          <div>
            <Label>URL image</Label>
            <Input {...register("image_url")} />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Annuler
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Enregistrement..." : "Enregistrer"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
