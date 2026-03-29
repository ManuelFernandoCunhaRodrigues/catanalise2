import json
import sqlite3
from typing import Any, Dict


def row_to_analysis_summary(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "filename": row["filename"],
        "score": row["score"],
        "nivel": row["nivel"],
        "data_criacao": row["data_criacao"],
    }


def row_to_analysis_detail(row: sqlite3.Row) -> Dict[str, Any]:
    errors = _load_json_list(row["erros"])
    alerts = _load_json_list(row["alertas"])
    inconsistencies = _load_json_list(row["inconsistencias"])
    analysis_payload = _load_json_dict(row["analysis_payload"])

    if analysis_payload is None:
        analysis_payload = {
            "filename": row["filename"],
            "status": "processado",
            "resultado": {
                "mensagem": "Analise recuperada do historico.",
                "score": row["score"],
                "nivel": row["nivel"],
            },
            "validacao": {
                "valid": len(errors) == 0 and len(inconsistencies) == 0,
                "erros": errors,
                "alertas": alerts,
                "inconsistencias": inconsistencies,
                "score": row["score"],
                "nivel": row["nivel"],
            },
            "score_confiabilidade": {
                "score": row["score"],
                "nivel": row["nivel"],
                "justificativa": [],
                "resumo": "Analise carregada do historico sem payload detalhado persistido.",
            },
        }

    return {
        "id": row["id"],
        "filename": row["filename"],
        "score": row["score"],
        "nivel": row["nivel"],
        "erros": errors,
        "alertas": alerts,
        "inconsistencias": inconsistencies,
        "data_criacao": row["data_criacao"],
        "analysis": analysis_payload,
    }


def _load_json_list(value: str | None) -> list[str]:
    if not value:
        return []

    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []

    if not isinstance(parsed, list):
        return []

    return [str(item) for item in parsed]


def _load_json_dict(value: str | None) -> Dict[str, Any] | None:
    if not value:
        return None

    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return None

    return parsed if isinstance(parsed, dict) else None
