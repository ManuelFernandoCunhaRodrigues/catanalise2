import json
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import DateTime, Integer, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AnalysisRecord(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    nivel: Mapped[str] = mapped_column(Text, nullable=False)
    erros: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    alertas: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    inconsistencias: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    analysis_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_criacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


def row_to_analysis_summary(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "filename": row["filename"],
        "score": row["score"],
        "nivel": row["nivel"],
        "data_criacao": row["data_criacao"],
    }


def row_to_analysis_detail(row: Dict[str, Any]) -> Dict[str, Any]:
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
