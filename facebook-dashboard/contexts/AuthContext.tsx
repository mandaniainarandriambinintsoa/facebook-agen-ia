"use client";

import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from "react";
import { saveToken, getToken, getTenantId, setTenantId, isAuthenticated, logout as authLogout } from "@/lib/auth";

interface AuthContextType {
  token: string | null;
  tenantId: string | null;
  authenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
  switchTenant: (id: string) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [tenantId, setTenant] = useState<string | null>(null);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    setToken(getToken());
    setTenant(getTenantId());
    setAuthenticated(isAuthenticated());
  }, []);

  const login = useCallback((newToken: string) => {
    saveToken(newToken);
    setToken(newToken);
    setTenant(getTenantId());
    setAuthenticated(true);
  }, []);

  const logout = useCallback(() => {
    authLogout();
    setToken(null);
    setTenant(null);
    setAuthenticated(false);
  }, []);

  const switchTenant = useCallback((id: string) => {
    setTenantId(id);
    setTenant(id);
  }, []);

  return (
    <AuthContext.Provider value={{ token, tenantId, authenticated, login, logout, switchTenant }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be inside AuthProvider");
  return ctx;
}
