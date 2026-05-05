/**
 * Bulle de message style WhatsApp/Messenger inline dans le texte.
 * Inspirée Curately où certaines phrases-clé deviennent une bulle verte.
 */
interface EditorialBubbleProps {
  children: React.ReactNode;
  variant?: "client" | "bot";
  timestamp?: string;
  className?: string;
}

export function EditorialBubble({
  children,
  variant = "client",
  timestamp,
  className,
}: EditorialBubbleProps) {
  const isClient = variant === "client";

  return (
    <span
      className={`inline-flex items-end gap-2 px-3.5 py-2 rounded-2xl shadow-sm ${
        isClient
          ? "bg-[#DCFCE7] text-[#0F0E0C] rounded-tr-sm"
          : "bg-white text-[#0F0E0C] rounded-tl-sm"
      } ${className || ""}`}
    >
      <span className="text-sm leading-snug">{children}</span>
      {timestamp && (
        <span className="font-mono text-[9px] text-[#0F0E0C]/40 mb-0.5">
          {timestamp}
          {isClient && <span className="ml-1 text-[#2D4A3E]">✓✓</span>}
        </span>
      )}
    </span>
  );
}
