"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Menu, X } from "lucide-react";

const NAV_ITEMS = [
  { href: "#story", label: "Le constat" },
  { href: "#how", label: "Comment ça marche" },
  { href: "#pricing", label: "Tarifs" },
  { href: "#faq", label: "Questions" },
];

export function LandingHeader() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 inset-x-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-[#F7F8FA]/90 backdrop-blur-md border-b border-[#1C1E21]/8"
          : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-5 sm:px-8 h-16 flex items-center justify-between">
        <Link
          href="/"
          className="text-2xl font-semibold text-[#1C1E21] tracking-tight italic"
        >
          Valina<span className="text-[#1877F2]">.</span>
        </Link>

        <nav className="hidden md:flex items-center gap-8 text-sm text-[#1C1E21]/70">
          {NAV_ITEMS.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="hover:text-[#1877F2] transition-colors duration-200"
            >
              {item.label}
            </a>
          ))}
        </nav>

        <div className="hidden md:flex items-center gap-4">
          <Link
            href="/login"
            className="text-sm text-[#1C1E21]/70 hover:text-[#1C1E21] transition-colors"
          >
            Se connecter
          </Link>
          <Link
            href="/login"
            className="inline-flex items-center gap-2 rounded-full bg-[#1C1E21] text-[#F7F8FA] px-5 py-2.5 text-sm font-medium hover:bg-[#1877F2] transition-colors duration-300"
          >
            Essai gratuit
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-[#F4B83A]" />
          </Link>
        </div>

        <button
          aria-label="Menu"
          className="md:hidden inline-flex h-10 w-10 items-center justify-center rounded-full hover:bg-[#1C1E21]/5"
          onClick={() => setOpen((v) => !v)}
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {open && (
        <div className="md:hidden border-t border-[#1C1E21]/10 bg-[#F7F8FA]">
          <div className="px-5 py-6 flex flex-col gap-4 text-base">
            {NAV_ITEMS.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="text-[#1C1E21]/80 hover:text-[#1877F2]"
                onClick={() => setOpen(false)}
              >
                {item.label}
              </a>
            ))}
            <Link href="/login" className="text-[#1C1E21]/80">
              Se connecter
            </Link>
            <Link
              href="/login"
              className="inline-flex items-center justify-center gap-2 rounded-full bg-[#1C1E21] text-[#F7F8FA] px-5 py-3 text-sm font-medium"
            >
              Essai gratuit
              <span className="inline-block h-1.5 w-1.5 rounded-full bg-[#F4B83A]" />
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
