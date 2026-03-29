from typing import Any, Optional

from services.utils import build_document_payload, dedupe, has_value, normalize_text, parse_date


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
    normalized_cat = build_document_payload(cat_data)
    normalized_art = build_document_payload(art_data or {})

    fraud_indicators: list[str] = []
    alert_indicators: list[str] = []
    details: list[str] = []
    rules: list[dict[str, Any]] = []
    fraud_score = 0

    date_result = check_date_inconsistency(normalized_cat)
    fraud_indicators.extend(date_result["fraudes"])
    alert_indicators.extend(date_result["alertas"])
    details.extend(date_result["detalhes"])
    rules.extend(date_result["regras"])
    fraud_score += date_result["score"]

    if art_data:
        art_result = compare_with_art(normalized_cat, normalized_art)
        fraud_indicators.extend(art_result["fraudes"])
        alert_indicators.extend(art_result["alertas"])
        details.extend(art_result["detalhes"])
        rules.extend(art_result["regras"])
        fraud_score += art_result["score"]

    pattern_result = detect_suspicious_patterns(normalized_cat)
    fraud_indicators.extend(pattern_result["fraudes"])
    alert_indicators.extend(pattern_result["alertas"])
    details.extend(pattern_result["detalhes"])
    rules.extend(pattern_result["regras"])
    fraud_score += pattern_result["score"]

    combined_result = _check_high_risk_combination(normalized_cat)
    fraud_indicators.extend(combined_result["fraudes"])
    details.extend(combined_result["detalhes"])
    rules.extend(combined_result["regras"])
    fraud_score += combined_result["score"]

    deduped_fraudes = dedupe(fraud_indicators)
    deduped_alertas = dedupe(alert_indicators)
    deduped_details = dedupe(details)
    deduped_rules = _dedupe_rules(rules)

    risk = evaluate_risk(deduped_fraudes, deduped_alertas)
    return {
        "fraude_detectada": len(deduped_fraudes) > 0,
        "nivel_risco": risk,
        "score_fraude": min(100, fraud_score),
        "fraudes": deduped_fraudes,
        "alertas": deduped_alertas,
        "indicadores": deduped_fraudes + deduped_alertas,
        "detalhes": deduped_details,
        "regras_avaliadas": deduped_rules,
    }


def check_date_inconsistency(cat_data: dict[str, Optional[str]]) -> dict[str, Any]:
    fraudes: list[str] = []
    alertas: list[str] = []
    detalhes: list[str] = []
    regras: list[dict[str, Any]] = []
    score = 0

    start_date = parse_date(cat_data.get("data_inicio") or cat_data.get("data_execucao"))
    end_date = parse_date(cat_data.get("data_fim"))

    if start_date and end_date and end_date < start_date:
        fraudes.append("Inconsistencia critica de datas")
        detalhes.append("Data de fim anterior a data de inicio.")
        regras.append(_build_rule("date_reverse_order", 35, True, "Periodo invertido entre inicio e fim."))
        score += 35

    if start_date and end_date:
        duration_days = (end_date - start_date).days
        if duration_days <= 1:
            alertas.append("Duracao muito curta")
            detalhes.append("Duracao de execucao igual ou inferior a 1 dia. Verifique se o periodo esta correto.")
            regras.append(_build_rule("short_duration", 10, True, "Duracao de execucao muito curta."))
            score += 10

    return {"fraudes": fraudes, "alertas": alertas, "detalhes": detalhes, "regras": regras, "score": score}


def compare_with_art(cat_data: dict[str, Optional[str]], art_data: dict[str, Optional[str]]) -> dict[str, Any]:
    fraudes: list[str] = []
    alertas: list[str] = []
    detalhes: list[str] = []
    regras: list[dict[str, Any]] = []
    score = 0

    if not art_data:
        return {"fraudes": fraudes, "alertas": alertas, "detalhes": detalhes, "regras": regras, "score": score}

    cat_name = normalize_text(cat_data.get("nome_profissional"))
    art_name = normalize_text(art_data.get("nome_profissional"))
    if cat_name and art_name and cat_name != art_name:
        fraudes.append("Divergencia entre CAT e ART")
        detalhes.append("Nome do profissional divergente entre CAT e ART.")
        regras.append(_build_rule("art_name_mismatch", 25, True, "Nome divergente em relacao a ART."))
        score += 25

    for field_name in ("data_inicio", "data_fim"):
        cat_value = cat_data.get(field_name)
        art_value = art_data.get(field_name)
        if has_value(cat_value) and has_value(art_value) and cat_value != art_value:
            fraudes.append("Divergencia entre CAT e ART")
            detalhes.append(f"{field_name.replace('_', ' ').capitalize()} diferente entre CAT e ART.")
            regras.append(_build_rule(f"{field_name}_art_mismatch", 20, True, f"{field_name} divergente em relacao a ART."))
            score += 20

    return {"fraudes": dedupe(fraudes), "alertas": alertas, "detalhes": dedupe(detalhes), "regras": regras, "score": score}


def detect_suspicious_patterns(cat_data: dict[str, Optional[str]]) -> dict[str, Any]:
    fraudes: list[str] = []
    alertas: list[str] = []
    detalhes: list[str] = []
    regras: list[dict[str, Any]] = []
    score = 0

    missing_essential = [field for field in ESSENTIAL_FIELDS if not has_value(cat_data.get(field))]
    has_any_date = has_value(cat_data.get("data_inicio")) or has_value(cat_data.get("data_fim")) or has_value(cat_data.get("data_execucao"))

    if len(missing_essential) >= 3 or {"nome_profissional", "numero_art"}.issubset(set(missing_essential)):
        fraudes.append("Campos criticos incompletos")
        detalhes.append("Ausencia de dados criticos no documento: " + ", ".join(missing_essential) + ".")
        regras.append(_build_rule("missing_critical_fields", 30, True, "Ausencia de campos essenciais para autenticidade."))
        score += 30
    elif missing_essential or not has_any_date:
        alertas.append("Campos importantes ausentes")
        missing_items = list(missing_essential)
        if not has_any_date:
            missing_items.append("datas")
        detalhes.append("Nem todos os campos esperados puderam ser confirmados: " + ", ".join(missing_items) + ".")
        regras.append(_build_rule("missing_relevant_fields", 8, True, "Campos importantes nao puderam ser confirmados."))
        score += 8

    numero_art = str(cat_data.get("numero_art") or "").strip()
    if numero_art and any(not char.isdigit() for char in numero_art):
        fraudes.append("Numero ART invalido")
        detalhes.append("Numero ART contem letras ou caracteres nao numericos.")
        regras.append(_build_rule("invalid_art_number", 25, True, "Numero ART contem caracteres invalidos."))
        score += 25
    elif numero_art and len(numero_art) < 6:
        alertas.append("Numero ART suspeito")
        detalhes.append("Numero ART muito curto. Revise a numeracao informada.")
        regras.append(_build_rule("short_art_number", 8, True, "Numero ART fora do tamanho esperado."))
        score += 8

    descricao = str(cat_data.get("descricao_servico") or "").strip()
    normalized_description = normalize_text(descricao)
    if normalized_description in GENERIC_DESCRIPTIONS:
        alertas.append("Descricao generica")
        detalhes.append("Descricao generica pode indicar baixa qualidade ou fraude.")
        regras.append(_build_rule("generic_description", 10, True, "Descricao excessivamente generica."))
        score += 10

    if descricao and len(descricao) < 20:
        alertas.append("Texto muito curto")
        detalhes.append("Descricao do servico muito curta para sustentar validacao tecnica.")
        regras.append(_build_rule("short_description", 8, True, "Descricao curta demais para validacao documental."))
        score += 8

    if descricao and _has_repeated_data(descricao):
        alertas.append("Padrao repetitivo")
        detalhes.append("Texto com repeticao excessiva, o que pode indicar documento montado artificialmente.")
        regras.append(_build_rule("repetitive_text", 12, True, "Texto com padrao repetitivo."))
        score += 12

    if descricao and not _has_technical_detail(descricao):
        alertas.append("Ausencia de detalhes tecnicos")
        detalhes.append("Nao foram encontrados termos tecnicos suficientes na descricao do servico.")
        regras.append(_build_rule("low_technical_density", 10, True, "Descricao com baixa densidade tecnica."))
        score += 10

    return {
        "fraudes": dedupe(fraudes),
        "alertas": dedupe(alertas),
        "detalhes": dedupe(detalhes),
        "regras": regras,
        "score": score,
    }


def evaluate_risk(fraudes: list[str], alertas: list[str]) -> str:
    fraud_count = len(fraudes)
    alert_count = len(alertas)

    if fraud_count >= 2 or (fraud_count >= 1 and alert_count >= 2):
        return "alto"
    if fraud_count == 1 or alert_count >= 3:
        return "medio"
    return "baixo"


def _check_high_risk_combination(cat_data: dict[str, Optional[str]]) -> dict[str, Any]:
    fraudes: list[str] = []
    detalhes: list[str] = []
    regras: list[dict[str, Any]] = []
    score = 0

    descricao = normalize_text(cat_data.get("descricao_servico"))
    start_date = parse_date(cat_data.get("data_inicio") or cat_data.get("data_execucao"))
    end_date = parse_date(cat_data.get("data_fim"))
    numero_art = str(cat_data.get("numero_art") or "").strip()

    short_duration = False
    if start_date and end_date:
        short_duration = (end_date - start_date).days <= 1

    invalid_art = (not numero_art) or len(numero_art) < 6 or any(not char.isdigit() for char in numero_art)
    generic_description = descricao in GENERIC_DESCRIPTIONS

    if generic_description and short_duration and invalid_art:
        fraudes.append("Combinacao de alto risco")
        detalhes.append("Combinacao de descricao generica, duracao curta e ART invalida indica documento possivelmente falso.")
        regras.append(_build_rule("high_risk_combination", 30, True, "Multiplos sinais fracos combinados elevam o risco."))
        score += 30

    return {"fraudes": fraudes, "detalhes": detalhes, "regras": regras, "score": score}


def _has_repeated_data(text: str) -> bool:
    words = [word for word in normalize_text(text).split(" ") if word]
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
    normalized = set(normalize_text(text).split())
    return len(normalized.intersection(technical_terms)) > 0


def _build_rule(code: str, weight: int, triggered: bool, explanation: str) -> dict[str, Any]:
    return {
        "codigo": code,
        "peso": weight,
        "acionada": triggered,
        "explicacao": explanation,
    }


def _dedupe_rules(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    result: list[dict[str, Any]] = []
    for item in items:
        key = item["codigo"]
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result
