import useSWR from "swr";
import { tenantFetcher, tenantApi } from "@/lib/api";

interface Prospect {
  id: string;
  sender_id: string;
  sender_name: string;
  channel: string;
  trigger_keyword: string;
  trigger_message: string;
  product_interest: string;
  status: string;
  notes: string;
  created_at: string;
}

interface ProspectsResponse {
  total: number;
  prospects: Prospect[];
}

interface ProspectsStats {
  today: number;
  this_week: number;
  total: number;
  by_status: {
    new: number;
    contacted: number;
    converted: number;
    lost: number;
  };
  per_day: { date: string; count: number }[];
}

export function useProspects(status?: string) {
  const params = status ? `?status=${status}` : "";
  const { data, error, isLoading, mutate } = useSWR<ProspectsResponse>(
    `/prospects${params}`,
    tenantFetcher
  );
  return { prospects: data, error, isLoading, mutate };
}

export function useProspectsStats() {
  const { data, error, isLoading } = useSWR<ProspectsStats>(
    "/prospects/stats",
    tenantFetcher
  );
  return { stats: data, error, isLoading };
}

export async function updateProspectStatus(
  prospectId: string,
  status: string,
  notes?: string
) {
  return tenantApi(`/prospects/${prospectId}`, {
    method: "PUT",
    body: JSON.stringify({ status, notes }),
  });
}
