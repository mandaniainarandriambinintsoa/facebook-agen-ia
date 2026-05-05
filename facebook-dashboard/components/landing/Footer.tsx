import Link from "next/link";

const COLUMNS = [
  {
    title: "Produit",
    links: [
      { href: "#story", label: "Le constat" },
      { href: "#how", label: "Comment ça marche" },
      { href: "#pricing", label: "Tarifs" },
      { href: "#faq", label: "Questions" },
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
    <footer className="bg-[#0F0E0C] text-[#FAF9F5]">
      <div className="max-w-6xl mx-auto px-5 sm:px-8 py-16">
        <div className="grid md:grid-cols-12 gap-10 mb-12">
          <div className="md:col-span-5">
            <Link
              href="/"
              className="font-display text-3xl italic font-medium inline-block mb-4"
            >
              Valina<span className="text-[#F4B83A]">.</span>
            </Link>
            <p className="text-[#FAF9F5]/70 max-w-sm leading-relaxed">
              L&apos;agent IA qui répond à tes clients sur Messenger Facebook
              24/7. Made in Madagascar, pour les commerçants malgaches et
              francophones.
            </p>
          </div>

          {COLUMNS.map((col) => (
            <div key={col.title} className="md:col-span-2">
              <h4 className="font-mono text-[11px] uppercase tracking-[0.2em] text-[#F4B83A] mb-5">
                {col.title}
              </h4>
              <ul className="space-y-3">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <Link
                      href={l.href}
                      className="text-[#FAF9F5]/70 hover:text-[#FAF9F5] transition-colors text-sm"
                    >
                      {l.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          <div className="md:col-span-1" />
        </div>

        <div className="pt-8 border-t border-[#FAF9F5]/15 flex flex-col md:flex-row gap-6 items-start md:items-center justify-between text-xs text-[#FAF9F5]/50">
          <div className="space-y-1">
            <p>
              © 2026{" "}
              <strong className="text-[#FAF9F5]/70">RANDRIAMBININTSOA MANDANIAINA</strong>
            </p>
            <p>
              LOT VT 85 HE BIS DB ANDOHANIMANDROSEZA, Antananarivo, Madagascar ·{" "}
              <a
                href="mailto:contact@manda-ia.com"
                className="underline hover:text-[#FAF9F5]"
              >
                contact@manda-ia.com
              </a>
            </p>
          </div>
          <p className="font-display italic text-[#F4B83A]">Made in Madagascar</p>
        </div>
      </div>
    </footer>
  );
}
