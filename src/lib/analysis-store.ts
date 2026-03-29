import type { AnalyzeResponse } from "@/lib/api";

const LAST_ANALYSIS_KEY = "cat-analyzer:last-analysis";

export function saveLastAnalysis(analysis: AnalyzeResponse): void {
  window.localStorage.setItem(LAST_ANALYSIS_KEY, JSON.stringify(analysis));
}

export function getLastAnalysis(): AnalyzeResponse | null {
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
