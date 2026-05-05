import { StepBadge } from "./StepBadge";

const FEATURES = [
  {
    title: "Réponses 24/7 sur Messenger",
    desc: "Tes clients reçoivent une réponse en moins de 5 secondes, à toute heure.",
    big: true,
  },
  {
    title: "Détection commande automatique",
    desc: "Quand un client parle paiement ou livraison, le bot capte adresse et numéro.",
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
    <section className="py-24 md:py-36 bg-[#0F0E0C] text-[#FAF9F5] relative overflow-hidden">
      <div className="max-w-6xl mx-auto px-5 sm:px-8">
        <div className="grid md:grid-cols-12 gap-8 mb-20">
          <div className="md:col-span-7">
            <div className="mb-6">
              <StepBadge variant="dark">Ce qu&apos;il y a dedans</StepBadge>
            </div>
            <h2 className="font-display text-4xl md:text-6xl tracking-[-0.02em] leading-[1.0]">
              Tout ce qu&apos;il te faut.
              <br />
              <em className="not-italic font-display italic text-[#F4B83A]">Rien de plus</em>
              <span className="text-[#F4B83A]">.</span>
            </h2>
          </div>
          <div className="md:col-span-5 md:pt-8">
            <p className="text-[#FAF9F5]/70 text-lg leading-relaxed">
              Pensé pour les commerçants malgaches et francophones. Pas pour les
              géants américains qui veulent te facturer en dollars.
            </p>
          </div>
        </div>

        {/* Features asymmetric grid */}
        <div className="grid md:grid-cols-12 gap-5">
          {FEATURES.map((f, i) => {
            const span = f.big ? "md:col-span-6" : "md:col-span-3";
            return (
              <article
                key={f.title}
                className={`${span} relative border border-[#FAF9F5]/12 rounded-2xl p-6 md:p-8 hover:border-[#F4B83A]/50 hover:bg-[#FAF9F5]/[0.025] transition-all duration-300`}
              >
                <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#F4B83A] block mb-5">
                  {String(i + 1).padStart(2, "0")} /09
                </span>
                <h3
                  className={`font-display ${
                    f.big ? "text-2xl md:text-[1.75rem]" : "text-lg md:text-xl"
                  } leading-tight mb-3 tracking-[-0.01em]`}
                >
                  {f.title}
                </h3>
                <p className="text-[#FAF9F5]/70 text-sm leading-relaxed">{f.desc}</p>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
