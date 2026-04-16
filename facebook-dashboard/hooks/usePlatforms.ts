import useSWR from "swr";
import { tenantFetcher, tenantApi } from "@/lib/api";
import type { TenantPlatform } from "@/lib/types";

export function usePlatforms() {
  const { data, error, isLoading, mutate } = useSWR<TenantPlatform[]>(
    "/platforms",
    tenantFetcher
  );

  const connectWhatsapp = async (payload: {
    phone_number_id: string;
    access_token: string;
    display_name?: string;
  }) => {
    await tenantApi("/connect-whatsapp", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    mutate();
  };

  return {
    platforms: data,
    error,
    isLoading,
    mutate,
    connectWhatsapp,
  };
}
