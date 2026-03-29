from typing import Any, Optional

from services.utils import build_document_payload, dedupe, has_value, humanize_field, is_valid_date, normalize_text, parse_date


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
    normalized = build_document_payload(data)

    errors = dedupe(validate_required_fields(normalized) + validate_format(normalized))
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
        if not has_value(data.get(field_name)):
            errors.append(f"Campo obrigatorio ausente: {field_name}. Preencha esse dado para concluir a analise.")

    if has_value(data.get("data_inicio")) and not has_value(data.get("data_fim")):
        errors.append("Data de fim ausente. Informe a data final quando houver data de inicio.")

    if has_value(data.get("numero_art")) and not has_value(data.get("descricao_servico")):
        errors.append("ART informada sem descricao do servico. Descreva a atividade vinculada a ART.")

    return errors


def validate_format(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    numero_art = data.get("numero_art")
    if has_value(numero_art) and not str(numero_art).isdigit():
        errors.append("Numero ART invalido. Use apenas numeros, sem letras ou simbolos.")

    for field_name in ("data_inicio", "data_fim", "data_execucao"):
        field_value = data.get(field_name)
        if has_value(field_value) and not is_valid_date(str(field_value)):
            errors.append(f"{humanize_field(field_name)} invalida. Use o formato DD/MM/AAAA.")

    return errors


def validate_consistency(data: dict[str, Any]) -> dict[str, list[str]]:
    inconsistencies: list[str] = []
    start_date = parse_date(data.get("data_inicio") or data.get("data_execucao"))
    end_date = parse_date(data.get("data_fim"))

    if start_date and end_date and end_date < start_date:
        inconsistencies.append("Data de fim anterior a data de inicio. Ajuste o periodo informado.")

    return {"inconsistencias": dedupe(inconsistencies)}


def detect_suspicious_patterns(data: dict[str, Any]) -> list[str]:
    alerts: list[str] = []

    descricao = str(data.get("descricao_servico") or "").strip()
    if descricao and len(descricao) < 20:
        alerts.append("Descricao muito curta. Inclua mais detalhes para tornar a analise confiavel.")

    normalized_description = normalize_text(descricao)
    if normalized_description in GENERIC_DESCRIPTIONS:
        alerts.append("Descricao muito generica, detalhe melhor o servico executado.")

    if descricao and len(normalized_description.split()) < 4:
        alerts.append("Ausencia de detalhes tecnicos na descricao do servico.")

    nome_profissional = str(data.get("nome_profissional") or "").strip()
    if nome_profissional and len(nome_profissional.split()) < 2:
        alerts.append("Nome profissional incompleto. Informe pelo menos nome e sobrenome.")

    numero_art = str(data.get("numero_art") or "").strip()
    if numero_art and (not numero_art.isdigit() or len(numero_art) < 6):
        alerts.append("Numero ART suspeito ou muito curto. Revise a numeracao informada.")

    start_date = parse_date(data.get("data_inicio") or data.get("data_execucao"))
    end_date = parse_date(data.get("data_fim"))
    if start_date and end_date:
        duration_days = (end_date - start_date).days
        if duration_days <= 1:
            alerts.append("Periodo de execucao muito curto. Confirme se as datas estao corretas.")

    return dedupe(alerts)


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
