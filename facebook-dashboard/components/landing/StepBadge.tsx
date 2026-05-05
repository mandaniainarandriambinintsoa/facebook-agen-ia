interface StepBadgeProps {
  children: React.ReactNode;
  variant?: "default" | "accent" | "dark";
}

export function StepBadge({ children, variant = "default" }: StepBadgeProps) {
  const styles = {
    default: "bg-[#F0F2F5] border-[#1C1E21]/15 text-[#1C1E21]",
    accent: "bg-[#F4B83A]/30 border-[#F4B83A] text-[#1C1E21]",
    dark: "bg-[#1C1E21] border-[#1C1E21] text-[#F7F8FA]",
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
  terracotta: "bg-[#1877F2] text-[#F7F8FA]",
  sun: "bg-[#F4B83A] text-[#1C1E21]",
  forest: "bg-[#16A34A] text-[#F7F8FA]",
  ink: "bg-[#1C1E21] text-[#F7F8FA]",
};

const SIZE_MAP = {
  sm: "h-8 w-8 text-base",
  md: "h-10 w-10 text-lg",
  lg: "h-14 w-14 text-2xl",
};

export function NumberCircle({ n, color = "terracotta", size = "md" }: NumberCircleProps) {
  return (
    <span
      className={`inline-flex items-center justify-center rounded-full font-medium ${COLOR_MAP[color]} ${SIZE_MAP[size]}`}
    >
      {n}
    </span>
  );
}
