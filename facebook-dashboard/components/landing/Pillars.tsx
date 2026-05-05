import { MessageSquareReply, ShoppingCart, BookOpen } from "lucide-react";

const PILLARS = [
  {
    icon: MessageSquareReply,
    title: "Ne perds plus jamais une vente",
    desc: "Tes clients reçoivent une réponse en moins de 5 secondes, 24/7. Plus aucun message ignoré, plus aucune vente perdue parce que tu dormais ou tu étais en déplacement.",
    color: "from-emerald-500 to-emerald-600",
  },
  {
    icon: ShoppingCart,
    title: "Convertit en commandes",
    desc: "Valina-Bot détecte les intentions d'achat, demande l'adresse, valide le paiement Mvola, Orange Money ou Airtel Money, et crée la commande dans ton dashboard.",
    color: "from-amber-500 to-amber-600",
  },
  {
    icon: BookOpen,
    title: "Apprend ton catalogue",
    desc: "Upload ton fichier Excel ou Google Sheets une seule fois. Valina-Bot apprend tes produits, tailles, prix, photos. Tu modifies, il met à jour automatiquement.",
    color: "from-slate-700 to-slate-900",
  },
];

export function Pillars() {
  return (
    <section className="py-20 md:py-28 bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 tracking-tight">
            Trois choses que tu n&apos;auras plus jamais à faire
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            Pendant que tu sers tes clients en magasin ou que tu dors, ton bot
            répond, vend et organise tes commandes.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {PILLARS.map((pillar) => (
            <div
              key={pillar.title}
              className="group relative rounded-2xl border border-slate-200 bg-white p-8 hover:shadow-xl hover:-translate-y-1 transition"
            >
              <div
                className={`inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${pillar.color} text-white mb-5`}
              >
                <pillar.icon className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-3">
                {pillar.title}
              </h3>
              <p className="text-slate-600 leading-relaxed">{pillar.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
