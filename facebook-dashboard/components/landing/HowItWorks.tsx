import { StepBadge, NumberCircle } from "./StepBadge";
import { DashedLine } from "./DashedLine";

const STEPS = [
  {
    n: 1,
    roman: "I.",
    title: "Connecte ta page Facebook",
    desc: "Login en 1 clic via OAuth Facebook. On synchronise ta page Messenger automatiquement, sans toucher au code.",
    detail: "OAuth · 1 clic · 30 secondes",
  },
  {
    n: 2,
    roman: "II.",
    title: "Upload ton catalogue Excel",
    desc: "Glisse ton fichier produits. Valina-Bot apprend les noms, prix, tailles et photos via notre moteur RAG bilingue.",
    detail: "Excel ou CSV · Apprentissage instantané",
  },
  {
    n: 3,
    roman: "III.",
    title: "Active et dors tranquille",
    desc: "Tu testes un message, tu valides, tu actives. Le bot commence à répondre. Tu vois tout en direct dans ton dashboard.",
    detail: "Test inclus · Activation immédiate",
  },
];

export function HowItWorks() {
  return (
    <section id="how" className="py-24 md:py-36 bg-[#F0F2F5] relative overflow-hidden">
      <div className="max-w-6xl mx-auto px-5 sm:px-8 relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <div className="mb-6">
            <StepBadge>Comment ça marche</StepBadge>
          </div>
          <h2 className="text-4xl md:text-6xl text-[#1C1E21] tracking-[-0.02em] leading-[1.0]">
            Trois étapes,
            <br />
            <em className="not-italic italic text-[#1877F2]">dix minutes</em>,<br />
            zéro ligne de code<span className="text-[#1877F2]">.</span>
          </h2>
        </div>

        {/* Steps with horizontal dashed connectors */}
        <div className="grid md:grid-cols-3 gap-12 md:gap-8 relative">
          {STEPS.map((step, i) => (
            <article key={step.n} className="relative">
              {/* Dashed connector to next step (desktop only) */}
              {i < STEPS.length - 1 && (
                <DashedLine
                  variant="step-arrow"
                  className="hidden md:block absolute top-8 -right-12 w-24 h-12 z-0 text-[#1C1E21]"
                  color="#1C1E21"
                />
              )}

              <div className="relative z-10 bg-[#F7F8FA] rounded-3xl p-8 md:p-10 border border-[#1C1E21]/8 h-full">
                <div className="flex items-baseline justify-between mb-6">
                  <span className="italic text-5xl md:text-6xl text-[#1877F2] leading-none">
                    {step.roman}
                  </span>
                  <NumberCircle n={step.n} color="ink" size="sm" />
                </div>

                <h3 className="text-2xl md:text-[1.75rem] text-[#1C1E21] leading-tight mb-4 tracking-[-0.01em]">
                  {step.title}
                </h3>

                <p className="text-[#1C1E21]/75 leading-relaxed mb-6">{step.desc}</p>

                <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#1C1E21]/45 block">
                  {step.detail}
                </span>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
