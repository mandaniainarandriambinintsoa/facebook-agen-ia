interface ProgressBarProps {
  current: number;
  total: number;
  labels?: string[];
}

export function ProgressBar({ current, total, labels }: ProgressBarProps) {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-3">
        <span className="font-mono text-xs text-[#1C1E21]/50 uppercase tracking-widest">
          Étape {current} sur {total}
        </span>
        {labels?.[current - 1] && (
          <span className="italic text-sm text-[#1877F2]">
            {labels[current - 1]}
          </span>
        )}
      </div>
      <div className="h-1 bg-[#1C1E21]/10 rounded-full overflow-hidden">
        <div
          className="h-full bg-[#1877F2] transition-all duration-500 ease-out"
          style={{ width: `${(current / total) * 100}%` }}
        />
      </div>
    </div>
  );
}
