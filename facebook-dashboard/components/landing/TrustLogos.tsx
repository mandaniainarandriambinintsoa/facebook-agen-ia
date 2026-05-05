export function TrustLogos() {
  const platforms = [
    { name: "Messenger", role: "Plateforme" },
    { name: "Mvola", role: "Paiement" },
    { name: "Orange Money", role: "Paiement" },
    { name: "Airtel Money", role: "Paiement" },
  ];

  return (
    <section className="py-16 md:py-20 bg-[#F7F8FA] border-y border-[#1C1E21]/10">
      <div className="max-w-6xl mx-auto px-5 sm:px-8">
        <p className="text-center font-mono text-[11px] uppercase tracking-[0.2em] text-[#1C1E21]/50 mb-10">
          Compatible avec
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-x-8 gap-y-10">
          {platforms.map((p, i) => (
            <div
              key={p.name}
              className={`flex flex-col gap-1 ${
                i < platforms.length - 1
                  ? "md:border-r md:border-[#1C1E21]/10 md:pr-8"
                  : ""
              }`}
            >
              <span className="font-mono text-[10px] text-[#1C1E21]/40 uppercase tracking-[0.2em]">
                {p.role}
              </span>
              <span className="text-2xl md:text-3xl text-[#1C1E21] tracking-tight">
                {p.name}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
