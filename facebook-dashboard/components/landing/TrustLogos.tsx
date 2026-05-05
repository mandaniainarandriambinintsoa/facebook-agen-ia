export function TrustLogos() {
  const platforms = [
    "Messenger",
    "WhatsApp Business",
    "Instagram",
    "Mvola",
    "Orange Money",
    "Airtel Money",
  ];

  return (
    <section className="border-y border-slate-200 bg-slate-50/50 py-10">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <p className="text-center text-xs font-medium uppercase tracking-wider text-slate-500 mb-6">
          Compatible avec
        </p>
        <div className="flex flex-wrap items-center justify-center gap-x-10 gap-y-4">
          {platforms.map((p) => (
            <span
              key={p}
              className="text-slate-400 font-semibold text-sm md:text-base"
            >
              {p}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
