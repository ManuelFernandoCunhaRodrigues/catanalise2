from datetime import datetime
from typing import Any, Dict, List, Optional


GENERIC_DESCRIPTIONS = {
    "obra",
    "servico",
    "serviço",
    "atividade",
}

CRITICAL_FIELDS = [
    "nome_profissional",
    "numero_art",
    "data_inicio",
    "data_fim",
    "descricao_servico",
    "contratante",
]


def detect_fraud(cat_data: dict, art_data: dict = None) -> dict:
    """
    Motor simples de auditoria automatizada para hackathon.
    Ele separa fraude confirmada de sinais fracos para apoiar decisão humana.
    """
    normalized_cat = _normalize_payload(cat_data)
    normalized_art = _normalize_payload(art_data or {})

    fraud_indicators: List[str] = []
    alert_indicators: List[str] = []
    details: List[str] = []

    date_result = check_date_inconsistency(normalized_cat)
    fraud_indicators.extend(date_result["fraudes"])
    alert_indicators.extend(date_result["alertas"])
    details.extend(date_result["detalhes"])

    art_result = compare_with_art(normalized_cat, normalized_art) if art_data else {
        "fraudes": [],
        "alertas": [],
        "detalhes": [],
    }
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


def check_date_inconsistency(cat_data: dict) -> dict:
    fraudes: List[str] = []
    alertas: List[str] = []
    detalhes: List[str] = []

    start_date = _parse_date(cat_data.get("data_inicio"))
    end_date = _parse_date(cat_data.get("data_fim"))

    if start_date and end_date and end_date < start_date:
        fraudes.append("Inconsistência crítica de datas")
        detalhes.append("Data de fim anterior à data de início.")

    if start_date and end_date:
        duration_days = (end_date - start_date).days
        if duration_days <= 1:
            alertas.append("Duração muito curta")
            detalhes.append("Duração de execução igual ou inferior a 1 dia. Verifique se o período está correto.")

    return {"fraudes": fraudes, "alertas": alertas, "detalhes": detalhes}


def compare_with_art(cat_data: dict, art_data: dict) -> dict:
    fraudes: List[str] = []
    alertas: List[str] = []
    detalhes: List[str] = []

    if not art_data:
        return {"fraudes": fraudes, "alertas": alertas, "detalhes": detalhes}

    cat_name = _normalize_text(cat_data.get("nome_profissional"))
    art_name = _normalize_text(art_data.get("nome_profissional"))
    if cat_name and art_name and cat_name != art_name:
        fraudes.append("Divergência entre CAT e ART")
        detalhes.append("Nome do profissional divergente entre CAT e ART.")

    for field_name in ("data_inicio", "data_fim"):
        cat_value = cat_data.get(field_name)
        art_value = art_data.get(field_name)
        if _has_value(cat_value) and _has_value(art_value) and cat_value != art_value:
            fraudes.append("Divergência entre CAT e ART")
            detalhes.append(f"{_humanize_field(field_name)} diferente entre CAT e ART.")

    return {"fraudes": fraudes, "alertas": alertas, "detalhes": detalhes}


def detect_suspicious_patterns(cat_data: dict) -> dict:
    fraudes: List[str] = []
    alertas: List[str] = []
    detalhes: List[str] = []

    missing_fields = [field for field in CRITICAL_FIELDS if not _has_value(cat_data.get(field))]
    if missing_fields:
        fraudes.append("Campos críticos incompletos")
        detalhes.append(
            "Ausência de dados críticos no documento: " + ", ".join(missing_fields) + "."
        )

    numero_art = str(cat_data.get("numero_art") or "").strip()
    if numero_art and any(not char.isdigit() for char in numero_art):
        fraudes.append("Número ART inválido")
        detalhes.append("Número ART contém letras ou caracteres não numéricos.")
    elif numero_art and len(numero_art) < 6:
        alertas.append("Número ART suspeito")
        detalhes.append("Número ART muito curto. Revise a numeração informada.")

    descricao = str(cat_data.get("descricao_servico") or "").strip()
    normalized_description = _normalize_text(descricao)
    if normalized_description in GENERIC_DESCRIPTIONS:
        alertas.append("Descrição genérica")
        detalhes.append("Descrição genérica pode indicar baixa qualidade ou fraude.")

    if descricao and len(descricao) < 20:
        alertas.append("Texto muito curto")
        detalhes.append("Descrição do serviço muito curta para sustentar validação técnica.")

    if descricao and _has_repeated_data(descricao):
        alertas.append("Padrão repetitivo")
        detalhes.append("Texto com repetição excessiva, o que pode indicar documento montado artificialmente.")

    if descricao and not _has_technical_detail(descricao):
        alertas.append("Ausência de detalhes técnicos")
        detalhes.append("Não foram encontrados termos técnicos suficientes na descrição do serviço.")

    return {"fraudes": fraudes, "alertas": alertas, "detalhes": detalhes}


def evaluate_risk(fraudes: List[str], alertas: List[str]) -> str:
    fraud_count = len(fraudes)
    alert_count = len(alertas)

    if fraud_count >= 2:
        return "alto"
    if fraud_count == 1 and alert_count > 0:
        return "medio"
    if alert_count > 0:
        return "baixo"
    return "baixo"


def _check_high_risk_combination(cat_data: dict) -> dict:
    fraudes: List[str] = []
    detalhes: List[str] = []

    descricao = _normalize_text(cat_data.get("descricao_servico"))
    start_date = _parse_date(cat_data.get("data_inicio"))
    end_date = _parse_date(cat_data.get("data_fim"))
    numero_art = str(cat_data.get("numero_art") or "").strip()

    short_duration = False
    if start_date and end_date:
        short_duration = (end_date - start_date).days <= 1

    invalid_art = (not numero_art) or len(numero_art) < 6 or any(not char.isdigit() for char in numero_art)
    generic_description = descricao in GENERIC_DESCRIPTIONS

    if generic_description and short_duration and invalid_art:
        fraudes.append("Combinação de alto risco")
        detalhes.append(
            "Combinação de descrição genérica, duração curta e ART inválida indica documento possivelmente falso."
        )

    return {"fraudes": fraudes, "detalhes": detalhes}


def _normalize_payload(data: Optional[dict]) -> Dict[str, Optional[str]]:
    if not data:
        return {}
    return {
        "nome_profissional": _clean_value(data.get("nome_profissional")),
        "numero_art": _clean_value(data.get("numero_art")),
        "data_inicio": _clean_value(data.get("data_inicio")),
        "data_fim": _clean_value(data.get("data_fim")),
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
    lowered = str(value or "").lower().strip()
    for original, replacement in (
        ("á", "a"),
        ("à", "a"),
        ("â", "a"),
        ("ã", "a"),
        ("é", "e"),
        ("ê", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ô", "o"),
        ("õ", "o"),
        ("ú", "u"),
        ("ç", "c"),
    ):
        lowered = lowered.replace(original, replacement)
    return " ".join(lowered.split())


def _has_repeated_data(text: str) -> bool:
    words = [word for word in _normalize_text(text).split(" ") if word]
    if len(words) < 4:
        return False
    return len(set(words)) <= max(1, len(words) // 3)


def _has_technical_detail(text: str) -> bool:
    technical_terms = {
        "execucao",
        "execução",
        "estrutura",
        "projeto",
        "fundacao",
        "fundação",
        "instalacao",
        "instalação",
        "gerenciamento",
        "acompanhamento",
        "fiscalizacao",
        "fiscalização",
        "dimensionamento",
        "concreto",
        "eletrica",
        "elétrica",
        "hidraulica",
        "hidráulica",
    }
    normalized = set(_normalize_text(text).split())
    return len(normalized.intersection(technical_terms)) > 0


def _humanize_field(field_name: str) -> str:
    labels = {
        "data_inicio": "Data de início",
        "data_fim": "Data de fim",
    }
    return labels.get(field_name, field_name)


def _dedupe(items: List[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
