"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
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
import { useKnowledge } from "@/hooks/useKnowledge";
import { useProducts } from "@/hooks/useProducts";
import { KnowledgeStatsCards } from "@/components/knowledge/KnowledgeStats";
import { UploadsHistory } from "@/components/knowledge/UploadsHistory";
import { UploadCatalogButton } from "@/components/products/UploadCatalogButton";
import { RefreshCw, Trash2 } from "lucide-react";
import { toast } from "sonner";

export default function KnowledgePage() {
  const { knowledge, isLoading, reindex, clearKnowledge } = useKnowledge();
  const { uploadCatalog } = useProducts();
  const [reindexing, setReindexing] = useState(false);
  const [confirmClear, setConfirmClear] = useState(false);

  const handleReindex = async () => {
    setReindexing(true);
    try {
      await reindex();
      toast.success("Reindexation terminee");
    } catch {
      toast.error("Erreur lors de la reindexation");
    } finally {
      setReindexing(false);
    }
  };

  const handleClear = async () => {
    try {
      await clearKnowledge();
      toast.success("Base de connaissances videe");
    } catch {
      toast.error("Erreur lors de la suppression");
    }
    setConfirmClear(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Base de connaissances</h2>
        <div className="flex gap-2">
          <UploadCatalogButton onUpload={uploadCatalog} />
          <Button variant="outline" onClick={handleReindex} disabled={reindexing}>
            <RefreshCw className={`h-4 w-4 mr-2 ${reindexing ? "animate-spin" : ""}`} />
            {reindexing ? "Reindexation..." : "Reindexer"}
          </Button>
          {(knowledge?.embeddings_count ?? 0) > 0 && (
            <Button variant="destructive" onClick={() => setConfirmClear(true)}>
              <Trash2 className="h-4 w-4 mr-2" />
              Vider
            </Button>
          )}
        </div>
      </div>
      <KnowledgeStatsCards knowledge={knowledge} isLoading={isLoading} />
      <UploadsHistory uploads={knowledge?.uploads} />

      <AlertDialog open={confirmClear} onOpenChange={() => setConfirmClear(false)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Vider la base de connaissances</AlertDialogTitle>
            <AlertDialogDescription>
              Cela supprimera tous les {knowledge?.embeddings_count ?? 0} embeddings.
              Le bot ne pourra plus repondre aux questions jusqu&apos;a la prochaine indexation.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Annuler</AlertDialogCancel>
            <AlertDialogAction onClick={handleClear}>
              Vider
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
