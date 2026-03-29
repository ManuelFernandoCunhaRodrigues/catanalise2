from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database.db import init_db
from database.repository import get_all_analyses, get_analysis_by_id, save_analysis
from services.art_integration import compare_cat_with_art
from services.processor import process_file


# API minima para hackathon: simples, clara e facil de conectar com qualquer frontend.
app = FastAPI(
    title="CAT Analyzer Backend",
    description="Backend minimo para upload, historico e demonstracao guiada de CAT.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializacao automatica do banco para a demo funcionar sem setup manual.
init_db()


class CATARTInput(BaseModel):
    numero_art: str | None = None
    nome_profissional: str | None = None
    data_inicio: str | None = None
    data_fim: str | None = None
    descricao_servico: str | None = None


class CATARTComparisonInput(BaseModel):
    cat_data: CATARTInput
    art_data: CATARTInput | None = None


@app.get("/")
async def root() -> dict:
    return {"status": "API rodando"}


@app.get("/demo")
async def demo_payload() -> dict:
    # Endpoint opcional para apresentacoes guiadas e testes rapidos de integracao.
    return {
        "filename": "CAT-DEMO-2026.pdf",
        "status": "processado",
        "resultado": {
            "mensagem": "Documento demo processado com sucesso",
            "score": 38,
            "nivel": "baixo",
        },
        "dados_extraidos": {
            "nome_profissional": "Joao Silva",
            "numero_art": "123456789",
            "data_inicio": "15/03/2023",
            "data_fim": "10/03/2023",
            "descricao_servico": "obra",
            "contratante": "Empresa X",
        },
        "validacao": {
            "erros": ["Data de fim anterior a data de inicio"],
            "alertas": ["Descricao generica"],
            "inconsistencias": ["Periodo informado na CAT e incompativel com a ART vinculada"],
        },
        "fraude": {
            "fraude_detectada": True,
            "nivel_risco": "alto",
            "indicadores": [
                "Inconsistencia critica de datas",
                "Descricao generica",
                "Divergencia entre CAT e ART",
            ],
        },
        "score_confiabilidade": {
            "score": 38,
            "nivel": "baixo",
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
        },
    }


@app.get("/history")
async def history() -> list[dict]:
    try:
        return get_all_analyses()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao buscar historico: {exc}",
        ) from exc


@app.get("/history/{analysis_id}")
async def history_by_id(analysis_id: int) -> dict:
    try:
        analysis = get_analysis_by_id(analysis_id)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao buscar analise: {exc}",
        ) from exc

    if analysis is None:
        raise HTTPException(status_code=404, detail="Analise nao encontrada.")

    return analysis


@app.post("/compare-cat-art")
async def compare_cat_art(payload: CATARTComparisonInput) -> dict:
    try:
        art_payload = payload.art_data.model_dump() if payload.art_data else None
        return compare_cat_with_art(payload.cat_data.model_dump(), art_payload)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao comparar CAT com ART: {exc}",
        ) from exc


@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)) -> dict:
    try:
        analysis_result = await process_file(file)
        persistence_payload = analysis_result.pop("_persistencia", None) or {}
        analysis_id = save_analysis(
            {
                "filename": analysis_result["filename"],
                "score": persistence_payload.get("score", analysis_result["resultado"]["score"]),
                "nivel": persistence_payload.get("nivel", analysis_result["resultado"]["nivel"]),
                "erros": persistence_payload.get("erros", []),
                "alertas": persistence_payload.get("alertas", []),
                "inconsistencias": persistence_payload.get("inconsistencias", []),
            }
        )
        analysis_result["analysis_id"] = analysis_id
        return analysis_result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao processar o documento: {exc}",
        ) from exc
