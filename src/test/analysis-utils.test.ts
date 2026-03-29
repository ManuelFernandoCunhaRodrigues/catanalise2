import { describe, expect, it } from "vitest";

import { formatBackendDate, formatScoreLevel, getMonthKey, getStatusFromScore, normalizeStatus } from "@/lib/analysis-utils";

describe("analysis-utils", () => {
  it("formats backend sqlite timestamps without timezone drift", () => {
    expect(formatBackendDate("2026-03-29 14:30:00")).toBe("29/03/2026");
  });

  it("normalizes status labels with accents", () => {
    expect(normalizeStatus("Revisao")).toBe("Revisao");
    expect(normalizeStatus("Revisão")).toBe("Revisao");
    expect(normalizeStatus("Aprovado")).toBe("Aprovado");
  });

  it("derives the UI status from score", () => {
    expect(getStatusFromScore(95)).toBe("Aprovado");
    expect(getStatusFromScore(70)).toBe("Revisao");
    expect(getStatusFromScore(20)).toBe("Reprovado");
  });

  it("extracts the month key from backend timestamps", () => {
    expect(getMonthKey("2026-03-29 14:30:00")).toBe("2026-03");
  });

  it("formats score levels for display", () => {
    expect(formatScoreLevel("medio")).toBe("Medio");
    expect(formatScoreLevel("baixo")).toBe("Baixo");
  });
});
