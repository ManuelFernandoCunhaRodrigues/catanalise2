from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
UPLOADS_DIR = Path(__file__).resolve().parent.parent / "uploads"


async def process_file(file: UploadFile) -> dict:
    """
    Processador minimo do hackathon.
    Le o PDF, valida o arquivo e devolve uma analise simulada pronta para demo.
    """
    original_filename = _normalize_filename(file.filename)

    if not original_filename.lower().endswith(".pdf"):
        raise ValueError("Arquivo invalido. Envie um PDF.")

    if file.content_type and file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise ValueError("Tipo de arquivo invalido. Envie um PDF.")

    file_bytes = await file.read()
    if not file_bytes:
        raise ValueError("Arquivo vazio. Envie um PDF com conteudo.")

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValueError("Arquivo acima do limite de 10MB.")

    if not file_bytes.startswith(b"%PDF-"):
        raise ValueError("Conteudo invalido. O arquivo enviado nao parece ser um PDF valido.")

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid4().hex}-{original_filename}"
    saved_path = UPLOADS_DIR / stored_filename
    saved_path.write_bytes(file_bytes)

    simulated_result = _simulate_analysis(file_bytes)
    persistence_payload = _simulate_persistence_data(file_bytes, simulated_result)

    return {
        "filename": original_filename,
        "status": "processado",
        "resultado": simulated_result,
        "_persistencia": persistence_payload,
    }


def _simulate_analysis(file_bytes: bytes) -> dict:
    """
    Simulacao simples para o MVP.
    Hoje devolve score com base no tamanho do arquivo, mas pode ser trocado por IA depois.
    """
    file_size = len(file_bytes)

    if file_size > 1_500_000:
        score = 90
    elif file_size > 300_000:
        score = 85
    else:
        score = 75

    if score >= 90:
        level = "alto"
    elif score >= 80:
        level = "medio"
    else:
        level = "baixo"

    return {
        "mensagem": "Documento recebido com sucesso",
        "score": score,
        "nivel": level,
    }


def _simulate_persistence_data(file_bytes: bytes, result: dict) -> dict:
    """
    Gera dados simples para historico auditavel sem complicar o MVP.
    """
    file_size = len(file_bytes)
    errors: list[str] = []
    alerts: list[str] = []
    inconsistencies: list[str] = []

    if file_size < 100_000:
        alerts.append("Arquivo pequeno para analise completa")

    if result["nivel"] == "baixo":
        inconsistencies.append("Score inicial abaixo do ideal para aprovacao automatica")

    return {
        "score": result["score"],
        "nivel": result["nivel"],
        "erros": errors,
        "alertas": alerts,
        "inconsistencias": inconsistencies,
    }


def _normalize_filename(filename: str | None) -> str:
    if not filename:
        raise ValueError("Arquivo invalido. Envie um PDF.")

    safe_name = Path(filename).name.strip()
    if not safe_name:
        raise ValueError("Nome de arquivo invalido.")

    return safe_name
