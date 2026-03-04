import useSWR from "swr";
import { tenantFetcher } from "@/lib/api";
import type { PaginatedMessages, ChartPoint } from "@/lib/types";

export function useMessages(limit = 50, offset = 0) {
  const { data, error, isLoading } = useSWR<PaginatedMessages>(
    `/messages?limit=${limit}&offset=${offset}`,
    tenantFetcher
  );
  return { data, error, isLoading };
}

export function useMessagesChart(days = 30) {
  const { data, error, isLoading } = useSWR<ChartPoint[]>(
    `/messages/chart?days=${days}`,
    tenantFetcher
  );
  return { chartData: data, error, isLoading };
}
