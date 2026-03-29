import re
from typing import Dict, Optional


def extract_fields(text: str) -> Dict[str, Optional[str]]:
    """
    Parser heurístico para MVP: simples o bastante para demo, útil o bastante para funcionar.
    """
    normalized_text = _normalize_spaces(text)
    original_lines = [line.strip() for line in text.splitlines() if line.strip()]

    return {
        "nome_profissional": _extract_nome_profissional(text, normalized_text, original_lines),
        "numero_art": _search_first(
            [
                r"\bART(?:\s|:|n[ºo.]*){0,3}(\d{6,})\b",
                r"\b(?:Registro|N[ºo.]*\s*ART)\s*:?\s*(\d{6,})\b",
            ],
            normalized_text,
        ),
        "data_execucao": _search_first(
            [
                r"\b(?:Data de Execu[cç][aã]o|Execu[cç][aã]o|Per[ií]odo)\s*:?\s*(\d{2}/\d{2}/\d{4})\b",
                r"\b(\d{2}/\d{2}/\d{4})\b",
            ],
            normalized_text,
        ),
        "descricao_servico": _extract_descricao_servico(text),
    }


def _extract_nome_profissional(text: str, normalized_text: str, lines: list[str]) -> Optional[str]:
    direct_match = _search_first(
        [
            r"\b(?:Profissional(?:\s+Respons[aá]vel)?|Respons[aá]vel T[eé]cnico|Engenheiro(?:\s+Respons[aá]vel)?)\s*:?\s*([A-ZÀ-Ý][A-Za-zÀ-ÿ\s]{5,})",
        ],
        text,
    )
    if direct_match:
        return _cleanup_name(direct_match)

    upper_patterns = [
        "NOME DO PROFISSIONAL",
        "PROFISSIONAL",
        "RESPONSAVEL TECNICO",
        "RESPONSÁVEL TÉCNICO",
    ]
    for index, line in enumerate(lines):
        comparable = _strip_accents_for_compare(line).upper()
        if any(pattern in comparable for pattern in upper_patterns):
            if index + 1 < len(lines):
                candidate = _cleanup_name(lines[index + 1])
                if candidate:
                    return candidate

    fallback_name = _search_first(
        [r"\b([A-ZÀ-Ý]{2,}(?:\s+[A-ZÀ-Ý]{2,}){1,5})\b"],
        normalized_text.upper(),
    )
    return _cleanup_name(fallback_name) if fallback_name else None


def _extract_descricao_servico(text: str) -> Optional[str]:
    patterns = [
        r"(?:Descri[cç][aã]o(?:\s+do)?\s+Servi[cç]o|Objeto|Atividades Executadas)\s*:?\s*(.+?)(?:\n{2,}|ART\b|CREA\b|Contratante\b|Profissional\b|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            description = _normalize_spaces(match.group(1))
            if description:
                return description

    meaningful_lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 25]
    if meaningful_lines:
        return meaningful_lines[0]

    return None


def _search_first(patterns: list[str], text: str) -> Optional[str]:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _cleanup_name(value: Optional[str]) -> Optional[str]:
    if not value:
        return None

    cleaned = re.sub(r"\s+", " ", value).strip(" :-")
    cleaned = re.sub(r"\b(?:CPF|RNP|CREA|ART)\b.*$", "", cleaned, flags=re.IGNORECASE).strip(" :-")
    return cleaned.title() if cleaned else None


def _strip_accents_for_compare(value: str) -> str:
    replacements = str.maketrans("ÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ", "AAAAEEEIIIOOOOUUUC")
    return value.translate(replacements)
