import useSWR from "swr";
import { tenantFetcher, tenantApi } from "@/lib/api";
import type { BotConfig } from "@/lib/types";

export function useConfig() {
  const { data, error, isLoading, mutate } = useSWR<BotConfig>(
    "/config",
    tenantFetcher
  );

  const updateConfig = async (config: BotConfig) => {
    await tenantApi("/config", {
      method: "PUT",
      body: JSON.stringify(config),
    });
    mutate();
  };

  return { config: data, error, isLoading, updateConfig };
}
