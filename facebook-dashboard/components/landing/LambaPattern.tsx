/**
 * Pattern decoratif inspire des tissus malgaches lamba.
 * Geometrique, repetitif, modernise. Utilise comme background subtle.
 */
export function LambaPattern({
  color = "currentColor",
  opacity = 0.08,
  className,
}: {
  color?: string;
  opacity?: number;
  className?: string;
}) {
  const id = "lamba-pat";
  return (
    <svg
      aria-hidden
      className={className}
      style={{ position: "absolute", inset: 0, width: "100%", height: "100%", opacity }}
    >
      <defs>
        <pattern id={id} x="0" y="0" width="48" height="48" patternUnits="userSpaceOnUse">
          <path
            d="M0 24 L24 0 L48 24 L24 48 Z"
            fill="none"
            stroke={color}
            strokeWidth="1"
          />
          <circle cx="24" cy="24" r="2" fill={color} />
          <line x1="0" y1="24" x2="48" y2="24" stroke={color} strokeWidth="0.5" strokeDasharray="2 4" />
        </pattern>
      </defs>
      <rect x="0" y="0" width="100%" height="100%" fill={`url(#${id})`} />
    </svg>
  );
}

/**
 * Variante "soleil" : rosace radiale qu'on peut placer en deco corner.
 */
export function SunBurst({
  size = 200,
  color = "currentColor",
  opacity = 0.15,
  className,
}: {
  size?: number;
  color?: string;
  opacity?: number;
  className?: string;
}) {
  const rays = Array.from({ length: 16 });
  const cx = size / 2;
  const cy = size / 2;
  const innerR = size * 0.18;
  const outerR = size * 0.45;
  return (
    <svg
      aria-hidden
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      className={className}
      style={{ opacity }}
    >
      <circle cx={cx} cy={cy} r={innerR} fill="none" stroke={color} strokeWidth="2" />
      {rays.map((_, i) => {
        const angle = (i * 360) / rays.length;
        const rad = (angle * Math.PI) / 180;
        const x1 = cx + Math.cos(rad) * innerR;
        const y1 = cy + Math.sin(rad) * innerR;
        const x2 = cx + Math.cos(rad) * outerR;
        const y2 = cy + Math.sin(rad) * outerR;
        return (
          <line
            key={i}
            x1={x1}
            y1={y1}
            x2={x2}
            y2={y2}
            stroke={color}
            strokeWidth="2"
            strokeLinecap="round"
          />
        );
      })}
    </svg>
  );
}
