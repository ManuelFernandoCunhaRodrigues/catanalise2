import json
from typing import Any, Dict, List, Optional

from sqlalchemy import select

from database.db import session_context
from database.models import AnalysisRecord, row_to_analysis_detail, row_to_analysis_summary


def save_analysis(data: Dict[str, Any]) -> int:
    with session_context() as session:
        record = AnalysisRecord(
            filename=data["filename"],
            score=int(data["score"]),
            nivel=str(data["nivel"]),
            erros=json.dumps(data.get("erros", []), ensure_ascii=False),
            alertas=json.dumps(data.get("alertas", []), ensure_ascii=False),
            inconsistencias=json.dumps(data.get("inconsistencias", []), ensure_ascii=False),
            analysis_payload=json.dumps(data.get("analysis_payload"), ensure_ascii=False),
        )
        session.add(record)
        session.flush()
        return int(record.id)


def get_all_analyses() -> List[Dict[str, Any]]:
    with session_context() as session:
        rows = session.execute(select(AnalysisRecord).order_by(AnalysisRecord.id.desc())).scalars().all()
        return [row_to_analysis_summary(_record_to_mapping(row)) for row in rows]


def get_analysis_by_id(analysis_id: int) -> Optional[Dict[str, Any]]:
    with session_context() as session:
        row = session.get(AnalysisRecord, analysis_id)

    if row is None:
        return None

    return row_to_analysis_detail(_record_to_mapping(row))


def _record_to_mapping(row: AnalysisRecord) -> Dict[str, Any]:
    return {
        "id": row.id,
        "filename": row.filename,
        "score": row.score,
        "nivel": row.nivel,
        "erros": row.erros,
        "alertas": row.alertas,
        "inconsistencias": row.inconsistencias,
        "analysis_payload": row.analysis_payload,
        "data_criacao": row.data_criacao.isoformat() if row.data_criacao else None,
    }
