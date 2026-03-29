interface ScoreBarProps {
  score: number;
  label: string;
}

export function ScoreBar({ score, label }: ScoreBarProps) {
  const getColor = (s: number) => {
    if (s >= 80) return "score-bar-green";
    if (s >= 50) return "score-bar-yellow";
    return "score-bar-red";
  };

  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium">{score}%</span>
      </div>
      <div className="h-2 w-full rounded-full bg-muted">
        <div
          className={`h-2 rounded-full transition-all duration-700 ${getColor(score)}`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}
