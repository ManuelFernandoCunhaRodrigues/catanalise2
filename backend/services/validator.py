from datetime import datetime
from typing import Any, Optional
import unicodedata


REQUIRED_FIELDS = [
    "nome_profissional",
    "numero_art",
    "descricao_servico",
    "contratante",
]

GENERIC_DESCRIPTIONS = {
    "servico",
    "obra",
    "atividade",
    "execucao",
}


def validate_cat(data: dict[str, Any]) -> dict[str, Any]:
    """
    Central validation flow for the CAT data extracted from the document.
    """
    normalized = _normalize_input(data)

    errors = _dedupe(validate_required_fields(normalized) + validate_format(normalized))
    consistency_result = validate_consistency(normalized)
    alerts = detect_suspicious_patterns(normalized)

    score_payload = calculate_score(
        errors=errors,
        inconsistencies=consistency_result["inconsistencias"],
        alerts=alerts,
    )

    return {
        "valid": len(errors) == 0 and len(consistency_result["inconsistencias"]) == 0,
        "erros": errors,
        "alertas": alerts,
        "inconsistencias": consistency_result["inconsistencias"],
        "score": score_payload["score"],
        "nivel": score_payload["nivel"],
    }


def validate_required_fields(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for field_name in REQUIRED_FIELDS:
        if not _has_value(data.get(field_name)):
            errors.append(f"Campo obrigatorio ausente: {field_name}. Preencha esse dado para concluir a analise.")

    if _has_value(data.get("data_inicio")) and not _has_value(data.get("data_fim")):
        errors.append("Data de fim ausente. Informe a data final quando houver data de inicio.")

    if _has_value(data.get("numero_art")) and not _has_value(data.get("descricao_servico")):
        errors.append("ART informada sem descricao do servico. Descreva a atividade vinculada a ART.")

    return errors


def validate_format(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    numero_art = data.get("numero_art")
    if _has_value(numero_art) and not str(numero_art).isdigit():
        errors.append("Numero ART invalido. Use apenas numeros, sem letras ou simbolos.")

    for field_name in ("data_inicio", "data_fim", "data_execucao"):
        field_value = data.get(field_name)
        if _has_value(field_value) and not _is_valid_date(str(field_value)):
            errors.append(f"{_humanize_field(field_name)} invalida. Use o formato DD/MM/AAAA.")

    return errors


def validate_consistency(data: dict[str, Any]) -> dict[str, list[str]]:
    inconsistencies: list[str] = []
    today = datetime.now().date()

    start_date = _parse_date(data.get("data_inicio") or data.get("data_execucao"))
    end_date = _parse_date(data.get("data_fim"))

    if start_date and start_date > today:
        inconsistencies.append("Data de inicio no futuro. Verifique se a execucao realmente ja ocorreu.")

    if end_date and end_date > today:
        inconsistencies.append("Data de fim no futuro. Confirme se a CAT nao foi preenchida com data incorreta.")

    if start_date and end_date and end_date < start_date:
        inconsistencies.append("Data de fim anterior a data de inicio. Ajuste o periodo informado.")

    return {"inconsistencias": _dedupe(inconsistencies)}


def detect_suspicious_patterns(data: dict[str, Any]) -> list[str]:
    alerts: list[str] = []

    descricao = str(data.get("descricao_servico") or "").strip()
    if descricao and len(descricao) < 20:
        alerts.append("Descricao muito curta. Inclua mais detalhes para tornar a analise confiavel.")

    normalized_description = _normalize_text(descricao)
    if normalized_description in GENERIC_DESCRIPTIONS:
        alerts.append("Descricao muito generica, detalhe melhor o servico executado.")

    nome_profissional = str(data.get("nome_profissional") or "").strip()
    if nome_profissional and len(nome_profissional.split()) < 2:
        alerts.append("Nome profissional incompleto. Informe pelo menos nome e sobrenome.")

    numero_art = str(data.get("numero_art") or "").strip()
    if numero_art and (not numero_art.isdigit() or len(numero_art) < 6):
        alerts.append("Numero ART suspeito ou muito curto. Revise a numeracao informada.")

    start_date = _parse_date(data.get("data_inicio") or data.get("data_execucao"))
    end_date = _parse_date(data.get("data_fim"))
    if start_date and end_date:
        duration_days = (end_date - start_date).days
        if duration_days <= 1:
            alerts.append("Periodo de execucao muito curto. Confirme se as datas estao corretas.")

    return _dedupe(alerts)


def calculate_score(*, errors: list[str], inconsistencies: list[str], alerts: list[str]) -> dict[str, Any]:
    score = 100
    score -= len(errors) * 30
    score -= len(inconsistencies) * 15
    score -= len(alerts) * 10
    score = max(0, min(100, score))

    if score >= 80:
        level = "alto"
    elif score >= 50:
        level = "medio"
    else:
        level = "baixo"

    return {"score": score, "nivel": level}


def validate_fields(fields: dict[str, Optional[str]]) -> dict[str, Any]:
    """
    Compatibility wrapper for the extraction output used by the current API.
    """
    payload = {
        "nome_profissional": fields.get("nome_profissional"),
        "numero_art": fields.get("numero_art"),
        "data_inicio": fields.get("data_inicio") or fields.get("data_execucao"),
        "data_fim": fields.get("data_fim"),
        "data_execucao": fields.get("data_execucao"),
        "descricao_servico": fields.get("descricao_servico"),
        "contratante": fields.get("contratante"),
    }
    return validate_cat(payload)


def _normalize_input(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "nome_profissional": _clean_value(data.get("nome_profissional")),
        "numero_art": _clean_value(data.get("numero_art")),
        "data_inicio": _clean_value(data.get("data_inicio")),
        "data_fim": _clean_value(data.get("data_fim")),
        "data_execucao": _clean_value(data.get("data_execucao")),
        "descricao_servico": _clean_value(data.get("descricao_servico")),
        "contratante": _clean_value(data.get("contratante")),
    }


def _clean_value(value: Any) -> Optional[str]:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _has_value(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def _is_valid_date(value: str) -> bool:
    return _parse_date(value) is not None


def _parse_date(value: Any) -> Optional[datetime.date]:
    if not _has_value(value):
        return None

    try:
        return datetime.strptime(str(value), "%d/%m/%Y").date()
    except ValueError:
        return None


def _humanize_field(field_name: str) -> str:
    labels = {
        "data_inicio": "Data de inicio",
        "data_fim": "Data de fim",
        "data_execucao": "Data de execucao",
    }
    return labels.get(field_name, field_name)


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.lower().strip())
    without_accents = "".join(char for char in normalized if not unicodedata.combining(char))
    return without_accents


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
