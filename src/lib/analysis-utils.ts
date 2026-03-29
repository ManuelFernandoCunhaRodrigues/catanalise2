export type UiAnalysisStatus = "Aprovado" | "Revisao" | "Reprovado";

export function getStatusFromScore(score: number): UiAnalysisStatus {
  if (score >= 80) {
    return "Aprovado";
  }
  if (score >= 50) {
    return "Revisao";
  }
  return "Reprovado";
}

export function formatBackendDate(value: string): string {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(parsed);
}
