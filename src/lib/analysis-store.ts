import type { AnalyzeResponse } from "@/lib/api";

const LAST_ANALYSIS_KEY = "cat-analyzer:last-analysis";
const MAX_STORED_TEXT_LENGTH = 5000;

export function saveLastAnalysis(analysis: AnalyzeResponse): void {
  if (typeof window === "undefined") {
    return;
  }

  const payloadToPersist: AnalyzeResponse = {
    ...analysis,
    texto_extraido: analysis.texto_extraido?.slice(0, MAX_STORED_TEXT_LENGTH),
  };

  try {
    window.localStorage.setItem(LAST_ANALYSIS_KEY, JSON.stringify(payloadToPersist));
  } catch {
    window.localStorage.removeItem(LAST_ANALYSIS_KEY);
  }
}

export function getLastAnalysis(): AnalyzeResponse | null {
  if (typeof window === "undefined") {
    return null;
  }

  const stored = window.localStorage.getItem(LAST_ANALYSIS_KEY);
  if (!stored) {
    return null;
  }

  try {
    return JSON.parse(stored) as AnalyzeResponse;
  } catch {
    window.localStorage.removeItem(LAST_ANALYSIS_KEY);
    return null;
  }
}
