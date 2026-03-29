from io import BytesIO
from typing import List

try:
    import fitz
except ImportError:  # pragma: no cover - dependency is required in runtime, optional in static review
    fitz = None

try:
    import pytesseract
    from PIL import Image
except ImportError:  # pragma: no cover - optional dependency
    pytesseract = None
    Image = None


def extract_text(pdf_file: bytes) -> str:
    """
    Reads the PDF page by page with PyMuPDF and falls back to OCR only when needed.
    """
    if fitz is None:
        raise ValueError("A extracao de texto nao esta disponivel porque a dependencia PyMuPDF nao foi instalada.")

    try:
        document = fitz.open(stream=pdf_file, filetype="pdf")
    except Exception as exc:
        raise ValueError("Nao foi possivel abrir o PDF informado.") from exc

    page_texts: List[str] = []

    try:
        for page in document:
            page_text = page.get_text("text").strip()
            if page_text:
                page_texts.append(page_text)
                continue

            ocr_text = _extract_page_with_ocr(page)
            if ocr_text:
                page_texts.append(ocr_text)
    finally:
        document.close()

    final_text = "\n\n".join(chunk for chunk in page_texts if chunk.strip()).strip()
    if not final_text:
        raise ValueError(
            "Nenhum texto foi encontrado no PDF. Verifique se o arquivo esta legivel ou se o OCR esta configurado."
        )

    return final_text


def _extract_page_with_ocr(page: "fitz.Page") -> str:
    """
    Lightweight OCR for scanned pages.
    Returns an empty string when OCR is unavailable.
    """
    if fitz is None or pytesseract is None or Image is None:
        return ""

    pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    image_bytes = pixmap.tobytes("png")
    image = Image.open(BytesIO(image_bytes))
    return pytesseract.image_to_string(image, lang="por+eng").strip()
