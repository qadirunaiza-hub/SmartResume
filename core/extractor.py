"""Extract raw text from uploaded PDF or DOCX files."""
from io import BytesIO


def extract_text(file_obj, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        return _from_pdf(file_obj)
    if ext in ("docx", "doc"):
        return _from_docx(file_obj)
    raise ValueError(f"Unsupported file type: .{ext}")


def _from_pdf(file_obj) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError("pypdf is required: pip install pypdf")

    reader = PdfReader(BytesIO(file_obj.read()) if not isinstance(file_obj, BytesIO) else file_obj)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def _from_docx(file_obj) -> str:
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx is required: pip install python-docx")

    doc = Document(BytesIO(file_obj.read()) if not isinstance(file_obj, BytesIO) else file_obj)
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs)
