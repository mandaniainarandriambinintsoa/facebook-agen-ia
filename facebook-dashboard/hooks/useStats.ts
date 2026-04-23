import useSWR from "swr";
import { tenantFetcher } from "@/lib/api";
import type { Stats } from "@/lib/types";

export function useStats(days = 30) {
  const { data, error, isLoading } = useSWR<Stats>(
    `/stats?days=${days}`,
    tenantFetcher
  );
  return { stats: data, error, isLoading };
}
