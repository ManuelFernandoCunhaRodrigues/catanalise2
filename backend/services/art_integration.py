from difflib import SequenceMatcher
from typing import Any, Optional

from services.utils import build_document_payload, dedupe, normalize_text, parse_date


ART_DATABASE = {
    "123456789": {
        "numero_art": "123456789",
        "nome_profissional": "Joao Silva",
        "data_inicio": "01/01/2023",
        "data_fim": "01/02/2023",
    },
    "987654321": {
        "numero_art": "987654321",
        "nome_profissional": "Maria Oliveira",
        "data_inicio": "15/02/2023",
        "data_fim": "30/04/2023",
    },
}


def compare_cat_with_art(cat_data: dict[str, Any], art_data: dict[str, Any] | None = None) -> dict[str, Any]:
    normalized_cat = build_document_payload(cat_data)
    resolved_art, resolution_alerts = _resolve_art(normalized_cat, art_data)

    inconsistencies: list[str] = []
    alerts: list[str] = list(resolution_alerts)

    inconsistencies.extend(compare_art_number(normalized_cat, resolved_art))
    inconsistencies.extend(compare_professional(normalized_cat, resolved_art))
    inconsistencies.extend(compare_dates(normalized_cat, resolved_art))
    alerts.extend(compare_description_vs_period(normalized_cat))

    inconsistencies = dedupe(inconsistencies)
    alerts = dedupe(alerts)

    return {
        "consistente": len(inconsistencies) == 0,
        "inconsistencias": inconsistencies,
        "alertas": alerts,
        "resumo": generate_summary(inconsistencies, alerts, resolved_art),
        "art_encontrada": resolved_art,
    }


def compare_art_number(cat_data: dict[str, Optional[str]], art_data: Optional[dict[str, Optional[str]]]) -> list[str]:
    inconsistencies: list[str] = []
    cat_art = cat_data.get("numero_art")
    art_number = (art_data or {}).get("numero_art")

    if cat_art and art_number and cat_art != art_number:
        inconsistencies.append("Numero da ART divergente entre CAT e ART informada.")

    return inconsistencies


def compare_professional(cat_data: dict[str, Optional[str]], art_data: Optional[dict[str, Optional[str]]]) -> list[str]:
    inconsistencies: list[str] = []
    cat_name = cat_data.get("nome_profissional")
    art_name = (art_data or {}).get("nome_profissional")

    if not cat_name or not art_name:
        return inconsistencies

    similarity = SequenceMatcher(None, normalize_text(cat_name), normalize_text(art_name)).ratio()
    if similarity < 0.88:
        inconsistencies.append("Nome do profissional divergente ou pouco similar entre CAT e ART.")

    return inconsistencies


def compare_dates(cat_data: dict[str, Optional[str]], art_data: Optional[dict[str, Optional[str]]]) -> list[str]:
    inconsistencies: list[str] = []

    if not art_data:
        return inconsistencies

    cat_start = parse_date(cat_data.get("data_inicio") or cat_data.get("data_execucao"))
    cat_end = parse_date(cat_data.get("data_fim"))
    art_start = parse_date(art_data.get("data_inicio"))
    art_end = parse_date(art_data.get("data_fim"))

    if cat_start and art_start and cat_start < art_start:
        inconsistencies.append("Data de inicio da CAT esta antes do periodo registrado na ART.")

    if cat_end and art_end and cat_end > art_end:
        inconsistencies.append("Data de fim da CAT ultrapassa o periodo registrado na ART.")

    return inconsistencies


def compare_description_vs_period(cat_data: dict[str, Optional[str]]) -> list[str]:
    alerts: list[str] = []
    description = str(cat_data.get("descricao_servico") or "").strip()
    cat_start = parse_date(cat_data.get("data_inicio") or cat_data.get("data_execucao"))
    cat_end = parse_date(cat_data.get("data_fim"))

    if not description or not cat_start or not cat_end:
        return alerts

    duration_days = (cat_end - cat_start).days
    normalized_description = normalize_text(description)

    if duration_days <= 3 and any(keyword in normalized_description for keyword in ("obra", "execucao", "residencial")):
        alerts.append("O periodo informado parece muito curto para a descricao do servico executado.")

    return alerts


def generate_summary(inconsistencies: list[str], alerts: list[str], art_data: Optional[dict[str, Optional[str]]]) -> str:
    if inconsistencies:
        return (
            "Os dados da CAT estao inconsistentes com a ART analisada, especialmente em campos essenciais do documento. "
            "Recomenda-se revisar o vinculo entre ART, profissional e periodo de execucao."
        )

    if alerts and art_data:
        return "A CAT esta compativel com a ART consultada, mas ha alertas que merecem revisao para aumentar a seguranca da analise."

    if alerts:
        return (
            "A comparacao nao encontrou inconsistencias criticas, mas faltam elementos para uma auditoria mais forte. "
            "Revise os alertas antes de aprovar o documento."
        )

    if art_data:
        return "Os dados da CAT estao compativeis com a ART analisada e nao foram encontradas inconsistencias relevantes."

    return "Nao foi possivel comparar a CAT com uma ART, mas nao foram encontradas inconsistencias documentais adicionais."


def _resolve_art(cat_data: dict[str, Optional[str]], art_data: Optional[dict[str, Any]]) -> tuple[Optional[dict[str, Optional[str]]], list[str]]:
    alerts: list[str] = []

    if art_data:
        return build_document_payload(art_data), alerts

    cat_art_number = cat_data.get("numero_art")
    if not cat_art_number:
        return None, alerts

    alerts.append("ART nao fornecida manualmente. Foi realizada busca automatica na base simulada.")
    fetched_art = ART_DATABASE.get(cat_art_number)

    if fetched_art is None:
        alerts.append("ART nao encontrada na base simulada para o numero informado.")
        return None, alerts

    return build_document_payload(fetched_art), alerts
