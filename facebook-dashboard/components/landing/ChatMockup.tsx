const MESSAGES = [
  {
    from: "client",
    text: "Bonjour, c'est combien la robe rouge ?",
    time: "23:42",
  },
  {
    from: "bot",
    text: "Bonjour ! La robe rouge est à 80 000 MGA, dispo en M, L et XL. Livraison Tana en 24h.",
    time: "23:42",
  },
  {
    from: "client",
    text: "Vous acceptez Mvola ?",
    time: "23:42",
  },
  {
    from: "bot",
    text: "Oui ! Mvola, Orange Money et Airtel Money. Je vous prépare la commande, c'est quoi votre adresse ?",
    time: "23:42",
  },
];

export function ChatMockup() {
  return (
    <div className="relative w-full max-w-sm">
      <div
        aria-hidden
        className="absolute -inset-4 rounded-[3rem] bg-gradient-to-br from-emerald-400/20 to-amber-400/20 blur-2xl"
      />
      <div className="relative rounded-[2.5rem] border-8 border-slate-900 bg-slate-900 shadow-2xl overflow-hidden">
        <div className="bg-emerald-600 text-white px-4 pt-3 pb-4 flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-white/20 flex items-center justify-center font-semibold">
            MS
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-sm truncate">Manda Shop</p>
            <p className="text-xs text-emerald-100">en ligne · répond en quelques secondes</p>
          </div>
        </div>

        <div className="bg-[#e5ddd5] px-3 py-4 space-y-3 min-h-[28rem]">
          {MESSAGES.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.from === "client" ? "justify-start" : "justify-end"}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-3 py-2 text-sm shadow ${
                  msg.from === "client"
                    ? "bg-white text-slate-900 rounded-tl-sm"
                    : "bg-[#dcf8c6] text-slate-900 rounded-tr-sm"
                }`}
              >
                <p>{msg.text}</p>
                <p className="text-[10px] text-slate-500 text-right mt-1">{msg.time}</p>
              </div>
            </div>
          ))}

          <div className="flex justify-end">
            <div className="bg-white rounded-2xl px-3 py-2 shadow flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-slate-400 animate-bounce" />
              <span className="h-2 w-2 rounded-full bg-slate-400 animate-bounce [animation-delay:150ms]" />
              <span className="h-2 w-2 rounded-full bg-slate-400 animate-bounce [animation-delay:300ms]" />
            </div>
          </div>
        </div>

        <div className="bg-slate-100 px-3 py-3 flex items-center gap-2">
          <div className="flex-1 bg-white rounded-full px-3 py-2 text-xs text-slate-400">
            Écrire un message...
          </div>
        </div>
      </div>
    </div>
  );
}
