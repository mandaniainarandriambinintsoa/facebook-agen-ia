"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { DashboardTourMount } from "@/components/dashboard/DashboardTourMount";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { authenticated } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!authenticated) router.replace("/");
  }, [authenticated, router]);

  if (!authenticated) return null;

  // Tour ne se monte que sur la home dashboard pour pas distraire
  // sur les sous-pages
  const isDashboardHome = pathname === "/dashboard";

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main
          className="flex-1 overflow-auto bg-muted/40 p-6 md:p-8 lg:p-10"
          data-tour="dashboard-home"
        >
          <div className="mx-auto w-full max-w-5xl">{children}</div>
          <footer className="mx-auto mt-12 w-full max-w-5xl border-t pt-4 text-center text-xs text-muted-foreground">
            © 2026 <strong>RANDRIAMBININTSOA MANDANIAINA</strong> — LOT VT 85 HE BIS DB ANDOHANIMANDROSEZA, Antananarivo, Analamanga, 101, Madagascar
          </footer>
        </main>
      </div>
      {isDashboardHome && <DashboardTourMount />}
    </div>
  );
}
