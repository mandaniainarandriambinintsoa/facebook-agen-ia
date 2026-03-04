import useSWR from "swr";
import { fetcher } from "@/lib/api";
import type { Tenant } from "@/lib/types";

export function useTenants() {
  const { data, error, isLoading } = useSWR<Tenant[]>(
    "/api/tenants/me",
    fetcher
  );
  return { tenants: data, error, isLoading };
}
