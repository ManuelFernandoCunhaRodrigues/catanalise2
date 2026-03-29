from datetime import datetime
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional
import unicodedata


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


def compare_cat_with_art(cat_data: dict, art_data: dict = None) -> dict:
    """
    Faz o cruzamento entre CAT e ART de forma explicavel.
    """
    normalized_cat = _normalize_document(cat_data)
    resolved_art, resolution_alerts = _resolve_art(normalized_cat, art_data)

    inconsistencies: List[str] = []
    alerts: List[str] = list(resolution_alerts)

    inconsistencies.extend(compare_art_number(normalized_cat, resolved_art))
    inconsistencies.extend(compare_professional(normalized_cat, resolved_art))
    inconsistencies.extend(compare_dates(normalized_cat, resolved_art))
    alerts.extend(compare_description_vs_period(normalized_cat))

    inconsistencies = _dedupe(inconsistencies)
    alerts = _dedupe(alerts)

    return {
        "consistente": len(inconsistencies) == 0,
        "inconsistencias": inconsistencies,
        "alertas": alerts,
        "resumo": generate_summary(inconsistencies, alerts, resolved_art),
    }


def compare_art_number(cat_data: dict, art_data: Optional[dict]) -> List[str]:
    inconsistencies: List[str] = []

    cat_art = cat_data.get("numero_art")
    art_number = (art_data or {}).get("numero_art")

    if cat_art and art_number and cat_art != art_number:
        inconsistencies.append("Numero da ART divergente entre CAT e ART informada.")

    return inconsistencies


def compare_professional(cat_data: dict, art_data: Optional[dict]) -> List[str]:
    inconsistencies: List[str] = []

    cat_name = cat_data.get("nome_profissional")
    art_name = (art_data or {}).get("nome_profissional")

    if not cat_name or not art_name:
        return inconsistencies

    similarity = SequenceMatcher(None, _normalize_text(cat_name), _normalize_text(art_name)).ratio()
    if similarity < 0.88:
        inconsistencies.append("Nome do profissional divergente ou pouco similar entre CAT e ART.")

    return inconsistencies


def compare_dates(cat_data: dict, art_data: Optional[dict]) -> List[str]:
    inconsistencies: List[str] = []

    if not art_data:
        return inconsistencies

    cat_start = _parse_date(cat_data.get("data_inicio"))
    cat_end = _parse_date(cat_data.get("data_fim"))
    art_start = _parse_date(art_data.get("data_inicio"))
    art_end = _parse_date(art_data.get("data_fim"))

    if not all([cat_start, cat_end, art_start, art_end]):
        return inconsistencies

    if cat_start < art_start:
        inconsistencies.append("Data de inicio da CAT esta antes do periodo registrado na ART.")

    if cat_end > art_end:
        inconsistencies.append("Data de fim da CAT ultrapassa o periodo registrado na ART.")

    return inconsistencies


def compare_description_vs_period(cat_data: dict) -> List[str]:
    alerts: List[str] = []

    description = str(cat_data.get("descricao_servico") or "").strip()
    cat_start = _parse_date(cat_data.get("data_inicio"))
    cat_end = _parse_date(cat_data.get("data_fim"))

    if not description or not cat_start or not cat_end:
        return alerts

    duration_days = (cat_end - cat_start).days
    normalized_description = _normalize_text(description)

    if duration_days <= 3 and any(keyword in normalized_description for keyword in ("obra", "execucao", "residencial")):
        alerts.append("O periodo informado parece muito curto para a descricao do servico executado.")

    return alerts


def generate_summary(inconsistencies: List[str], alerts: List[str], art_data: Optional[dict]) -> str:
    if inconsistencies:
        return (
            "Os dados da CAT estao inconsistentes com a ART analisada, especialmente em campos essenciais do documento. "
            "Recomenda-se revisar o vinculo entre ART, profissional e periodo de execucao."
        )

    if alerts and art_data:
        return (
            "A CAT esta compativel com a ART consultada, mas ha alertas que merecem revisao para aumentar a seguranca da analise."
        )

    if alerts:
        return (
            "A comparacao nao encontrou inconsistencias criticas, mas faltam elementos para uma auditoria mais forte. "
            "Revise os alertas antes de aprovar o documento."
        )

    return "Os dados da CAT estao compativeis com a ART analisada e nao foram encontradas inconsistencias relevantes."


def _resolve_art(cat_data: dict, art_data: Optional[dict]) -> tuple[Optional[dict], List[str]]:
    alerts: List[str] = []

    if art_data:
        return _normalize_document(art_data), alerts

    cat_art_number = cat_data.get("numero_art")
    if not cat_art_number:
        return None, alerts

    alerts.append("ART nao fornecida manualmente. Foi realizada busca automatica na base simulada.")
    fetched_art = ART_DATABASE.get(cat_art_number)

    if fetched_art is None:
        alerts.append("ART nao encontrada na base simulada para o numero informado.")
        return None, alerts

    return _normalize_document(fetched_art), alerts


def _normalize_document(data: Optional[dict]) -> Dict[str, Optional[str]]:
    if not data:
        return {}

    return {
        "numero_art": _clean_value(data.get("numero_art")),
        "nome_profissional": _clean_value(data.get("nome_profissional")),
        "data_inicio": _clean_value(data.get("data_inicio")),
        "data_fim": _clean_value(data.get("data_fim")),
        "descricao_servico": _clean_value(data.get("descricao_servico")),
    }


def _clean_value(value: Any) -> Optional[str]:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _parse_date(value: Optional[str]) -> Optional[datetime.date]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%d/%m/%Y").date()
    except ValueError:
        return None


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(value).lower().strip())
    without_accents = "".join(char for char in normalized if not unicodedata.combining(char))
    return " ".join(without_accents.split())


def _dedupe(items: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
