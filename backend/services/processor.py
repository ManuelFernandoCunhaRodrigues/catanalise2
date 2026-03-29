from pathlib import Path
from time import perf_counter
from uuid import uuid4

from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool

from services.art_integration import compare_cat_with_art
from services.extractor import extract_text
from services.feedback import generate_feedback
from services.fraud_detector import detect_fraud
from services.parser import extract_fields
from services.scorer import calculate_score
from services.validator import validate_fields


MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
UPLOADS_DIR = Path(__file__).resolve().parent.parent / "uploads"


async def process_file(file: UploadFile) -> dict:
    original_filename = _normalize_filename(file.filename)
    started_at = perf_counter()
    file_bytes = await _read_and_validate_pdf(file)

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid4().hex}-{original_filename}"
    saved_path = UPLOADS_DIR / stored_filename

    await run_in_threadpool(saved_path.write_bytes, file_bytes)
    result_payload = await run_in_threadpool(_run_analysis_pipeline, file_bytes, original_filename, saved_path.name)
    processing = {
        "modo": "threadpool",
        "arquivo_salvo": saved_path.name,
        "tempo_ms": round((perf_counter() - started_at) * 1000, 2),
    }
    result_payload["processamento"] = processing
    result_payload["_persistencia"]["analysis_payload"]["processamento"] = processing
    return result_payload


async def _read_and_validate_pdf(file: UploadFile) -> bytes:
    if file.content_type and file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise ValueError("Tipo de arquivo invalido. Envie um PDF.")

    file_bytes = await file.read()
    if not file_bytes:
        raise ValueError("Arquivo vazio. Envie um PDF com conteudo.")

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValueError("Arquivo acima do limite de 10MB.")

    if not file_bytes.startswith(b"%PDF-"):
        raise ValueError("Conteudo invalido. O arquivo enviado nao parece ser um PDF valido.")

    return file_bytes


def _run_analysis_pipeline(file_bytes: bytes, original_filename: str, stored_filename: str) -> dict:
    extracted_text = extract_text(file_bytes)
    extracted_fields = extract_fields(extracted_text)
    validation_result = validate_fields(extracted_fields)
    art_comparison = compare_cat_with_art(extracted_fields)
    merged_validation = _merge_validation_with_art(validation_result, art_comparison)
    fraud_result = detect_fraud(extracted_fields, art_comparison.get("art_encontrada"))
    reliability_score = calculate_score(merged_validation, fraud_result)
    intelligent_feedback = generate_feedback(
        {
            "erros": merged_validation["erros"],
            "alertas": merged_validation["alertas"],
            "inconsistencias": merged_validation["inconsistencias"],
            "fraudes": fraud_result["fraudes"],
        }
    )
    result_message = _build_result_message(merged_validation, fraud_result, reliability_score)

    analysis_payload = {
        "filename": original_filename,
        "status": "processado",
        "resultado": {
            "mensagem": result_message,
            "score": reliability_score["score"],
            "nivel": reliability_score["nivel"],
        },
        "texto_extraido": extracted_text,
        "dados_extraidos": extracted_fields,
        "validacao": merged_validation,
        "comparacao_art": art_comparison,
        "fraude": fraud_result,
        "score_confiabilidade": reliability_score,
        "feedback_inteligente": intelligent_feedback,
        "arquivo_salvo": stored_filename,
    }

    return {
        **analysis_payload,
        "_persistencia": {
            "score": reliability_score["score"],
            "nivel": reliability_score["nivel"],
            "erros": merged_validation["erros"],
            "alertas": merged_validation["alertas"],
            "inconsistencias": merged_validation["inconsistencias"],
            "analysis_payload": analysis_payload,
        },
    }


def _merge_validation_with_art(validation_result: dict, art_comparison: dict) -> dict:
    merged_alerts = _merge_lists(validation_result.get("alertas", []), art_comparison.get("alertas", []))
    merged_inconsistencies = _merge_lists(
        validation_result.get("inconsistencias", []),
        art_comparison.get("inconsistencias", []),
    )

    merged_validation = {
        **validation_result,
        "alertas": merged_alerts,
        "inconsistencias": merged_inconsistencies,
    }
    merged_validation["valid"] = len(merged_validation.get("erros", [])) == 0 and len(merged_inconsistencies) == 0
    return merged_validation


def _build_result_message(validation_result: dict, fraud_result: dict, reliability_score: dict) -> str:
    if fraud_result.get("fraude_detectada"):
        return "Documento processado com sinais relevantes de risco e necessidade de revisao humana."
    if validation_result.get("erros") or validation_result.get("inconsistencias"):
        return "Documento processado com pendencias que exigem correcao antes da aprovacao."
    if validation_result.get("alertas"):
        return "Documento processado com alertas. Revise os pontos sinalizados para aumentar a confiabilidade."
    return f"Documento processado com sucesso e score {reliability_score['score']} de confiabilidade."


def _normalize_filename(filename: str | None) -> str:
    if not filename:
        raise ValueError("Arquivo invalido. Envie um PDF.")

    safe_name = Path(filename).name.strip()
    safe_name = "".join(char for char in safe_name if char.isalnum() or char in {"-", "_", ".", " "}).strip()
    if not safe_name:
        raise ValueError("Nome de arquivo invalido.")

    if len(safe_name) > 120:
        stem = Path(safe_name).stem[:100].rstrip()
        suffix = Path(safe_name).suffix[:10]
        safe_name = f"{stem}{suffix}"

    if not safe_name.lower().endswith(".pdf"):
        raise ValueError("Arquivo invalido. Envie um PDF.")

    return safe_name


def _merge_lists(primary: list[str], secondary: list[str]) -> list[str]:
    seen = set()
    result: list[str] = []
    for item in list(primary) + list(secondary):
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
