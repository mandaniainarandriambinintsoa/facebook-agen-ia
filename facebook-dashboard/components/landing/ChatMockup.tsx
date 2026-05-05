"use client";

const MESSAGES = [
  { from: "client", text: "Salama tompoko, mbola misy ve ny robe rouge taille M ?", time: "23:42", delay: 100 },
  { from: "bot", text: "Salama ! Misy ihany ny taille M sy L. Vidiny 80 000 Ar. Livraison Tana 24h.", time: "23:42", delay: 600 },
  { from: "client", text: "Mety ny Mvola ?", time: "23:43", delay: 1100 },
  { from: "bot", text: "Mety tsara ny Mvola, Orange Money sy Airtel Money. Mba lazao ahy ny adirezan-tsika ?", time: "23:43", delay: 1600 },
];

export function ChatMockup() {
  return (
    <div className="relative w-full max-w-[340px] md:max-w-[380px]">
      {/* Phone frame */}
      <div className="relative rounded-[2.75rem] bg-[#1A1614] p-2.5 shadow-[0_30px_80px_-20px_rgba(183,72,30,0.4)]">
        {/* Notch */}
        <div className="absolute top-2.5 left-1/2 -translate-x-1/2 z-10 h-6 w-28 rounded-b-2xl bg-[#1A1614]" />

        {/* Screen */}
        <div className="relative rounded-[2.25rem] overflow-hidden bg-[#F0EAE3]">
          {/* Status bar */}
          <div className="bg-[#1A1614] text-[#FBF6EE] pt-3 pb-1 px-6 flex items-center justify-between text-[10px] font-medium">
            <span>23:43</span>
            <span className="opacity-70">100%</span>
          </div>

          {/* Header conversation */}
          <div className="bg-[#FBF6EE] border-b border-[#1A1614]/8 px-4 py-3 flex items-center gap-3">
            <div className="h-9 w-9 rounded-full bg-gradient-to-br from-[#B7481E] to-[#F4B83A] flex items-center justify-center font-display text-white font-semibold text-sm">
              T
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-[#1A1614] text-sm leading-tight">Tantine Hanta</p>
              <p className="text-[10px] text-[#2D4A3E] flex items-center gap-1">
                <span className="inline-block h-1.5 w-1.5 rounded-full bg-[#2D4A3E] animate-pulse" />
                Valina-Bot répond pour toi
              </p>
            </div>
          </div>

          {/* Messages */}
          <div className="px-3 py-4 space-y-2.5 min-h-[420px] bg-[#F5EFE5]">
            {MESSAGES.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.from === "client" ? "justify-start" : "justify-end"} animate-in fade-in slide-in-from-bottom-2 fill-mode-both`}
                style={{ animationDelay: `${msg.delay}ms`, animationDuration: "400ms" }}
              >
                <div
                  className={`max-w-[82%] rounded-2xl px-3.5 py-2 text-[13px] leading-relaxed shadow-sm ${
                    msg.from === "client"
                      ? "bg-white text-[#1A1614] rounded-tl-md"
                      : "bg-[#1A1614] text-[#FBF6EE] rounded-tr-md"
                  }`}
                >
                  <p>{msg.text}</p>
                  <p className={`text-[9px] mt-1 ${msg.from === "client" ? "text-[#1A1614]/40" : "text-[#FBF6EE]/50"} text-right`}>
                    {msg.time}
                  </p>
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            <div
              className="flex justify-start animate-in fade-in fill-mode-both"
              style={{ animationDelay: "2200ms", animationDuration: "400ms" }}
            >
              <div className="bg-white rounded-2xl rounded-tl-md px-3 py-2.5 shadow-sm flex items-center gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-[#1A1614]/40 animate-bounce" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#1A1614]/40 animate-bounce [animation-delay:150ms]" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#1A1614]/40 animate-bounce [animation-delay:300ms]" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Floating ribbon */}
      <div
        className="absolute -right-4 -top-4 md:-right-8 md:-top-6 rotate-6 bg-[#F4B83A] text-[#1A1614] font-display italic text-sm px-4 py-1.5 rounded-md shadow-lg"
        aria-hidden
      >
        live, en mada
      </div>
    </div>
  );
}
