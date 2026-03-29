from datetime import datetime
from typing import Any, Dict, List, Optional


# Campos essenciais para uma CAT minimamente auditável.
REQUIRED_FIELDS = [
    "nome_profissional",
    "numero_art",
    "descricao_servico",
    "contratante",
]

GENERIC_DESCRIPTIONS = {
    "servico",
    "serviço",
    "obra",
    "atividade",
    "execucao",
    "execução",
}


def validate_cat(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Função principal do motor de validação.
    Consolida erros, alertas, inconsistências e score final.
    """
    normalized = _normalize_input(data)

    errors = validate_required_fields(normalized)
    errors.extend(validate_format(normalized))

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


def validate_required_fields(data: Dict[str, Any]) -> List[str]:
    """
    Garante a presença dos campos essenciais e de pares obrigatórios.
    """
    errors: List[str] = []

    for field_name in REQUIRED_FIELDS:
        if not _has_value(data.get(field_name)):
            errors.append(f"Campo obrigatório ausente: {field_name}. Preencha esse dado para concluir a análise.")

    if _has_value(data.get("data_inicio")) and not _has_value(data.get("data_fim")):
        errors.append("Data de fim ausente. Informe a data final quando houver data de início.")

    if _has_value(data.get("numero_art")) and not _has_value(data.get("descricao_servico")):
        errors.append("ART informada sem descrição do serviço. Descreva a atividade vinculada à ART.")

    return errors


def validate_format(data: Dict[str, Any]) -> List[str]:
    """
    Valida formatos básicos para reduzir erros humanos de digitação.
    """
    errors: List[str] = []

    numero_art = data.get("numero_art")
    if _has_value(numero_art) and not str(numero_art).isdigit():
        errors.append("Número ART inválido. Use apenas números, sem letras ou símbolos.")

    for field_name in ("data_inicio", "data_fim"):
        field_value = data.get(field_name)
        if _has_value(field_value) and not _is_valid_date(str(field_value)):
            errors.append(f"{_humanize_field(field_name)} inválida. Use o formato DD/MM/AAAA.")

    return errors


def validate_consistency(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Analisa relação entre datas e regras temporais do documento.
    """
    inconsistencies: List[str] = []
    today = datetime.now().date()

    start_date = _parse_date(data.get("data_inicio"))
    end_date = _parse_date(data.get("data_fim"))

    if start_date and start_date > today:
        inconsistencies.append("Data de início no futuro. Verifique se a execução realmente já ocorreu.")

    if end_date and end_date > today:
        inconsistencies.append("Data de fim no futuro. Confirme se a CAT não foi preenchida com data incorreta.")

    if start_date and end_date and end_date < start_date:
        inconsistencies.append("Data de fim anterior à data de início. Ajuste o período informado.")

    return {"inconsistencias": inconsistencies}


def detect_suspicious_patterns(data: Dict[str, Any]) -> List[str]:
    """
    Regras simples que simulam indícios de baixa qualidade ou possível fraude.
    """
    alerts: List[str] = []

    descricao = str(data.get("descricao_servico") or "").strip()
    if descricao and len(descricao) < 20:
        alerts.append("Descrição muito curta. Inclua mais detalhes para tornar a análise confiável.")

    normalized_description = _normalize_text(descricao)
    if normalized_description in GENERIC_DESCRIPTIONS:
        alerts.append("Descrição muito genérica, detalhe melhor o serviço executado.")

    nome_profissional = str(data.get("nome_profissional") or "").strip()
    if nome_profissional and len(nome_profissional.split()) < 2:
        alerts.append("Nome profissional incompleto. Informe pelo menos nome e sobrenome.")

    numero_art = str(data.get("numero_art") or "").strip()
    if numero_art and (not numero_art.isdigit() or len(numero_art) < 6):
        alerts.append("Número ART suspeito ou muito curto. Revise a numeração informada.")

    start_date = _parse_date(data.get("data_inicio"))
    end_date = _parse_date(data.get("data_fim"))
    if start_date and end_date:
        duration_days = (end_date - start_date).days
        if duration_days <= 1:
            alerts.append("Período de execução muito curto. Confirme se as datas estão corretas.")

    return alerts


def calculate_score(*, errors: List[str], inconsistencies: List[str], alerts: List[str]) -> Dict[str, Any]:
    """
    Score explicável para demo: fácil de apresentar para banca e produto.
    """
    score = 100
    score -= len(errors) * 30
    score -= len(inconsistencies) * 15
    score -= len(alerts) * 10
    score = max(0, min(100, score))

    if score >= 80:
        level = "alto"
    elif score >= 50:
        level = "médio"
    else:
        level = "baixo"

    return {"score": score, "nivel": level}


def validate_fields(fields: Dict[str, Optional[str]]) -> Dict[str, Any]:
    """
    Compatibilidade com o fluxo atual do PDF analyzer.
    Mapeia o payload antigo para o novo motor.
    """
    payload = {
        "nome_profissional": fields.get("nome_profissional"),
        "numero_art": fields.get("numero_art"),
        "data_inicio": fields.get("data_inicio") or fields.get("data_execucao"),
        "data_fim": fields.get("data_fim"),
        "descricao_servico": fields.get("descricao_servico"),
        "contratante": fields.get("contratante"),
    }
    return validate_cat(payload)


def _normalize_input(data: Dict[str, Any]) -> Dict[str, Any]:
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
        "data_inicio": "Data de início",
        "data_fim": "Data de fim",
    }
    return labels.get(field_name, field_name)


def _normalize_text(value: str) -> str:
    lowered = value.lower().strip()
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
    return lowered
