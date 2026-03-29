from typing import Any


ERROR_PENALTY = 25
INCONSISTENCY_PENALTY = 20
FRAUD_PENALTY = 40
ALERT_PENALTY = 10


def calculate_reliability_score(data: dict[str, Any]) -> dict[str, Any]:
    """
    Explainable reliability score used by the API and the UI summary.
    """
    normalized = _normalize_score_input(data)
    score = apply_penalties(normalized)
    level = classify_score(score)
    justification = generate_justification(normalized)
    summary = generate_summary(score, level, normalized)

    return {
        "score": score,
        "nivel": level,
        "justificativa": justification,
        "resumo": summary,
    }


def apply_penalties(data: dict[str, list[str]]) -> int:
    score = 100
    score -= len(data["erros"]) * ERROR_PENALTY
    score -= len(data["inconsistencias"]) * INCONSISTENCY_PENALTY
    score -= len(data["fraudes"]) * FRAUD_PENALTY
    score -= len(data["alertas"]) * ALERT_PENALTY
    return max(0, min(100, score))


def classify_score(score: int) -> str:
    if score >= 80:
        return "alto"
    if score >= 50:
        return "medio"
    return "baixo"


def generate_justification(data: dict[str, list[str]]) -> list[str]:
    explanations: list[str] = []

    for error in data["erros"]:
        explanations.append(f"Erro critico reduz significativamente a confiabilidade: {error}.")

    for inconsistency in data["inconsistencias"]:
        explanations.append(f"Inconsistencia reduz a seguranca da analise: {inconsistency}.")

    for fraud in data["fraudes"]:
        explanations.append(f"Fraude detectada impacta fortemente o score: {fraud}.")

    for alert in data["alertas"]:
        explanations.append(f"Alerta indica necessidade de revisao: {alert}.")

    if not explanations:
        explanations.append("Nenhum problema relevante foi identificado, mantendo o documento com alta confiabilidade.")

    return explanations


def generate_summary(score: int, level: str, data: dict[str, list[str]]) -> str:
    has_fraud = len(data["fraudes"]) > 0
    has_inconsistency = len(data["inconsistencias"]) > 0
    has_errors = len(data["erros"]) > 0
    has_alerts = len(data["alertas"]) > 0

    if level == "alto":
        return (
            "Este documento apresenta boa consistencia geral e alto nivel de confiabilidade. "
            "A aprovacao pode seguir com baixa necessidade de revisao adicional."
        )

    if level == "medio":
        if has_fraud or has_inconsistency:
            return (
                "Este documento apresenta inconsistencias ou sinais de risco que exigem atencao. "
                "Recomenda-se revisao humana antes da aprovacao."
            )
        return (
            "Este documento tem confiabilidade intermediaria, com alertas que merecem conferencia. "
            "Uma revisao simples pode aumentar a seguranca da decisao."
        )

    if has_fraud:
        return (
            "Este documento apresenta possiveis indicios de fraude, resultando em confiabilidade baixa. "
            "Recomenda-se bloqueio preventivo e auditoria antes de qualquer aprovacao."
        )

    if has_errors or has_inconsistency or has_alerts:
        return (
            "Este documento apresenta multiplos problemas de qualidade e consistencia, resultando em confiabilidade baixa. "
            "Recomenda-se revisao completa antes da aprovacao."
        )

    return f"Este documento recebeu score {score}, com nivel {level} de confiabilidade."


def calculate_score(validation: dict[str, Any], fraud: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Compatibility wrapper that combines validation and fraud results into a single score.
    """
    fraud = fraud or {}
    payload = {
        "erros": validation.get("erros", []),
        "alertas": _merge_lists(validation.get("alertas", []), fraud.get("alertas", [])),
        "inconsistencias": validation.get("inconsistencias", []),
        "fraudes": fraud.get("fraudes", []),
    }
    return calculate_reliability_score(payload)


def _normalize_score_input(data: dict[str, Any]) -> dict[str, list[str]]:
    return {
        "erros": _dedupe(_ensure_list(data.get("erros"))),
        "alertas": _dedupe(_ensure_list(data.get("alertas"))),
        "inconsistencias": _dedupe(_ensure_list(data.get("inconsistencias"))),
        "fraudes": _dedupe(_ensure_list(data.get("fraudes"))),
    }


def _ensure_list(value: Any) -> list[str]:
    if not value:
        return []
    return [str(item) for item in value]


def _merge_lists(primary: list[str], secondary: list[str]) -> list[str]:
    return _dedupe(list(primary) + list(secondary))


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
