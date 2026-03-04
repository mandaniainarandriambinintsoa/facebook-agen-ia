const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

function getTenantId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("tenant_id");
}

export async function api<T = unknown>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (res.status === 401) {
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
      localStorage.removeItem("tenant_id");
      window.location.href = "/";
    }
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }

  return res.json();
}

export function tenantApi<T = unknown>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const tenantId = getTenantId();
  if (!tenantId) throw new Error("No tenant selected");
  return api<T>(`/api/tenants/${tenantId}${path}`, options);
}

export function apiUrl(path: string): string {
  return `${API_URL}${path}`;
}

export const fetcher = <T = unknown>(path: string) => api<T>(path);
export const tenantFetcher = <T = unknown>(path: string) => tenantApi<T>(path);
