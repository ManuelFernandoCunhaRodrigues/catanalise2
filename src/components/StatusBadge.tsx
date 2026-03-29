import { Badge } from "@/components/ui/badge";
import { normalizeStatus, type UiAnalysisStatus } from "@/lib/analysis-utils";

interface StatusBadgeProps {
  status: UiAnalysisStatus | string;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const normalizedStatus = normalizeStatus(status);

  const variants: Record<UiAnalysisStatus, string> = {
    Aprovado: "bg-success/10 text-success border-success/20 hover:bg-success/15",
    Revisao: "bg-warning/10 text-warning border-warning/20 hover:bg-warning/15",
    Reprovado: "bg-destructive/10 text-destructive border-destructive/20 hover:bg-destructive/15",
  };

  return (
    <Badge variant="outline" className={variants[normalizedStatus]}>
      {normalizedStatus}
    </Badge>
  );
}
