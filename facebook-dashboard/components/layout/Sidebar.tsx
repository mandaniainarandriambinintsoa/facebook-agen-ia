"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  MessageSquare,
  Package,
  Brain,
  Settings,
  Flame,
  ShoppingCart,
  Plug,
  Wand2,
} from "lucide-react";

const links = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, tour: "nav-dashboard" },
  { href: "/dashboard/prospects", label: "Prospects", icon: Flame, tour: "nav-prospects" },
  { href: "/dashboard/orders", label: "Commandes", icon: ShoppingCart, tour: "nav-orders" },
  { href: "/dashboard/messages", label: "Messages", icon: MessageSquare, tour: "nav-messages" },
  { href: "/dashboard/products", label: "Produits", icon: Package, tour: "nav-products" },
  { href: "/dashboard/knowledge", label: "Connaissances", icon: Brain, tour: "nav-knowledge" },
  { href: "/dashboard/platforms", label: "Plateformes", icon: Plug, tour: "nav-platforms" },
  { href: "/dashboard/config", label: "Configuration", icon: Settings, tour: "nav-config" },
  { href: "/onboarding", label: "Refaire la configuration", icon: Wand2, tour: "nav-onboarding" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex w-64 flex-col border-r bg-card">
      <div className="p-6">
        <h1 className="text-lg font-semibold">Agent IA</h1>
        <p className="text-sm text-muted-foreground">Dashboard</p>
      </div>
      <nav className="flex-1 px-3 space-y-1">
        {links.map((link) => {
          const isActive =
            link.href === "/dashboard"
              ? pathname === "/dashboard"
              : pathname.startsWith(link.href);
          return (
            <Link
              key={link.href}
              href={link.href}
              data-tour={link.tour}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <link.icon className="h-4 w-4" />
              {link.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
