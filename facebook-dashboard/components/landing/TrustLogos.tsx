export function TrustLogos() {
  const platforms = [
    { name: "Messenger", role: "Plateforme" },
    { name: "Mvola", role: "Paiement" },
    { name: "Orange Money", role: "Paiement" },
    { name: "Airtel Money", role: "Paiement" },
  ];

  return (
    <section className="py-14 bg-[#FBF6EE]">
      <div className="max-w-7xl mx-auto px-5 sm:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {platforms.map((p, i) => (
            <div
              key={p.name}
              className={`flex flex-col gap-1 ${
                i < platforms.length - 1 ? "md:border-r md:border-[#1A1614]/10 md:pr-8" : ""
              }`}
            >
              <span className="font-mono text-xs text-[#1A1614]/40 uppercase tracking-widest">
                {p.role}
              </span>
              <span className="font-display text-2xl text-[#1A1614]">
                {p.name}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
