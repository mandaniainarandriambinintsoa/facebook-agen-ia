const PILLARS = [
  {
    n: "01",
    kicker: "Toujours là",
    title: "Aucune vente perdue parce que tu dormais",
    desc: "Le bot répond en 5 secondes, que ce soit à 8h, à 23h ou pendant ton week-end. Tes clients ne s'en vont pas parce que personne n'a vu leur question.",
    accent: "#B7481E",
    big: true,
  },
  {
    n: "02",
    kicker: "Ferme la vente",
    title: "Prend la commande Mvola, Orange ou Airtel automatiquement",
    desc: "Quand un client veut acheter, le bot capte l'adresse, le téléphone, valide le paiement, et crée la commande dans ton dashboard.",
    accent: "#2D4A3E",
    big: false,
  },
  {
    n: "03",
    kicker: "Apprend ton métier",
    title: "Comprend ton catalogue Excel sans formation",
    desc: "Tu uploades ton fichier produits une seule fois. Le bot apprend les noms, prix, tailles, photos. Tu modifies, il met à jour.",
    accent: "#F4B83A",
    big: false,
  },
];

export function Pillars() {
  return (
    <section id="story" className="py-20 md:py-32 bg-[#F5E9D9] relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-5 sm:px-8 relative z-10">
        {/* Section header */}
        <div className="max-w-3xl mb-16 md:mb-24">
          <span className="font-mono text-xs text-[#B7481E] uppercase tracking-widest mb-4 block">
            Le constat
          </span>
          <h2 className="font-display text-4xl md:text-6xl text-[#1A1614] tracking-tight leading-[1.05]">
            Tes clients posent les{" "}
            <span className="italic text-[#B7481E]">mêmes</span> questions,
            <br />
            tu réponds <span className="italic">100 fois</span> par jour,
            <br />
            et le soir tu dors mal.
          </h2>
          <p className="mt-6 text-lg text-[#1A1614]/70 max-w-xl leading-relaxed">
            Trois choses que Valina-Bot fait à ta place, dès le premier jour.
          </p>
        </div>

        {/* Asymmetric grid */}
        <div className="grid md:grid-cols-12 gap-6 md:gap-8">
          {/* Big card - col-span-7 */}
          <article className="md:col-span-7 relative bg-[#1A1614] text-[#FBF6EE] rounded-2xl p-8 md:p-12 overflow-hidden group">
            <div
              aria-hidden
              className="absolute -right-20 -top-20 w-72 h-72 rounded-full"
              style={{ background: `radial-gradient(circle, ${PILLARS[0].accent}55 0%, transparent 70%)` }}
            />
            <span
              className="font-display text-7xl md:text-9xl block leading-none mb-6 opacity-30"
              style={{ color: PILLARS[0].accent }}
            >
              {PILLARS[0].n}
            </span>
            <span className="font-mono text-xs uppercase tracking-widest text-[#F4B83A] mb-3 block">
              {PILLARS[0].kicker}
            </span>
            <h3 className="font-display text-3xl md:text-4xl leading-tight mb-5">
              {PILLARS[0].title}
            </h3>
            <p className="text-[#FBF6EE]/80 text-lg leading-relaxed max-w-md">
              {PILLARS[0].desc}
            </p>
          </article>

          {/* Two stacked cards - col-span-5 */}
          <div className="md:col-span-5 flex flex-col gap-6 md:gap-8">
            {PILLARS.slice(1).map((p) => (
              <article
                key={p.n}
                className="relative flex-1 bg-[#FBF6EE] rounded-2xl p-7 md:p-8 border border-[#1A1614]/10 group hover:border-[#B7481E]/40 transition-colors"
              >
                <div className="flex items-baseline justify-between mb-4">
                  <span
                    className="font-display text-5xl leading-none"
                    style={{ color: p.accent }}
                  >
                    {p.n}
                  </span>
                  <span className="font-mono text-xs uppercase tracking-widest text-[#1A1614]/50">
                    {p.kicker}
                  </span>
                </div>
                <h3 className="font-display text-xl md:text-2xl leading-tight mb-3 text-[#1A1614]">
                  {p.title}
                </h3>
                <p className="text-[#1A1614]/70 leading-relaxed">{p.desc}</p>
              </article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
