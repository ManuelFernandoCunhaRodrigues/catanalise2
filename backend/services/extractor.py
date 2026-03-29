from io import BytesIO
from typing import List

import fitz

try:
    import pytesseract
    from PIL import Image
except ImportError:  # pragma: no cover - dependência opcional
    pytesseract = None
    Image = None


def extract_text(pdf_file: bytes) -> str:
    """
    Lê o PDF página por página com PyMuPDF e faz OCR só se necessário.
    """
    try:
        document = fitz.open(stream=pdf_file, filetype="pdf")
    except Exception as exc:
        raise ValueError("Não foi possível abrir o PDF informado.") from exc

    page_texts: List[str] = []

    for page in document:
        page_text = page.get_text("text").strip()

        # Primeiro tentamos a camada nativa do PDF, que é mais rápida e confiável.
        if page_text:
            page_texts.append(page_text)
            continue

        # Se a página vier escaneada, tentamos OCR como fallback opcional.
        ocr_text = _extract_page_with_ocr(page)
        if ocr_text:
            page_texts.append(ocr_text)

    document.close()

    final_text = "\n\n".join(chunk for chunk in page_texts if chunk.strip()).strip()
    if not final_text:
        raise ValueError(
            "Nenhum texto foi encontrado no PDF. Verifique se o arquivo está legível ou se o OCR está configurado."
        )

    return final_text


def _extract_page_with_ocr(page: fitz.Page) -> str:
    """
    OCR leve para páginas escaneadas.
    Retorna string vazia quando OCR não está disponível.
    """
    if pytesseract is None or Image is None:
        return ""

    pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    image_bytes = pixmap.tobytes("png")
    image = Image.open(BytesIO(image_bytes))

    # `por` cobre bem CATs em português; `eng` ajuda em ruídos mistos.
    return pytesseract.image_to_string(image, lang="por+eng").strip()
