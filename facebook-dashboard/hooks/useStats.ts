import useSWR from "swr";
import { tenantFetcher } from "@/lib/api";
import type { Stats } from "@/lib/types";

export function useStats() {
  const { data, error, isLoading } = useSWR<Stats>("/stats", tenantFetcher);
  return { stats: data, error, isLoading };
}
