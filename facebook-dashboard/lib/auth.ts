import { jwtDecode } from "jwt-decode";

interface JwtPayload {
  sub: string;
  tenant_id?: number;
  exp: number;
}

export function saveToken(token: string) {
  localStorage.setItem("token", token);
  try {
    const decoded = jwtDecode<JwtPayload>(token);
    if (decoded.tenant_id) {
      localStorage.setItem("tenant_id", String(decoded.tenant_id));
    }
  } catch {
    // ignore decode errors
  }
}

export function getToken(): string | null {
  return localStorage.getItem("token");
}

export function getTenantId(): string | null {
  return localStorage.getItem("tenant_id");
}

export function setTenantId(id: string) {
  localStorage.setItem("tenant_id", id);
}

export function isAuthenticated(): boolean {
  const token = getToken();
  if (!token) return false;
  try {
    const decoded = jwtDecode<JwtPayload>(token);
    return decoded.exp * 1000 > Date.now();
  } catch {
    return false;
  }
}

export function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("tenant_id");
}
