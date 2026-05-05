/**
 * Ligne pointillée courbe inspirée Curately. Connecte un titre à une CTA
 * ou à une illustration. Anime le tracé au scroll via stroke-dashoffset.
 */
interface DashedLineProps {
  variant?: "hero-cta" | "pillar-curve" | "step-arrow" | "vertical";
  className?: string;
  color?: string;
  strokeWidth?: number;
}

const PATHS: Record<string, { d: string; viewBox: string }> = {
  "hero-cta": {
    d: "M 5 5 Q 50 5 50 50 Q 50 95 100 95",
    viewBox: "0 0 105 100",
  },
  "pillar-curve": {
    d: "M 5 5 Q 80 5 80 50 Q 80 100 5 100 Q 0 150 100 150",
    viewBox: "0 0 105 160",
  },
  "step-arrow": {
    d: "M 5 50 Q 50 50 50 5 Q 50 -40 100 -40 L 100 0 M 95 -5 L 100 0 L 95 5",
    viewBox: "0 -50 105 60",
  },
  vertical: {
    d: "M 50 0 Q 30 50 50 100 Q 70 150 50 200 L 50 195 M 45 195 L 50 200 L 55 195",
    viewBox: "0 0 100 205",
  },
};

export function DashedLine({
  variant = "hero-cta",
  className,
  color = "#1C1E21",
  strokeWidth = 2,
}: DashedLineProps) {
  const { d, viewBox } = PATHS[variant];
  return (
    <svg
      aria-hidden
      viewBox={viewBox}
      preserveAspectRatio="none"
      className={className}
      fill="none"
    >
      <path
        d={d}
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeDasharray="6 8"
      />
    </svg>
  );
}
