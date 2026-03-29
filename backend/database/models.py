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
    return {
        "id": row["id"],
        "filename": row["filename"],
        "score": row["score"],
        "nivel": row["nivel"],
        "erros": json.loads(row["erros"]),
        "alertas": json.loads(row["alertas"]),
        "inconsistencias": json.loads(row["inconsistencias"]),
        "data_criacao": row["data_criacao"],
    }
