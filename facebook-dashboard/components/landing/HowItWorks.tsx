const STEPS = [
  {
    n: "I.",
    title: "Connecte ta page Facebook",
    desc: "Login en 1 clic via OAuth. On synchronise ta page Messenger et on configure les webhooks. Aucun code à toucher.",
    detail: "OAuth Meta · 1 clic · 30 secondes",
  },
  {
    n: "II.",
    title: "Upload ton catalogue Excel",
    desc: "Glisse-dépose ton fichier produits. Valina-Bot apprend les noms, prix, tailles et photos via notre moteur RAG bilingue Français + Malgache.",
    detail: "Excel ou Google Sheets · Apprentissage instantané",
  },
  {
    n: "III.",
    title: "Active et dors tranquille",
    desc: "Tu testes un message, tu valides, tu actives. Le bot commence à répondre. Tu vois tout en temps réel dans ton dashboard.",
    detail: "Test inclus · Activation immédiate · Dashboard live",
  },
];

export function HowItWorks() {
  return (
    <section id="how" className="py-20 md:py-32 bg-[#FBF6EE] relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-5 sm:px-8">
        <div className="max-w-3xl mb-16">
          <span className="font-mono text-xs text-[#2D4A3E] uppercase tracking-widest mb-4 block">
            Comment ça marche
          </span>
          <h2 className="font-display text-4xl md:text-5xl text-[#1A1614] tracking-tight leading-[1.05]">
            Trois étapes,{" "}
            <span className="italic text-[#2D4A3E]">dix minutes</span>,<br />
            zéro ligne de code.
          </h2>
        </div>

        {/* Editorial timeline */}
        <div className="relative space-y-12 md:space-y-0 md:grid md:grid-cols-3 md:gap-px md:bg-[#1A1614]/10">
          {STEPS.map((step, i) => (
            <article
              key={step.n}
              className="relative bg-[#FBF6EE] md:p-8 md:py-12 md:hover:bg-[#F5E9D9] transition-colors duration-300 group"
            >
              <div className="flex items-baseline gap-4 mb-6">
                <span className="font-display italic text-5xl md:text-6xl text-[#B7481E] leading-none">
                  {step.n}
                </span>
                <span className="h-px flex-1 bg-[#1A1614]/15 mt-6" />
              </div>

              <h3 className="font-display text-2xl md:text-3xl text-[#1A1614] leading-tight mb-4">
                {step.title}
              </h3>

              <p className="text-[#1A1614]/70 leading-relaxed mb-6 max-w-md">
                {step.desc}
              </p>

              <span className="font-mono text-xs uppercase tracking-widest text-[#1A1614]/50 block">
                {step.detail}
              </span>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
