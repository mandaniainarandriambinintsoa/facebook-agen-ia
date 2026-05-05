import { StepBadge, NumberCircle } from "./StepBadge";
import { DashedLine } from "./DashedLine";
import { IllustrationFrame } from "./IllustrationFrame";
import { EditorialBubble } from "./EditorialBubble";

const PILLARS = [
  {
    n: 1,
    color: "terracotta" as const,
    badge: "Acquisition",
    title: "Aucune vente perdue parce que tu dormais",
    desc: "Ton client envoie un message à 23h. À 23h une seconde plus tard, il a sa réponse. Pas de message ignoré, pas de client qui s'en va chez le voisin pendant que tu dors.",
    illustration: {
      src: "/illustrations/customer-night.jpg",
      alt: "Cliente qui chatte avec le bot Valina la nuit",
    },
    quote: { text: "Mbola misy ve taille M ?", time: "23:42" },
    align: "right" as const,
  },
  {
    n: 2,
    color: "forest" as const,
    badge: "Conversion",
    title: "Prend la commande Mvola, Orange ou Airtel automatiquement",
    desc: "Quand un client veut acheter, le bot capte son adresse, son numéro, valide le paiement, et crée la commande dans ton dashboard. Tu n'as qu'à préparer le colis.",
    illustration: {
      src: "/illustrations/delivery-mvola.jpg",
      alt: "Livreur Tana qui livre une commande validée Mvola",
    },
    quote: { text: "Adresse : Lot 42 Andoharanofotsy. Mvola validé ✓", time: "16:55" },
    align: "left" as const,
  },
  {
    n: 3,
    color: "sun" as const,
    badge: "Apprentissage",
    title: "Comprend ton catalogue Excel sans que tu n'expliques",
    desc: "Tu uploades ton fichier produits une seule fois. Le bot apprend les noms, prix, tailles, photos. Tu modifies ton Excel, il se met à jour automatiquement.",
    illustration: {
      src: "/illustrations/merchant-tired.jpg",
      alt: "Catalogue qui se transforme en cerveau du bot",
    },
    quote: { text: "Robe rouge dispo M, L et XL. 80 000 Ar.", time: "now" },
    align: "right" as const,
  },
];

export function Pillars() {
  return (
    <section id="story" className="py-24 md:py-36 bg-[#FAF9F5]">
      <div className="max-w-6xl mx-auto px-5 sm:px-8">
        {/* Section header */}
        <div className="text-center max-w-3xl mx-auto mb-20 md:mb-32">
          <div className="mb-6">
            <StepBadge>Le constat</StepBadge>
          </div>
          <h2 className="font-display text-4xl md:text-6xl text-[#0F0E0C] tracking-[-0.02em] leading-[1.0]">
            Tes clients posent les{" "}
            <em className="not-italic font-display italic text-[#B7481E]">mêmes</em> questions,
            <br />
            tu réponds <em className="not-italic font-display italic">100 fois</em> par jour,
            <br />
            et le soir tu dors mal<span className="text-[#B7481E]">.</span>
          </h2>
          <p className="mt-8 text-lg text-[#0F0E0C]/70 max-w-xl mx-auto leading-relaxed">
            Trois choses que Valina-Bot fait à ta place, dès le premier jour.
          </p>
        </div>

        {/* Zigzag pillars */}
        <div className="space-y-32 md:space-y-44">
          {PILLARS.map((pillar) => {
            const isRight = pillar.align === "right";
            return (
              <article
                key={pillar.n}
                className="relative grid md:grid-cols-12 gap-8 md:gap-16 items-center"
              >
                {/* Decorative dashed line - desktop only */}
                <DashedLine
                  variant="pillar-curve"
                  className={`absolute hidden md:block top-1/4 ${
                    isRight ? "left-1/3 -scale-x-100" : "right-1/3"
                  } w-[30%] h-[60%] -z-0 opacity-60`}
                  color="#0F0E0C"
                />

                {/* Text */}
                <div
                  className={`md:col-span-6 relative z-10 ${
                    isRight ? "md:order-1" : "md:order-2"
                  }`}
                >
                  <div className="flex items-center gap-4 mb-6">
                    <NumberCircle n={pillar.n} color={pillar.color} size="md" />
                    <StepBadge variant={pillar.color === "sun" ? "accent" : "default"}>
                      {pillar.badge}
                    </StepBadge>
                  </div>

                  <h3 className="font-display text-3xl md:text-4xl lg:text-5xl text-[#0F0E0C] tracking-[-0.02em] leading-[1.05] mb-6">
                    {pillar.title}
                  </h3>

                  <p className="text-lg text-[#0F0E0C]/75 leading-relaxed mb-8 max-w-md">
                    {pillar.desc}
                  </p>

                  <div className="inline-block">
                    <EditorialBubble
                      variant="client"
                      timestamp={pillar.quote.time}
                    >
                      {pillar.quote.text}
                    </EditorialBubble>
                  </div>
                </div>

                {/* Illustration */}
                <div
                  className={`md:col-span-6 relative z-10 ${
                    isRight ? "md:order-2" : "md:order-1"
                  }`}
                >
                  <IllustrationFrame
                    src={pillar.illustration.src}
                    alt={pillar.illustration.alt}
                    width={560}
                    height={420}
                  />
                </div>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
