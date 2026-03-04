import useSWR from "swr";
import { tenantFetcher, tenantApi } from "@/lib/api";
import type { KnowledgeStats } from "@/lib/types";

export function useKnowledge() {
  const { data, error, isLoading, mutate } = useSWR<KnowledgeStats>(
    "/knowledge-stats",
    tenantFetcher
  );

  const reindex = async () => {
    await tenantApi("/reindex", { method: "POST" });
    mutate();
  };

  const clearKnowledge = async () => {
    await tenantApi("/knowledge", { method: "DELETE" });
    mutate();
  };

  return { knowledge: data, error, isLoading, reindex, clearKnowledge, mutate };
}
