import {
  Clock,
  Languages,
  Image as ImageIcon,
  Bell,
  ShoppingBag,
  MessageCircle,
  Shield,
  TrendingUp,
  PenLine,
} from "lucide-react";

const FEATURES = [
  {
    icon: Clock,
    title: "Réponses 24/7 sur Messenger",
    desc: "Tes clients sont servis nuit et jour, sans temps d'attente, sans compte humain à payer.",
  },
  {
    icon: ShoppingBag,
    title: "Détection commande automatique",
    desc: "Le bot détecte les intentions d'achat (paiement, livraison) et capture l'adresse + téléphone.",
  },
  {
    icon: Languages,
    title: "Bilingue FR + Malgache",
    desc: "Notre moteur RAG comprend les deux langues. Le client écrit en MG, le bot répond en MG.",
  },
  {
    icon: ImageIcon,
    title: "Envoi auto photo produit",
    desc: "Le client demande à voir ? Valina-Bot envoie la photo du produit avec prix et dispo.",
  },
  {
    icon: Bell,
    title: "Notifs prospects chauds",
    desc: "Alerte instantanée Telegram quand un client manifeste l'intention d'acheter.",
  },
  {
    icon: MessageCircle,
    title: "Auto-reply commentaires",
    desc: "Le bot répond en privé aux commentaires sous tes posts (idéal pour les lives).",
  },
  {
    icon: PenLine,
    title: "Custom prompt",
    desc: "Adapte le ton du bot à ta marque. Familier, formel, fun, le bot suit ton style.",
  },
  {
    icon: Shield,
    title: "Conforme RGPD",
    desc: "Hébergé en UE. Pas de transfert de données vers les USA. Registre fourni.",
  },
  {
    icon: TrendingUp,
    title: "Dashboard temps réel",
    desc: "Conversations, commandes, prospects, stats. Tout en un seul endroit.",
  },
];

export function Features() {
  return (
    <section id="features" className="py-20 md:py-28 bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 tracking-tight">
            Tout ce qu&apos;il te faut, rien de plus
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            Pensé pour les commerçants malgaches et francophones, pas pour les
            géants américains.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="rounded-xl border border-slate-200 bg-white p-6 hover:border-emerald-300 hover:bg-emerald-50/30 transition"
            >
              <div className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100 text-emerald-700 mb-4">
                <f.icon className="h-5 w-5" />
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">{f.title}</h3>
              <p className="text-sm text-slate-600 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
