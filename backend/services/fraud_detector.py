from datetime import datetime
from typing import Any, Optional
import unicodedata


GENERIC_DESCRIPTIONS = {
    "obra",
    "servico",
    "atividade",
    "execucao",
}

ESSENTIAL_FIELDS = [
    "nome_profissional",
    "numero_art",
    "descricao_servico",
    "contratante",
]


def detect_fraud(cat_data: dict[str, Any], art_data: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Lightweight fraud detector focused on explainable indicators for the hackathon flow.
    """
    normalized_cat = _normalize_payload(cat_data)
    normalized_art = _normalize_payload(art_data or {})

    fraud_indicators: list[str] = []
    alert_indicators: list[str] = []
    details: list[str] = []

    date_result = check_date_inconsistency(normalized_cat)
    fraud_indicators.extend(date_result["fraudes"])
    alert_indicators.extend(date_result["alertas"])
    details.extend(date_result["detalhes"])

    if art_data:
        art_result = compare_with_art(normalized_cat, normalized_art)
        fraud_indicators.extend(art_result["fraudes"])
        alert_indicators.extend(art_result["alertas"])
        details.extend(art_result["detalhes"])

    pattern_result = detect_suspicious_patterns(normalized_cat)
    fraud_indicators.extend(pattern_result["fraudes"])
    alert_indicators.extend(pattern_result["alertas"])
    details.extend(pattern_result["detalhes"])

    combined_result = _check_high_risk_combination(normalized_cat)
    fraud_indicators.extend(combined_result["fraudes"])
    details.extend(combined_result["detalhes"])

    deduped_fraudes = _dedupe(fraud_indicators)
    deduped_alertas = _dedupe(alert_indicators)
    deduped_details = _dedupe(details)

    risk = evaluate_risk(deduped_fraudes, deduped_alertas)
    return {
        "fraude_detectada": len(deduped_fraudes) > 0,
        "nivel_risco": risk,
        "fraudes": deduped_fraudes,
        "alertas": deduped_alertas,
        "indicadores": deduped_fraudes + deduped_alertas,
        "detalhes": deduped_details,
    }


def check_date_inconsistency(cat_data: dict[str, Optional[str]]) -> dict[str, list[str]]:
    fraudes: list[str] = []
    alertas: list[str] = []
    detalhes: list[str] = []

    start_date = _parse_date(cat_data.get("data_inicio") or cat_data.get("data_execucao"))
    end_date = _parse_date(cat_data.get("data_fim"))

    if start_date and end_date and end_date < start_date:
        fraudes.append("Inconsistencia critica de datas")
        detalhes.append("Data de fim anterior a data de inicio.")

    if start_date and end_date:
        duration_days = (end_date - start_date).days
        if duration_days <= 1:
            alertas.append("Duracao muito curta")
            detalhes.append("Duracao de execucao igual ou inferior a 1 dia. Verifique se o periodo esta correto.")

    return {"fraudes": fraudes, "alertas": alertas, "detalhes": detalhes}


def compare_with_art(cat_data: dict[str, Optional[str]], art_data: dict[str, Optional[str]]) -> dict[str, list[str]]:
    fraudes: list[str] = []
    alertas: list[str] = []
    detalhes: list[str] = []

    if not art_data:
        return {"fraudes": fraudes, "alertas": alertas, "detalhes": detalhes}

    cat_name = _normalize_text(cat_data.get("nome_profissional"))
    art_name = _normalize_text(art_data.get("nome_profissional"))
    if cat_name and art_name and cat_name != art_name:
        fraudes.append("Divergencia entre CAT e ART")
        detalhes.append("Nome do profissional divergente entre CAT e ART.")

    for field_name in ("data_inicio", "data_fim"):
        cat_value = cat_data.get(field_name)
        art_value = art_data.get(field_name)
        if _has_value(cat_value) and _has_value(art_value) and cat_value != art_value:
            fraudes.append("Divergencia entre CAT e ART")
            detalhes.append(f"{_humanize_field(field_name)} diferente entre CAT e ART.")

    return {"fraudes": _dedupe(fraudes), "alertas": alertas, "detalhes": _dedupe(detalhes)}


def detect_suspicious_patterns(cat_data: dict[str, Optional[str]]) -> dict[str, list[str]]:
    fraudes: list[str] = []
    alertas: list[str] = []
    detalhes: list[str] = []

    missing_essential = [field for field in ESSENTIAL_FIELDS if not _has_value(cat_data.get(field))]
    has_any_date = _has_value(cat_data.get("data_inicio")) or _has_value(cat_data.get("data_fim")) or _has_value(cat_data.get("data_execucao"))

    if len(missing_essential) >= 3 or {"nome_profissional", "numero_art"}.issubset(set(missing_essential)):
        fraudes.append("Campos criticos incompletos")
        detalhes.append("Ausencia de dados criticos no documento: " + ", ".join(missing_essential) + ".")
    elif missing_essential or not has_any_date:
        alertas.append("Campos importantes ausentes")
        missing_items = list(missing_essential)
        if not has_any_date:
            missing_items.append("datas")
        detalhes.append("Nem todos os campos esperados puderam ser confirmados: " + ", ".join(missing_items) + ".")

    numero_art = str(cat_data.get("numero_art") or "").strip()
    if numero_art and any(not char.isdigit() for char in numero_art):
        fraudes.append("Numero ART invalido")
        detalhes.append("Numero ART contem letras ou caracteres nao numericos.")
    elif numero_art and len(numero_art) < 6:
        alertas.append("Numero ART suspeito")
        detalhes.append("Numero ART muito curto. Revise a numeracao informada.")

    descricao = str(cat_data.get("descricao_servico") or "").strip()
    normalized_description = _normalize_text(descricao)
    if normalized_description in GENERIC_DESCRIPTIONS:
        alertas.append("Descricao generica")
        detalhes.append("Descricao generica pode indicar baixa qualidade ou fraude.")

    if descricao and len(descricao) < 20:
        alertas.append("Texto muito curto")
        detalhes.append("Descricao do servico muito curta para sustentar validacao tecnica.")

    if descricao and _has_repeated_data(descricao):
        alertas.append("Padrao repetitivo")
        detalhes.append("Texto com repeticao excessiva, o que pode indicar documento montado artificialmente.")

    if descricao and not _has_technical_detail(descricao):
        alertas.append("Ausencia de detalhes tecnicos")
        detalhes.append("Nao foram encontrados termos tecnicos suficientes na descricao do servico.")

    return {
        "fraudes": _dedupe(fraudes),
        "alertas": _dedupe(alertas),
        "detalhes": _dedupe(detalhes),
    }


def evaluate_risk(fraudes: list[str], alertas: list[str]) -> str:
    fraud_count = len(fraudes)
    alert_count = len(alertas)

    if fraud_count >= 2 or (fraud_count >= 1 and alert_count >= 2):
        return "alto"
    if fraud_count == 1 or alert_count >= 3:
        return "medio"
    return "baixo"


def _check_high_risk_combination(cat_data: dict[str, Optional[str]]) -> dict[str, list[str]]:
    fraudes: list[str] = []
    detalhes: list[str] = []

    descricao = _normalize_text(cat_data.get("descricao_servico"))
    start_date = _parse_date(cat_data.get("data_inicio") or cat_data.get("data_execucao"))
    end_date = _parse_date(cat_data.get("data_fim"))
    numero_art = str(cat_data.get("numero_art") or "").strip()

    short_duration = False
    if start_date and end_date:
        short_duration = (end_date - start_date).days <= 1

    invalid_art = (not numero_art) or len(numero_art) < 6 or any(not char.isdigit() for char in numero_art)
    generic_description = descricao in GENERIC_DESCRIPTIONS

    if generic_description and short_duration and invalid_art:
        fraudes.append("Combinacao de alto risco")
        detalhes.append(
            "Combinacao de descricao generica, duracao curta e ART invalida indica documento possivelmente falso."
        )

    return {"fraudes": fraudes, "detalhes": detalhes}


def _normalize_payload(data: Optional[dict[str, Any]]) -> dict[str, Optional[str]]:
    if not data:
        return {}
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


def _parse_date(value: Any) -> Optional[datetime.date]:
    if not _has_value(value):
        return None
    try:
        return datetime.strptime(str(value), "%d/%m/%Y").date()
    except ValueError:
        return None


def _has_value(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def _normalize_text(value: Any) -> str:
    normalized = unicodedata.normalize("NFKD", str(value or "").lower().strip())
    without_accents = "".join(char for char in normalized if not unicodedata.combining(char))
    return " ".join(without_accents.split())


def _has_repeated_data(text: str) -> bool:
    words = [word for word in _normalize_text(text).split(" ") if word]
    if len(words) < 4:
        return False
    return len(set(words)) <= max(1, len(words) // 3)


def _has_technical_detail(text: str) -> bool:
    technical_terms = {
        "execucao",
        "estrutura",
        "projeto",
        "fundacao",
        "instalacao",
        "gerenciamento",
        "acompanhamento",
        "fiscalizacao",
        "dimensionamento",
        "concreto",
        "eletrica",
        "hidraulica",
        "drenagem",
        "pavimentacao",
    }
    normalized = set(_normalize_text(text).split())
    return len(normalized.intersection(technical_terms)) > 0


def _humanize_field(field_name: str) -> str:
    labels = {
        "data_inicio": "Data de inicio",
        "data_fim": "Data de fim",
    }
    return labels.get(field_name, field_name)


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
