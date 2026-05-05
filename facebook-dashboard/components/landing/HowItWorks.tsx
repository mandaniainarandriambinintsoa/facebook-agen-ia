import { Facebook, Upload, Zap } from "lucide-react";

const STEPS = [
  {
    n: "1",
    icon: Facebook,
    title: "Connecte ta page Facebook",
    desc: "Login en 1 clic via Facebook OAuth. Pas de code, pas de configuration technique. On récupère ta page et on configure les webhooks Messenger automatiquement.",
  },
  {
    n: "2",
    icon: Upload,
    title: "Upload ton catalogue",
    desc: "Glisse-dépose ton fichier Excel ou CSV (produits, prix, tailles, photos). Valina-Bot apprend ton catalogue en quelques secondes via notre moteur RAG bilingue FR + Malgache.",
  },
  {
    n: "3",
    icon: Zap,
    title: "Active le bot",
    desc: "Test un message à toi-même pour valider, puis active. Tes clients commencent à recevoir des réponses immédiatement. Tu vois tout dans le dashboard en temps réel.",
  },
];

export function HowItWorks() {
  return (
    <section id="how" className="py-20 md:py-28 bg-slate-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 tracking-tight">
            Comment ça marche
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            Trois étapes, dix minutes, zéro ligne de code.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {STEPS.map((step) => (
            <div key={step.n} className="relative">
              <div className="bg-white border border-slate-200 rounded-2xl p-8 h-full">
                <div className="flex items-center justify-between mb-6">
                  <span className="text-5xl font-bold bg-gradient-to-br from-emerald-600 to-amber-500 bg-clip-text text-transparent">
                    {step.n}
                  </span>
                  <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-slate-700">
                    <step.icon className="h-5 w-5" />
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-3">
                  {step.title}
                </h3>
                <p className="text-slate-600 leading-relaxed">{step.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
