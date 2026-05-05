interface StepBadgeProps {
  children: React.ReactNode;
  variant?: "default" | "accent" | "dark";
}

export function StepBadge({ children, variant = "default" }: StepBadgeProps) {
  const styles = {
    default: "bg-[#F4ECE0] border-[#0F0E0C]/15 text-[#0F0E0C]",
    accent: "bg-[#F4B83A]/30 border-[#F4B83A] text-[#0F0E0C]",
    dark: "bg-[#0F0E0C] border-[#0F0E0C] text-[#FAF9F5]",
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border px-3 py-1 font-mono text-[11px] font-medium uppercase tracking-[0.2em] ${styles[variant]}`}
    >
      {children}
    </span>
  );
}

interface NumberCircleProps {
  n: number;
  color?: "terracotta" | "sun" | "forest" | "ink";
  size?: "sm" | "md" | "lg";
}

const COLOR_MAP = {
  terracotta: "bg-[#B7481E] text-[#FAF9F5]",
  sun: "bg-[#F4B83A] text-[#0F0E0C]",
  forest: "bg-[#2D4A3E] text-[#FAF9F5]",
  ink: "bg-[#0F0E0C] text-[#FAF9F5]",
};

const SIZE_MAP = {
  sm: "h-8 w-8 text-base",
  md: "h-10 w-10 text-lg",
  lg: "h-14 w-14 text-2xl",
};

export function NumberCircle({ n, color = "terracotta", size = "md" }: NumberCircleProps) {
  return (
    <span
      className={`inline-flex items-center justify-center rounded-full font-display font-medium ${COLOR_MAP[color]} ${SIZE_MAP[size]}`}
    >
      {n}
    </span>
  );
}
