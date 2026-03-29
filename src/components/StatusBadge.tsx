import { Badge } from "@/components/ui/badge";

interface StatusBadgeProps {
  status: "Aprovado" | "Revisao" | "Reprovado" | "Revisão";
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const normalizedStatus = status === "Revisão" ? "Revisao" : status;

  const variants: Record<string, string> = {
    Aprovado: "bg-success/10 text-success border-success/20 hover:bg-success/15",
    Revisao: "bg-warning/10 text-warning border-warning/20 hover:bg-warning/15",
    Reprovado: "bg-destructive/10 text-destructive border-destructive/20 hover:bg-destructive/15",
  };

  return (
    <Badge variant="outline" className={variants[normalizedStatus]}>
      {status}
    </Badge>
  );
}
