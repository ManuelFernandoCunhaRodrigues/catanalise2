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

export function normalizeStatus(value: string): UiAnalysisStatus {
  const normalized = value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase();

  if (normalized.startsWith("aprov")) {
    return "Aprovado";
  }
  if (normalized.startsWith("revis")) {
    return "Revisao";
  }
  return "Reprovado";
}

export function formatBackendDate(value: string): string {
  const [datePart] = value.split(" ");
  if (!datePart) {
    return value;
  }

  const [year, month, day] = datePart.split("-");
  if (!year || !month || !day) {
    return value;
  }

  return `${day.padStart(2, "0")}/${month.padStart(2, "0")}/${year}`;
}

export function getMonthKey(value: string): string | null {
  const [datePart] = value.split(" ");
  if (!datePart || datePart.length < 7) {
    return null;
  }
  return datePart.slice(0, 7);
}

export function formatScoreLevel(level: string | undefined): string {
  if (!level) {
    return "Nao informado";
  }

  const normalized = level
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase();

  if (normalized === "alto") {
    return "Alto";
  }
  if (normalized === "medio") {
    return "Medio";
  }
  if (normalized === "baixo") {
    return "Baixo";
  }

  return level;
}
