import re
import unicodedata
from datetime import datetime
from typing import Any


DATE_FORMAT = "%d/%m/%Y"
DATE_PATTERN = r"\d{2}/\d{2}/\d{4}"


def clean_optional_str(value: Any) -> str | None:
    if value is None:
        return None

    cleaned = normalize_spaces(str(value))
    return cleaned or None


def has_value(value: Any) -> bool:
    return clean_optional_str(value) is not None


def parse_date(value: Any) -> datetime.date | None:
    cleaned = clean_optional_str(value)
    if not cleaned:
        return None

    try:
        return datetime.strptime(cleaned, DATE_FORMAT).date()
    except ValueError:
        return None


def is_valid_date(value: Any) -> bool:
    return parse_date(value) is not None


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_text(value: Any) -> str:
    normalized = unicodedata.normalize("NFKD", str(value or "").lower().strip())
    without_accents = "".join(char for char in normalized if not unicodedata.combining(char))
    return normalize_spaces(without_accents)


def dedupe(items: list[str]) -> list[str]:
    seen = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def build_document_payload(data: dict[str, Any]) -> dict[str, str | None]:
    return {
        "nome_profissional": clean_optional_str(data.get("nome_profissional")),
        "numero_art": clean_optional_str(data.get("numero_art")),
        "data_inicio": clean_optional_str(data.get("data_inicio")),
        "data_fim": clean_optional_str(data.get("data_fim")),
        "data_execucao": clean_optional_str(data.get("data_execucao")),
        "descricao_servico": clean_optional_str(data.get("descricao_servico")),
        "contratante": clean_optional_str(data.get("contratante")),
    }


def humanize_field(field_name: str) -> str:
    labels = {
        "data_inicio": "Data de inicio",
        "data_fim": "Data de fim",
        "data_execucao": "Data de execucao",
    }
    return labels.get(field_name, field_name)
