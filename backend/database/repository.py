import json
from typing import Any, Dict, List, Optional

from database.db import connection_context
from database.models import row_to_analysis_detail, row_to_analysis_summary


def save_analysis(data: Dict[str, Any]) -> int:
    """
    Salva uma analise no historico, convertendo listas para JSON string.
    """
    with connection_context() as connection:
        cursor = connection.execute(
            """
            INSERT INTO analyses (filename, score, nivel, erros, alertas, inconsistencias, analysis_payload)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["filename"],
                data["score"],
                data["nivel"],
                json.dumps(data.get("erros", []), ensure_ascii=False),
                json.dumps(data.get("alertas", []), ensure_ascii=False),
                json.dumps(data.get("inconsistencias", []), ensure_ascii=False),
                json.dumps(data.get("analysis_payload"), ensure_ascii=False),
            ),
        )
        return int(cursor.lastrowid)


def get_all_analyses() -> List[Dict[str, Any]]:
    with connection_context() as connection:
        rows = connection.execute(
            """
            SELECT id, filename, score, nivel, data_criacao
            FROM analyses
            ORDER BY id DESC
            """
        ).fetchall()

    return [row_to_analysis_summary(row) for row in rows]


def get_analysis_by_id(analysis_id: int) -> Optional[Dict[str, Any]]:
    with connection_context() as connection:
        row = connection.execute(
            """
            SELECT id, filename, score, nivel, erros, alertas, inconsistencias, analysis_payload, data_criacao
            FROM analyses
            WHERE id = ?
            """,
            (analysis_id,),
        ).fetchone()

    if row is None:
        return None

    return row_to_analysis_detail(row)
