import Link from "next/link";
import { Bot } from "lucide-react";

const COLUMNS = [
  {
    title: "Produit",
    links: [
      { href: "#features", label: "Fonctionnalités" },
      { href: "#pricing", label: "Tarifs" },
      { href: "#how", label: "Comment ça marche" },
      { href: "#faq", label: "FAQ" },
    ],
  },
  {
    title: "Société",
    links: [
      { href: "mailto:contact@manda-ia.com", label: "Contact" },
      { href: "/login", label: "Se connecter" },
    ],
  },
  {
    title: "Légal",
    links: [
      { href: "/privacy", label: "Confidentialité" },
      { href: "/terms", label: "Conditions" },
      { href: "/data-deletion", label: "Suppression données" },
    ],
  },
];

export function LandingFooter() {
  return (
    <footer className="bg-slate-50 border-t border-slate-200">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-14">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <Link href="/" className="flex items-center gap-2 font-semibold text-slate-900">
              <span className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-slate-900 to-emerald-600 text-white">
                <Bot className="h-5 w-5" />
              </span>
              <span>Valina-Bot</span>
            </Link>
            <p className="mt-4 text-sm text-slate-600 max-w-xs">
              L&apos;agent IA qui répond à tes clients sur Facebook, Instagram
              et WhatsApp 24/7.
            </p>
          </div>

          {COLUMNS.map((col) => (
            <div key={col.title}>
              <h4 className="font-semibold text-slate-900 text-sm mb-4">
                {col.title}
              </h4>
              <ul className="space-y-2">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <Link
                      href={l.href}
                      className="text-sm text-slate-600 hover:text-slate-900 transition"
                    >
                      {l.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 pt-8 border-t border-slate-200 flex flex-col md:flex-row gap-4 items-center justify-between text-xs text-slate-500">
          <div className="space-y-1 text-center md:text-left">
            <p>
              © 2026 <strong>RANDRIAMBININTSOA MANDANIAINA</strong> · Tous droits réservés
            </p>
            <p>
              LOT VT 85 HE BIS DB ANDOHANIMANDROSEZA, Antananarivo, Madagascar ·{" "}
              <a href="mailto:contact@manda-ia.com" className="underline">
                contact@manda-ia.com
              </a>
            </p>
          </div>
          <p className="text-slate-400">Made in Madagascar</p>
        </div>
      </div>
    </footer>
  );
}
