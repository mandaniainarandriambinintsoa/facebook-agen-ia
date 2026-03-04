"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useKnowledge } from "@/hooks/useKnowledge";
import { useProducts } from "@/hooks/useProducts";
import { KnowledgeStatsCards } from "@/components/knowledge/KnowledgeStats";
import { UploadsHistory } from "@/components/knowledge/UploadsHistory";
import { UploadCatalogButton } from "@/components/products/UploadCatalogButton";
import { RefreshCw } from "lucide-react";
import { toast } from "sonner";

export default function KnowledgePage() {
  const { knowledge, isLoading, reindex } = useKnowledge();
  const { uploadCatalog } = useProducts();
  const [reindexing, setReindexing] = useState(false);

  const handleReindex = async () => {
    setReindexing(true);
    try {
      await reindex();
      toast.success("Réindexation terminée");
    } catch {
      toast.error("Erreur lors de la réindexation");
    } finally {
      setReindexing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Base de connaissances</h2>
        <div className="flex gap-2">
          <UploadCatalogButton onUpload={uploadCatalog} />
          <Button variant="outline" onClick={handleReindex} disabled={reindexing}>
            <RefreshCw className={`h-4 w-4 mr-2 ${reindexing ? "animate-spin" : ""}`} />
            {reindexing ? "Réindexation..." : "Réindexer"}
          </Button>
        </div>
      </div>
      <KnowledgeStatsCards knowledge={knowledge} isLoading={isLoading} />
      <UploadsHistory uploads={knowledge?.uploads} />
    </div>
  );
}
