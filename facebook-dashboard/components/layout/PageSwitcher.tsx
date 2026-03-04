"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useTenants } from "@/hooks/useTenants";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { api } from "@/lib/api";
import { saveToken } from "@/lib/auth";

export function PageSwitcher() {
  const { tenantId, switchTenant } = useAuth();
  const { tenants } = useTenants();

  if (!tenants || tenants.length <= 1) return null;

  const handleSwitch = async (id: string) => {
    try {
      const res = await api<{ access_token: string }>(
        `/api/tenants/switch/${id}`,
        { method: "POST" }
      );
      saveToken(res.access_token);
      switchTenant(id);
      window.location.reload();
    } catch {
      // ignore
    }
  };

  return (
    <Select value={tenantId || ""} onValueChange={handleSwitch}>
      <SelectTrigger className="w-[200px]">
        <SelectValue placeholder="Sélectionner une page" />
      </SelectTrigger>
      <SelectContent>
        {tenants.map((t) => (
          <SelectItem key={t.id} value={String(t.id)}>
            {t.page_name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
