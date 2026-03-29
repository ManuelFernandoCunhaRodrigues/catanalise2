import os

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from auth import require_api_token
from database.db import init_db
from database.repository import get_all_analyses, get_analysis_by_id, save_analysis
from services.art_integration import compare_cat_with_art
from services.processor import process_file


def _resolve_allowed_origins() -> list[str]:
    raw_origins = os.getenv("ALLOWED_ORIGINS", "").strip()
    if not raw_origins:
        return [
            "http://127.0.0.1:8080",
            "http://localhost:8080",
            "http://127.0.0.1:4173",
            "http://localhost:4173",
        ]

    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


def _has_value(value: object) -> bool:
    return value is not None and str(value).strip() != ""


app = FastAPI(
    title="CAT Analyzer Backend",
    description="Backend para upload, analise, historico e demonstracao guiada de CAT.",
    version="0.3.0",
)


allowed_origins = _resolve_allowed_origins()
allow_all_origins = "*" in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all_origins else allowed_origins,
    allow_credentials=not allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


class CATARTInput(BaseModel):
    numero_art: str | None = None
    nome_profissional: str | None = None
    data_inicio: str | None = None
    data_fim: str | None = None
    data_execucao: str | None = None
    descricao_servico: str | None = None
    contratante: str | None = None


class CATARTComparisonInput(BaseModel):
    cat_data: CATARTInput
    art_data: CATARTInput | None = None


@app.get("/")
async def root() -> dict:
    return {"status": "API rodando"}


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/demo")
async def demo_payload() -> dict:
    return {
        "filename": "CAT-DEMO-2026.pdf",
        "status": "processado",
        "resultado": {
            "mensagem": "Documento demo processado com sinais relevantes de risco e necessidade de revisao humana.",
            "score": 38,
            "nivel": "baixo",
        },
        "dados_extraidos": {
            "nome_profissional": "Joao Silva",
            "numero_art": "123456789",
            "data_inicio": "15/03/2023",
            "data_fim": "10/03/2023",
            "data_execucao": "15/03/2023",
            "descricao_servico": "obra",
            "contratante": "Empresa X",
        },
        "validacao": {
            "valid": False,
            "erros": ["Data de fim anterior a data de inicio."],
            "alertas": ["Descricao muito generica, detalhe melhor o servico executado."],
            "inconsistencias": ["Data de inicio da CAT esta antes do periodo registrado na ART."],
            "score": 45,
            "nivel": "baixo",
        },
        "comparacao_art": {
            "consistente": False,
            "inconsistencias": ["Data de inicio da CAT esta antes do periodo registrado na ART."],
            "alertas": ["ART nao fornecida manualmente. Foi realizada busca automatica na base simulada."],
            "resumo": "Os dados da CAT estao inconsistentes com a ART analisada, especialmente em campos essenciais do documento.",
            "art_encontrada": {
                "numero_art": "123456789",
                "nome_profissional": "Joao Silva",
                "data_inicio": "01/01/2023",
                "data_fim": "01/02/2023",
            },
        },
        "fraude": {
            "fraude_detectada": True,
            "nivel_risco": "alto",
            "score_fraude": 85,
            "fraudes": ["Inconsistencia critica de datas", "Divergencia entre CAT e ART"],
            "alertas": ["Descricao generica"],
            "indicadores": ["Inconsistencia critica de datas", "Divergencia entre CAT e ART", "Descricao generica"],
            "detalhes": [
                "Data de fim anterior a data de inicio.",
                "Nome do profissional divergente entre CAT e ART.",
                "Descricao generica pode indicar baixa qualidade ou fraude.",
            ],
            "regras_avaliadas": [
                {"codigo": "date_reverse_order", "peso": 35, "acionada": True, "explicacao": "Periodo invertido entre inicio e fim."}
            ],
        },
        "score_confiabilidade": {
            "score": 38,
            "nivel": "baixo",
            "justificativa": [
                "Erro critico reduz significativamente a confiabilidade: data inconsistente.",
                "Inconsistencia reduz a seguranca da analise: periodo incompativel com a ART.",
                "Alerta indica necessidade de revisao: descricao generica.",
            ],
            "resumo": "Documento com baixa confiabilidade e necessidade de revisao antes da aprovacao.",
        },
        "feedback_inteligente": {
            "status": "reprovado",
            "resumo_geral": "O sistema encontrou erro de data, descricao generica e divergencia com ART.",
            "recomendacoes": [
                "Corrigir o periodo de execucao.",
                "Detalhar melhor a descricao do servico.",
                "Confirmar a ART correspondente.",
            ],
            "feedback": [
                {"tipo": "erro", "mensagem": "A data de fim esta anterior a data de inicio.", "sugestao": "Verifique e corrija o periodo de execucao da obra."}
            ],
        },
    }


@app.get("/history")
async def history(_: None = Depends(require_api_token)) -> list[dict]:
    try:
        return await run_in_threadpool(get_all_analyses)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Falha interna ao buscar o historico.") from exc


@app.get("/history/{analysis_id}")
async def history_by_id(analysis_id: int, _: None = Depends(require_api_token)) -> dict:
    try:
        analysis = await run_in_threadpool(get_analysis_by_id, analysis_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Falha interna ao buscar a analise.") from exc

    if analysis is None:
        raise HTTPException(status_code=404, detail="Analise nao encontrada.")

    return analysis


@app.post("/compare-cat-art")
async def compare_cat_art(payload: CATARTComparisonInput, _: None = Depends(require_api_token)) -> dict:
    cat_payload = payload.cat_data.model_dump()
    if not any(_has_value(value) for value in cat_payload.values()):
        raise HTTPException(status_code=400, detail="Informe ao menos um campo da CAT para realizar a comparacao.")

    try:
        art_payload = payload.art_data.model_dump() if payload.art_data else None
        return await run_in_threadpool(compare_cat_with_art, cat_payload, art_payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Falha interna ao comparar CAT com ART.") from exc


@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...), _: None = Depends(require_api_token)) -> dict:
    try:
        analysis_result = await process_file(file)
        persistence_payload = analysis_result.pop("_persistencia", None) or {}
        analysis_id = await run_in_threadpool(
            save_analysis,
            {
                "filename": analysis_result["filename"],
                "score": persistence_payload.get("score", analysis_result["resultado"]["score"]),
                "nivel": persistence_payload.get("nivel", analysis_result["resultado"]["nivel"]),
                "erros": persistence_payload.get("erros", []),
                "alertas": persistence_payload.get("alertas", []),
                "inconsistencias": persistence_payload.get("inconsistencias", []),
                "analysis_payload": persistence_payload.get("analysis_payload", analysis_result),
            },
        )
        analysis_result["analysis_id"] = analysis_id
        return analysis_result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Falha interna ao processar o documento.") from exc
