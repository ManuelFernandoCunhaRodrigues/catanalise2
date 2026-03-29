import re
import unicodedata
from typing import Optional


DATE_PATTERN = r"\d{2}/\d{2}/\d{4}"
SECTION_BREAK_LABELS = (
    "numero art",
    "art",
    "contratante",
    "cliente",
    "responsavel tecnico",
    "nome do profissional",
    "descricao do servico",
    "descricao dos servicos",
    "objeto",
    "atividades executadas",
)


def extract_fields(text: str) -> dict[str, Optional[str]]:
    """
    Extracts the main CAT fields with lightweight heuristics that are resilient to OCR noise.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    normalized_lines = [_normalize_ascii(line) for line in lines]
    normalized_text = _normalize_ascii(_normalize_spaces(text))

    range_start, range_end = _extract_date_range(normalized_text)
    execution_date = _search_first([rf"\b({DATE_PATTERN})\b"], normalized_text)

    data_inicio = _extract_date_from_labels(
        lines,
        normalized_lines,
        ["data de inicio", "inicio da obra", "inicio", "periodo de inicio"],
    ) or range_start
    data_fim = _extract_date_from_labels(
        lines,
        normalized_lines,
        ["data de fim", "fim da obra", "termino", "conclusao", "periodo de fim"],
    ) or range_end

    return {
        "nome_profissional": _extract_named_value(
            lines,
            normalized_lines,
            ["nome do profissional", "profissional", "responsavel tecnico", "engenheiro responsavel"],
        ),
        "numero_art": _search_first(
            [
                r"\bart(?:\s|:|n[o.]*){0,3}(\d{6,})\b",
                r"\b(?:registro|numero da art|n art)\s*:?\s*(\d{6,})\b",
            ],
            normalized_text,
        ),
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "data_execucao": _extract_date_from_labels(
            lines,
            normalized_lines,
            ["data de execucao", "execucao", "periodo"],
        )
        or data_inicio
        or execution_date,
        "descricao_servico": _extract_description(lines, normalized_lines),
        "contratante": _extract_named_value(
            lines,
            normalized_lines,
            ["contratante", "cliente", "tomador", "empresa contratante"],
        ),
    }


def _extract_named_value(lines: list[str], normalized_lines: list[str], labels: list[str]) -> Optional[str]:
    for index, normalized_line in enumerate(normalized_lines):
        for label in labels:
            if label not in normalized_line:
                continue

            same_line_value = _extract_value_after_colon(lines[index])
            if same_line_value:
                return _cleanup_text(same_line_value)

            next_line = _extract_next_meaningful_line(lines, normalized_lines, index)
            if next_line:
                return _cleanup_text(next_line)

    return None


def _extract_date_from_labels(lines: list[str], normalized_lines: list[str], labels: list[str]) -> Optional[str]:
    for index, normalized_line in enumerate(normalized_lines):
        for label in labels:
            if label not in normalized_line:
                continue

            same_line_match = re.search(DATE_PATTERN, lines[index])
            if same_line_match:
                return same_line_match.group(0)

            next_line = _extract_next_meaningful_line(lines, normalized_lines, index)
            if next_line:
                next_line_match = re.search(DATE_PATTERN, next_line)
                if next_line_match:
                    return next_line_match.group(0)

    return None


def _extract_date_range(normalized_text: str) -> tuple[Optional[str], Optional[str]]:
    match = re.search(
        rf"\b({DATE_PATTERN})\s*(?:a|ate|-|/)\s*({DATE_PATTERN})\b",
        normalized_text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None, None

    return match.group(1), match.group(2)


def _extract_description(lines: list[str], normalized_lines: list[str]) -> Optional[str]:
    labels = ["descricao do servico", "descricao dos servicos", "objeto", "atividades executadas"]

    for index, normalized_line in enumerate(normalized_lines):
        if not any(label in normalized_line for label in labels):
            continue

        inline_value = _extract_value_after_colon(lines[index])
        if inline_value:
            return _cleanup_text(inline_value)

        collected: list[str] = []
        for candidate_line, candidate_normalized in zip(lines[index + 1 :], normalized_lines[index + 1 :]):
            if any(label in candidate_normalized for label in SECTION_BREAK_LABELS):
                break

            cleaned_candidate = _cleanup_text(candidate_line)
            if cleaned_candidate:
                collected.append(cleaned_candidate)

            if len(" ".join(collected)) >= 160:
                break

        if collected:
            return _cleanup_text(" ".join(collected))

    meaningful_lines = [line.strip() for line in lines if len(line.strip()) > 25]
    return _cleanup_text(meaningful_lines[0]) if meaningful_lines else None


def _extract_next_meaningful_line(lines: list[str], normalized_lines: list[str], start_index: int) -> Optional[str]:
    for offset in range(start_index + 1, len(lines)):
        if any(label in normalized_lines[offset] for label in SECTION_BREAK_LABELS):
            return None

        candidate = _cleanup_text(lines[offset])
        if candidate:
            return candidate

    return None


def _extract_value_after_colon(line: str) -> Optional[str]:
    if ":" not in line:
        return None

    _, value = line.split(":", 1)
    return value.strip() or None


def _search_first(patterns: list[str], text: str) -> Optional[str]:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return _cleanup_text(match.group(1))
    return None


def _normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _normalize_ascii(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(char for char in normalized if not unicodedata.combining(char))
    return _normalize_spaces(without_accents.lower())


def _cleanup_text(value: Optional[str]) -> Optional[str]:
    if not value:
        return None

    cleaned = re.sub(r"\s+", " ", value).strip(" :-")
    cleaned = re.sub(r"\b(?:cpf|cnpj|rnp|crea|art)\b.*$", "", cleaned, flags=re.IGNORECASE).strip(" :-")
    return cleaned or None
