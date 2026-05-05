const FEATURES = [
  {
    title: "Réponses 24/7 sur Messenger",
    desc: "Tes clients reçoivent une réponse en moins de 5 secondes, à toute heure.",
    big: true,
  },
  {
    title: "Détection commande automatique",
    desc: "Quand un client parle paiement ou livraison, le bot capte l'adresse et le numéro.",
  },
  {
    title: "Bilingue Français + Malgache",
    desc: "RAG multilingue. Le client écrit en MG, le bot répond en MG.",
  },
  {
    title: "Photos produits envoyées",
    desc: "Quand le client demande à voir, le bot envoie automatiquement la photo.",
  },
  {
    title: "Notifs prospects chauds",
    desc: "Alerte instantanée Telegram quand un client manifeste une intention d'achat.",
    big: true,
  },
  {
    title: "Auto-reply commentaires",
    desc: "Le bot répond en privé aux commentaires sous tes posts (idéal pour les lives).",
  },
  {
    title: "Custom prompt",
    desc: "Adapte le ton du bot à ta marque. Familier, formel, fun.",
  },
  {
    title: "Conforme RGPD",
    desc: "Hébergé en Europe. Pas de transfert de données vers les USA.",
  },
  {
    title: "Dashboard temps réel",
    desc: "Conversations, commandes, prospects, stats. Tout en un seul endroit.",
  },
];

export function Features() {
  return (
    <section className="py-20 md:py-32 bg-[#1A1614] text-[#FBF6EE] relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-5 sm:px-8">
        <div className="grid md:grid-cols-12 gap-8 mb-16">
          <div className="md:col-span-7">
            <span className="font-mono text-xs text-[#F4B83A] uppercase tracking-widest mb-4 block">
              Ce qu&apos;il y a dans la boîte
            </span>
            <h2 className="font-display text-4xl md:text-6xl tracking-tight leading-[1.05]">
              Tout ce qu&apos;il te faut.{" "}
              <span className="italic text-[#F4B83A]">Rien de plus.</span>
            </h2>
          </div>
          <div className="md:col-span-5 md:pt-8">
            <p className="text-[#FBF6EE]/70 text-lg leading-relaxed">
              Pensé pour les commerçants malgaches et francophones. Pas pour les
              géants américains qui veulent te facturer en dollars.
            </p>
          </div>
        </div>

        {/* Features asymmetric grid */}
        <div className="grid md:grid-cols-12 gap-6">
          {FEATURES.map((f, i) => {
            const span = f.big ? "md:col-span-6" : "md:col-span-3";
            return (
              <article
                key={f.title}
                className={`${span} relative border border-[#FBF6EE]/15 rounded-xl p-6 md:p-7 hover:border-[#F4B83A]/50 hover:bg-[#FBF6EE]/[0.03] transition-all duration-300 group`}
              >
                <span className="font-mono text-xs text-[#F4B83A] block mb-4">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <h3 className={`font-display ${f.big ? "text-2xl md:text-3xl" : "text-lg md:text-xl"} leading-tight mb-3`}>
                  {f.title}
                </h3>
                <p className="text-[#FBF6EE]/70 text-sm leading-relaxed">
                  {f.desc}
                </p>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
