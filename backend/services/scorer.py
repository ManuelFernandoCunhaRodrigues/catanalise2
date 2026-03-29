from typing import Any, Dict, List


ERROR_PENALTY = 25
INCONSISTENCY_PENALTY = 20
FRAUD_PENALTY = 40
ALERT_PENALTY = 10


def calculate_reliability_score(data: dict) -> dict:
    """
    Score explicável de confiabilidade para uso em apoio à decisão.
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


def apply_penalties(data: dict) -> int:
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


def generate_justification(data: dict) -> List[str]:
    explanations: List[str] = []

    for error in data["erros"]:
        explanations.append(f"Erro crítico reduz significativamente a confiabilidade: {error}.")

    for inconsistency in data["inconsistencias"]:
        explanations.append(f"Inconsistência reduz a segurança da análise: {inconsistency}.")

    for fraud in data["fraudes"]:
        explanations.append(f"Fraude detectada impacta fortemente o score: {fraud}.")

    for alert in data["alertas"]:
        explanations.append(f"Alerta indica necessidade de revisão: {alert}.")

    if not explanations:
        explanations.append("Nenhum problema relevante foi identificado, mantendo o documento com alta confiabilidade.")

    return explanations


def generate_summary(score: int, level: str, data: dict) -> str:
    has_fraud = len(data["fraudes"]) > 0
    has_inconsistency = len(data["inconsistencias"]) > 0
    has_errors = len(data["erros"]) > 0
    has_alerts = len(data["alertas"]) > 0

    if level == "alto":
        return (
            "Este documento apresenta boa consistência geral e alto nível de confiabilidade. "
            "A aprovação pode seguir com baixa necessidade de revisão adicional."
        )

    if level == "medio":
        if has_fraud or has_inconsistency:
            return (
                "Este documento apresenta inconsistências ou sinais de risco que exigem atenção. "
                "Recomenda-se revisão humana antes da aprovação."
            )
        return (
            "Este documento tem confiabilidade intermediária, com alertas que merecem conferência. "
            "Uma revisão simples pode aumentar a segurança da decisão."
        )

    if has_fraud:
        return (
            "Este documento apresenta possíveis indícios de fraude, resultando em confiabilidade baixa. "
            "Recomenda-se bloqueio preventivo e auditoria antes de qualquer aprovação."
        )

    if has_errors or has_inconsistency or has_alerts:
        return (
            "Este documento apresenta múltiplos problemas de qualidade e consistência, resultando em confiabilidade baixa. "
            "Recomenda-se revisão completa antes da aprovação."
        )

    return f"Este documento recebeu score {score}, com nível {level} de confiabilidade."


def calculate_score(validation: Dict[str, Any], fraud: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Compatibilidade com o fluxo atual da API.
    Combina validação e fraude em um único score de confiabilidade.
    """
    fraud = fraud or {}
    payload = {
        "erros": validation.get("erros", []),
        "alertas": _merge_lists(validation.get("alertas", []), fraud.get("alertas", [])),
        "inconsistencias": validation.get("inconsistencias", []),
        "fraudes": fraud.get("fraudes", []),
    }
    return calculate_reliability_score(payload)


def _normalize_score_input(data: dict) -> dict:
    return {
        "erros": _ensure_list(data.get("erros")),
        "alertas": _ensure_list(data.get("alertas")),
        "inconsistencias": _ensure_list(data.get("inconsistencias")),
        "fraudes": _ensure_list(data.get("fraudes")),
    }


def _ensure_list(value: Any) -> List[str]:
    if not value:
        return []
    return [str(item) for item in value]


def _merge_lists(primary: List[str], secondary: List[str]) -> List[str]:
    merged: List[str] = []
    for item in list(primary) + list(secondary):
        if item not in merged:
            merged.append(item)
    return merged
